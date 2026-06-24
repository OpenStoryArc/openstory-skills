// Build + validate the prompt -> skill -> tool -> endpoint -> code citation tree.
//
//   node scripts/build-citations.mjs          # regenerate CITATIONS.md
//   node scripts/build-citations.mjs --check   # validate only; fail if CITATIONS.md is stale
//
// Source of truth is citations.json. This script guarantees the tree never drifts
// from the actual skills on disk: every non-pending skill must have a SKILL.md,
// every SKILL.md must be registered, every tool a prompt/skill cites must exist
// in the tool registry, and the committed CITATIONS.md must match what this
// regenerates. Run in CI so a new skill (or a renamed tool) can't ship undocumented.

import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';

const ROOT = new URL('..', import.meta.url);
const p = (rel) => new URL(rel, ROOT);

const data = JSON.parse(readFileSync(p('citations.json'), 'utf8'));
const { tools, skills, prompts } = data;

// ---- validate ----------------------------------------------------------------
const errors = [];

// every skill on disk is registered, and vice-versa
const onDisk = readdirSync(p('skills'), { withFileTypes: true })
  .filter((d) => d.isDirectory())
  .map((d) => d.name)
  .filter((name) => existsSync(p(`skills/${name}/SKILL.md`)));

for (const name of onDisk) {
  if (!skills[name]) errors.push(`skill "${name}" has a SKILL.md but is not in citations.json`);
  else {
    // frontmatter name must match the directory
    const fm = readFileSync(p(`skills/${name}/SKILL.md`), 'utf8').match(/^name:\s*(.+)$/m);
    if (!fm || fm[1].trim() !== name) errors.push(`skills/${name}/SKILL.md frontmatter name != "${name}"`);
  }
}
for (const [name, skill] of Object.entries(skills)) {
  if (skill.status !== 'pending' && !onDisk.includes(name)) {
    errors.push(`skill "${name}" is ${skill.status} in citations.json but has no skills/${name}/SKILL.md`);
  }
  for (const t of skill.tools) {
    if (!tools[t]) errors.push(`skill "${name}" cites unknown tool "${t}"`);
  }
}

// every prompt resolves to a known skill + known tools
const ids = new Set();
for (const pr of prompts) {
  if (ids.has(pr.id)) errors.push(`duplicate prompt id "${pr.id}"`);
  ids.add(pr.id);
  if (!skills[pr.skill]) errors.push(`prompt ${pr.id} cites unknown skill "${pr.skill}"`);
  for (const t of pr.tools) {
    if (!tools[t]) errors.push(`prompt ${pr.id} cites unknown tool "${t}"`);
  }
}

if (errors.length) {
  console.error('Citation tree INVALID:\n' + errors.map((e) => `  - ${e}`).join('\n'));
  process.exit(1);
}

// ---- coverage ----------------------------------------------------------------
const built = (s) => skills[s] && skills[s].status !== 'pending';
const covered = prompts.filter((pr) => built(pr.skill)).length;
const byStatus = (st) => prompts.filter((pr) => skills[pr.skill]?.status === st).length;

// ---- render CITATIONS.md -----------------------------------------------------
const sections = [...new Set(prompts.map((pr) => pr.section))];
const sectionNum = (pr) => pr.id.split('.')[0];

let md = `# Citation tree — prompts → skills → tools → endpoints → code

> **Generated** from \`citations.json\` by \`scripts/build-citations.mjs\`. Do not edit by
> hand — edit the JSON and run \`node scripts/build-citations.mjs\`. CI runs
> \`--check\` so this can never drift from the skills on disk. Citations are
> grounded against OpenStory \`master\`: \`rs/mcp/src/http_store.rs\` (the MCP→REST
> endpoint map) and live API probes.

**Coverage:** ${covered}/${prompts.length} common prompts are backed by a built skill — ${byStatus('live')} live · ${byStatus('heuristic')} heuristic · ${byStatus('pending')} pending.

This is the trace an agent can follow to trust a skill: a prompt → the skill that
serves it → the MCP tools it calls → the REST endpoint each tool wraps → the
source line that defines it.

## Prompt → skill → tools

`;

for (const sec of sections) {
  const num = prompts.find((pr) => pr.section === sec).id.split('.')[0];
  md += `### ${num} · ${sec}\n\n`;
  for (const pr of prompts.filter((x) => x.section === sec)) {
    const sk = skills[pr.skill];
    const slash = sk.status === 'pending' ? `\`${pr.skill}\` _(pending — not built)_` : `**\`/openstory:${pr.skill}\`** _(${sk.status})_`;
    md += `- **[${pr.id}]** "${pr.text}"\n  → ${slash}\n`;
    for (const t of pr.tools) {
      const tool = tools[t];
      md += `  - \`${t}\` — \`${tool.mcp}\` → \`${tool.rest}\` — _${tool.source}_${tool.status === 'pending' ? ' **(pending)**' : ''}\n`;
    }
    md += `\n`;
  }
}

md += `## Data sources (every tool the skills cite)\n\n`;
md += `| Tool | MCP | REST endpoint | Source | Status |\n|---|---|---|---|---|\n`;
for (const [name, t] of Object.entries(tools)) {
  md += `| \`${name}\` | \`${t.mcp}\` | \`${t.rest}\` | ${t.source} | ${t.status} |\n`;
}

md += `\n## Skills\n\n| Skill | Question | Status | Tools |\n|---|---|---|---|\n`;
for (const [name, s] of Object.entries(skills)) {
  const slash = s.status === 'pending' ? name : `/openstory:${name}`;
  md += `| \`${slash}\` | ${s.question} | ${s.status} | ${s.tools.map((t) => `\`${t}\``).join(', ')} |\n`;
}

const pendingPrompts = prompts.filter((pr) => !built(pr.skill));
const pendingTools = Object.entries(tools).filter(([, t]) => t.status === 'pending');
md += `\n## Gaps\n\n`;
md += pendingPrompts.length
  ? pendingPrompts.map((pr) => `- **[${pr.id}]** needs \`${pr.skill}\` (not yet built)`).join('\n') + '\n'
  : '- None — every prompt resolves to a built skill.\n';
if (pendingTools.length) {
  md += `\n**Pending server tools** (skills degrade gracefully until these land):\n`;
  md += pendingTools.map(([n, t]) => `- \`${n}\` — ${t.source}`).join('\n') + '\n';
}

md += `\n---\n_Evidence tags: **live** = queried against your store · **heuristic** = composed from existing tools, sharper when a dedicated tool lands · **illustrative** = representative shape._\n`;

// ---- write or check ----------------------------------------------------------
const target = p('CITATIONS.md');
if (process.argv.includes('--check')) {
  const current = existsSync(target) ? readFileSync(target, 'utf8') : '';
  if (current !== md) {
    console.error('CITATIONS.md is stale — run `node scripts/build-citations.mjs` and commit.');
    process.exit(1);
  }
  console.log(`Citation tree valid + in sync (${covered}/${prompts.length} prompts covered).`);
} else {
  writeFileSync(target, md);
  console.log(`Wrote CITATIONS.md — ${covered}/${prompts.length} prompts covered, ${Object.keys(tools).length} tools, ${Object.keys(skills).length} skills.`);
}
