# OpenStory skills

Ask your own AI coding-agent history. A Claude Code **plugin** that turns
OpenStory into slash commands — `/openstory:cost`, `/openstory:recall`, and more —
backed by your own session store.

> A mirror, not a leash. The skills only read your OpenStory data; they never
> touch your code or your repos.

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
| `/openstory:time` | "Where does my time actually go?" | `productivity`, `list_sessions` |
| `/openstory:tools` | "Which tools/commands do I rely on most?" | `tool_journey`, `list_sessions`* |
| `/openstory:team` | "Who on my team is working on what?" | `list_sessions`, `session_synopsis` |
| `/openstory:arc` | "Tell the story of `<project/topic>`." | `search`, `session_synopsis` |
| `/openstory:prime` | "Pick up where the last session left off." | `list_sessions`, `session_synopsis`, `session_transcript` |

Each is a thin SKILL.md over OpenStory MCP tools — no scripts to install, portable
to any OpenStory user.

\* Some skills run today on existing tools (heuristic) and get sharper when a
dedicated server-side tool lands — `coach`/`scan` want `prompt_scorecard` +
`sensitivity_scan`; `tools` wants `tool_histogram` (tool + command frequency).
Each prefers its dedicated tool when present and falls back gracefully.

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

```bash
node --test test/mcp-contract.test.mjs    # zero deps; Node 18+
```

A static contract test over `.mcp.json`: no env value may use `${...}`
shell-style expansion (Claude Code may pass it verbatim), and every env key must
be one `open-story-mcp` actually reads. This is the test that would have caught
the silent-zeros regression where the manifest shipped
`"${OPENSTORY_API_URL:-http://localhost:3002}"`. Runs in CI on every PR
(`.github/workflows/test.yml`).

## Layout

```
.claude-plugin/
  plugin.json        # plugin manifest (identity + version)
  marketplace.json   # makes this repo installable as a marketplace
skills/
  cost/SKILL.md  recall/SKILL.md  recap/SKILL.md
  standup/SKILL.md  coach/SKILL.md  scan/SKILL.md
.mcp.json            # declares the OpenStory MCP server
test/                # node --test contract checks over .mcp.json
.github/workflows/   # CI: runs the contract test on every PR
```

## License

Apache-2.0.
