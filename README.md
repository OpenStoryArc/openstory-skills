# OpenStory skills

Ask your own AI coding-agent history. A Claude Code **plugin** that turns
OpenStory into slash commands — `/openstory:cost`, `/openstory:recall`, and more —
backed by your own session store.

> A mirror, not a leash. The skills only read your OpenStory data; they never
> touch your code or your repos.

## Quickstart

Zero to your first report in three steps. Needs [Claude Code](https://claude.com/claude-code)
and [Homebrew](https://brew.sh).

**1. Install OpenStory's engine** — the store + the `open-story-mcp` binary the skills read:

```bash
brew install openstoryarc/openstory/openstory openstoryarc/openstory/openstory-mcp
brew services run openstoryarc/openstory/openstory   # starts your store → http://localhost:3002
```

**2. Install these skills** — a Claude Code **plugin** (not brew):

```bash
/plugin marketplace add openstoryarc/openstory-skills
/plugin install openstory@openstory-skills
/reload-plugins
```

**3. Ask your history anything:**

```bash
/openstory:cost            # what your agent sessions have cost
/openstory:recap           # what you shipped this week
/openstory:recall nats     # the last time you touched <topic>, with the commands
```

That's it. The skills read **your own** OpenStory store via `open-story-mcp` (REST,
`localhost:3002` by default — see [Prerequisite](#prerequisite) for a remote/secured
instance). Full skill list is below; how each prompt maps prompt → skill → tool →
endpoint → code is traced in [`CITATIONS.md`](./CITATIONS.md).

## Prerequisite

OpenStory running and reachable. The skills talk to the OpenStory **MCP server**,
which the plugin declares for you (`.mcp.json`). It reads from your OpenStory REST
API, defaulting to `http://localhost:3002` (built into the binary).

- Install + run OpenStory (see https://openstory.work).
- Make sure `open-story-mcp` is on your `PATH` (Homebrew install provides it).

**Pointing at a remote or token-secured instance.** Two ways:

1. **Export it in your shell** (simplest — no file edits, survives plugin
   updates). Stdio MCP servers inherit your shell environment, so set the vars
   before launching `claude`:

   ```bash
   export OPENSTORY_API_URL=https://your-instance
   export OPENSTORY_API_TOKEN=your-token
   ```

2. **Add an `env` block to `.mcp.json`** with a **literal** value:

   ```json
   "env": {
     "OPENSTORY_API_URL": "https://your-instance",
     "OPENSTORY_API_TOKEN": "your-token"
   }
   ```

   Use a literal — don't rely on `${VAR:-default}` shell-style expansion here.
   Depending on your Claude Code version it may be passed verbatim, which makes a
   bogus URL and every query silently returns empty. (The plugin-vendored
   `.mcp.json` can also be overwritten on plugin update, so the shell export
   above is the more durable option.)

## Install

```bash
/plugin marketplace add openstoryarc/openstory-skills   # this repo
/plugin install openstory@openstory-skills
/reload-plugins
```

Then:

```bash
/openstory:cost                      # what your sessions cost — total + tokens/day
/openstory:recall nats leaf          # the last time you did X, with the commands
```

Plugin skills are namespaced by the plugin, so it's `/openstory:<skill>` (this is
what keeps them from colliding with anyone else's skills).

## Skills

| Skill | Question it answers | Data |
|-------|---------------------|------|
| `/openstory:cost` | "What did my agent sessions cost?" | `token_usage`, `daily_token_usage` |
| `/openstory:recall <topic>` | "How did I solve / set up X last time?" | `search`, `session_synopsis`, `tool_journey` |
| `/openstory:recap` | "What did I work on this week?" | `project_pulse`, `list_sessions` |
| `/openstory:standup` | "Write my standup for today." | `list_sessions`, `session_synopsis` |
| `/openstory:coach` | "How am I doing / where do I get stuck?" | `session_patterns`, `session_errors`, `productivity`* |
| `/openstory:scan` | "Anything sensitive before I share?" | `search`* (redacted summary only) |
| `/openstory:exposure` | "What would a third party infer about me?" | `productivity`, `daily_token_usage`, `project_pulse` ‡ |
| `/openstory:time` | "Where does my time actually go?" | `productivity`, `list_sessions` |
| `/openstory:tools` | "Which tools/commands do I rely on most?" | `tool_journey`, `list_sessions`* |
| `/openstory:team` | "Who on my team is working on what?" | `list_sessions`, `session_synopsis` |
| `/openstory:arc` | "Tell the story of `<project/topic>`." | `search`, `session_synopsis` |
| `/openstory:prime` | "Pick up where the last session left off." | `list_sessions`, `session_synopsis`, `session_transcript` |
| `/openstory:watch` | "Watch a branch's work as it streams." | `subscribe_session`, `list_sessions` |
| `/openstory:reel <topic>` | "Turn X into a saved, replayable reel." | `agent_search`, `session_story`, `save_reel`, `list_reels`, `play_reel` |

Each is a thin SKILL.md over OpenStory MCP tools — nothing to install beyond the
plugin, portable to any OpenStory user.

`scan` and `exposure` are the two halves of "is it safe to share this": `scan`
hunts **secrets** (values that must never leave), `exposure` hunts **inferences**
(what someone derives from data containing no secrets at all — your sleep window,
the week your house was empty, your burn rate). A history can pass `scan` clean
and still give away all of that.

\* Some skills run today on existing tools (heuristic) and get sharper when a
dedicated server-side tool lands — `coach`/`scan` want `prompt_scorecard` +
`sensitivity_scan`; `tools` wants `tool_histogram` (tool + command frequency).
Each prefers its dedicated tool when present and falls back gracefully.

‡ `exposure` is the one skill that ships a script — `skills/exposure/scripts/exposure_audit.py`,
stdlib-only Python 3, bundled with the plugin (no install step). The MCP tools
above give the metadata sections; the script adds the deterministic inference
(sleep window across midnight, absence gaps) and the verbatim-preview section,
which it writes to a local git-ignored file rather than into your transcript. It
audits **your own** store only — there is no flag to point it at another person,
by design. Run `python3 skills/exposure/scripts/exposure_audit.py --test` for its
self-check.

## Traceability — the citation tree

Every common prompt is traced to the skill that serves it, the MCP tools it calls,
the REST endpoint each tool wraps, and the source line that defines it — see
**[`CITATIONS.md`](./CITATIONS.md)** (human-readable) and **[`citations.json`](./citations.json)**
(machine-readable, for agents). The tree is generated and CI-validated:

```bash
node scripts/build-citations.mjs          # regenerate CITATIONS.md from citations.json
node scripts/build-citations.mjs --check   # CI: fail if a skill is undocumented or the tree is stale
```

So a new skill can't ship without a citation, and a citation can't point at a tool
that doesn't exist.

## Local development

Test the plugin before publishing — a local path works as a marketplace:

```bash
/plugin marketplace add ./openstory-skills      # or the absolute path
/plugin install openstory@openstory-skills
/reload-plugins
```

If you already have an OpenStory MCP named `openstory` wired in another project
(e.g. the OpenStory repo's own `.mcp.json`), test this plugin from a directory
*outside* that repo to avoid two servers claiming the same name.

## Tests

Layered — see **[`TESTING.md`](./TESTING.md)** for the full methodology (incl. the
agent rubric for behavioral testing).

```bash
# Layer 0 — static contract (runs in CI, zero deps, Node 18+)
node --test test/mcp-contract.test.mjs     # .mcp.json: no ${...}, only env vars the binary reads
node scripts/build-citations.mjs --check    # citation tree consistent with skills on disk

# Layers 1 & 2 — data-path probe (needs a running OpenStory)
node scripts/probe-skills.mjs               # every skill's cited tools are exposed AND return real data

# Bundled skill script — self-check (no network)
python3 skills/exposure/scripts/exposure_audit.py --test
```

Layer 0 catches wiring/metadata regressions (it would have caught the silent-zeros
`${OPENSTORY_API_URL:-…}` manifest). The probe catches the rest — a skill citing a
tool the server doesn't expose, or an endpoint that 404s / returns empty — by
driving every skill's data path from `citations.json` against a live store.

## Layout

```
.claude-plugin/
  plugin.json        # plugin manifest (identity + version)
  marketplace.json   # makes this repo installable as a marketplace
skills/
  cost/SKILL.md  recall/SKILL.md  recap/SKILL.md
  standup/SKILL.md  coach/SKILL.md  scan/SKILL.md
  exposure/SKILL.md + scripts/exposure_audit.py   # the one skill with a script
.mcp.json            # declares the OpenStory MCP server
test/                # node --test contract checks over .mcp.json
.github/workflows/   # CI: runs the contract test on every PR
```

## License

Apache-2.0.
