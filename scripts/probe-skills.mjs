// Citation-driven skill data-path probe.
//
//   node scripts/probe-skills.mjs            # probe every skill's tools against a live OpenStory
//   OPENSTORY_API_URL=https://host node scripts/probe-skills.mjs
//
// The static tests (test/mcp-contract.test.mjs, build-citations.mjs --check) prove
// the WIRING and METADATA are consistent. They prove nothing about whether a skill
// actually works against data. This probe closes that gap — it would have caught
// both the silent-zeros .mcp.json bug AND a citation pointing at a 404 endpoint.
//
// Using citations.json as the spec, for every skill it:
//   Layer 1 (availability) — spawns `open-story-mcp`, tools/list, asserts every
//            live tool the skill cites is actually exposed by the server.
//   Layer 2 (liveness)     — hits each cited tool's REST endpoint against a real
//            OpenStory and asserts HTTP 200 + a non-empty, non-trivial body.
// A skill PASSES when all its live tools pass both layers. `pending` tools are
// skipped (reported, not failed). Exit non-zero on any failure — so an agent (or
// CI with a seeded store) can run it as a gate.
//
// Requires: a running OpenStory (OPENSTORY_API_URL, default http://localhost:3002)
// and, for Layer 1, `open-story-mcp` on PATH (Layer 1 is skipped with a note if absent).

import { readFileSync } from 'node:fs';
import { spawn } from 'node:child_process';

const API = (process.env.OPENSTORY_API_URL || 'http://localhost:3002').replace(/\/$/, '');
const { tools, skills } = JSON.parse(readFileSync(new URL('../citations.json', import.meta.url), 'utf8'));

// ---- Layer 1: which tools does the MCP server actually expose? ----------------
function listMcpTools() {
  return new Promise((resolve) => {
    let out = '';
    let done = false;
    let child;
    const finish = () => {
      if (done) return;
      done = true;
      try { child?.kill(); } catch {}
      const names = new Set();
      for (const line of out.split('\n')) {
        try {
          const m = JSON.parse(line);
          if (m.id === 2 && m.result?.tools) for (const t of m.result.tools) names.add(t.name);
        } catch {}
      }
      resolve(names.size ? names : null);
    };
    try {
      child = spawn('open-story-mcp', { stdio: ['pipe', 'pipe', 'ignore'] });
    } catch {
      return resolve(null);
    }
    child.on('error', () => { if (!done) { done = true; resolve(null); } }); // not on PATH
    // Resolve the instant the tools/list (id:2) reply lands — open-story-mcp is a
    // server and keeps stdout open, so waiting for 'close' would hang ~15s.
    child.stdout.on('data', (d) => { out += d; if (out.includes('"id":2')) finish(); });
    child.on('close', finish);
    child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'probe', version: '0' } } }) + '\n');
    child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} }) + '\n');
    child.stdin.end();
    setTimeout(finish, 12000); // fallback only
  });
}

// ---- Layer 2: does the tool's REST endpoint return real data? -----------------
async function probeRest(restSpec, sample) {
  const m = restSpec.match(/GET (\/api\/[^\s?]+)/);
  if (!m) return { ok: null, note: 'non-REST (streaming)' };
  const path = m[1].replace('{id}', sample.id);
  // Per-session endpoints can be *legitimately* empty (a session with no errors,
  // no patterns yet) — so 200 alone proves the data path. Aggregate endpoints
  // (sessions list, insights, search) must actually return data.
  const perSession = /\/sessions\/[^/]+\//.test(path);
  let url = API + path;
  if (path.includes('/search')) url += '?q=test&limit=5';
  else if (path.includes('/agent/project-context') || path.includes('/agent/recent-files')) url += `?project=${encodeURIComponent(sample.project || '')}`;
  else if (path.includes('/insights/')) url += '?days=7';
  // one retry — these endpoints can transiently time out under load
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(12000) });
      const text = await r.text();
      if (r.status !== 200) return { ok: false, status: r.status, size: text.length };
      if (perSession) return { ok: true, status: 200, size: text.length };
      const nonTrivial = text.length > 2 && !['[]', 'null', '{}', '{"sessions":[]}'].includes(text.trim());
      return { ok: nonTrivial, status: 200, size: text.length, note: nonTrivial ? undefined : 'empty' };
    } catch (e) {
      if (attempt === 1) return { ok: false, note: String(e.message || e) };
    }
  }
}

// ---- run ----------------------------------------------------------------------
const exposed = await listMcpTools();
console.log(`Skill data-path probe — API ${API}`);
console.log(exposed ? `Layer 1: open-story-mcp exposes ${exposed.size} tools` : `Layer 1: SKIPPED (open-story-mcp not on PATH — availability check unavailable)`);

// a sample session id + project for the {id}/{project} endpoints
let sample = { id: '', project: '' };
try {
  const s = (await (await fetch(`${API}/api/sessions`, { signal: AbortSignal.timeout(10000) })).json()).sessions?.[0];
  if (s) sample = { id: s.session_id, project: s.project_name };
} catch {}
if (!sample.id) { console.error('Could not fetch a sample session from the API — is OpenStory running?'); process.exit(2); }

// Probe each unique live tool ONCE, in parallel — skills share tools heavily
// (list_sessions appears in most), so per-skill sequential probing is both slow
// and redundant.
const liveTools = [...new Set(
  Object.values(skills).filter((s) => s.status !== 'pending').flatMap((s) => s.tools),
)].filter((t) => tools[t] && tools[t].status !== 'pending');

const result = {};
await Promise.all(liveTools.map(async (t) => {
  const tool = tools[t];
  const bare = tool.mcp.replace(/^mcp__openstory__/, '');
  result[t] = { avail: exposed ? exposed.has(bare) : null, rest: await probeRest(tool.rest, sample) };
}));

let failures = 0;
const lines = [];
for (const [name, skill] of Object.entries(skills)) {
  if (skill.status === 'pending') { lines.push(`  ~ ${name.padEnd(8)} pending (not built) — skipped`); continue; }
  const parts = [];
  let skillOk = true;
  for (const t of skill.tools) {
    const tool = tools[t];
    if (!tool || tool.status === 'pending') { parts.push(`${t}:pending`); continue; }
    const { avail, rest } = result[t];
    const availMark = avail === false ? '✗avail' : '';
    const dataMark = rest.ok === false ? `✗data(${rest.status || rest.note})` : rest.ok === null ? 'stream' : `${rest.status}`;
    if (avail === false || rest.ok === false) skillOk = false;
    parts.push(`${t}(${[availMark, dataMark].filter(Boolean).join(',')})`);
  }
  if (!skillOk) failures++;
  lines.push(`  ${skillOk ? '✓' : '✗'} ${name.padEnd(8)} ${parts.join(' ')}`);
}

console.log('\nPer-skill data path:');
console.log(lines.join('\n'));
console.log(`\n${failures ? `✗ ${failures} skill(s) have a broken data path` : '✓ every built skill has a working data path'}`);
process.exit(failures ? 1 : 0);
