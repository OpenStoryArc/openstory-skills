# OpenStory skills

Ask your own AI coding-agent history. A Claude Code **plugin** that turns
OpenStory into slash commands — `/openstory:cost`, `/openstory:recall`, and more —
backed by your own session store.

> A mirror, not a leash. The skills only read your OpenStory data; they never
> touch your code or your repos.

## Prerequisite

OpenStory running and reachable. The skills talk to the OpenStory **MCP server**,
which the plugin declares for you (`.mcp.json`). It reads from your OpenStory REST
API — default `http://localhost:3002`, override with `OPENSTORY_API_URL`.

- Install + run OpenStory (see https://openstory.work).
- Make sure `open-story-mcp` is on your `PATH` (Homebrew install provides it).

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
| `/openstory:cost` | "What did my agent sessions cost?" | `mcp__openstory__token_usage`, `daily_token_usage` |
| `/openstory:recall <topic>` | "How did I solve / set up X last time?" | `mcp__openstory__search`, `session_synopsis`, `tool_journey` |

More on the way: `recap`, `standup`, `coach`, `scan`. Each is a thin SKILL.md over
OpenStory MCP tools — no scripts to install, portable to any OpenStory user.

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

## Layout

```
.claude-plugin/
  plugin.json        # plugin manifest (identity + version)
  marketplace.json   # makes this repo installable as a marketplace
skills/
  cost/SKILL.md
  recall/SKILL.md
.mcp.json            # declares the OpenStory MCP server
```

## License

Apache-2.0.
