---
name: tools
description: Show which tools and commands you rely on most across coding sessions — tool histogram, top shell commands, and Read:Write ratio. Frequency, not duration (that's time) or cost (that's cost). Use when the user asks "what tools do I use most", "my top commands", "what do I reach for", "how often do I edit vs read", or "tool breakdown".
---

# tools

What you *reach for* — the frequency of tools and commands across your sessions.
Counts, not time (`/openstory:time`) or money (`/openstory:cost`). Two phases:
pull via MCP, then render. Report only what the tools return.

## Phase 1 — pull the numbers

Prefer a dedicated histogram tool if it exists:

- `mcp__openstory__tool_histogram` — aggregate tool + command counts over a
  window. **May not exist yet** (it would wrap `/api/insights/tool-evolution`
  plus bash-command parsing). If present, use it.

Fallback (existing tools, `mcp__openstory__*`):

- `mcp__openstory__list_sessions` — pick the heaviest recent sessions.
- `mcp__openstory__tool_journey` on those — per-session tool sequence; aggregate
  the counts across them into a tool histogram. Tool-level only — command-level
  (grep/git/ssh) needs the dedicated tool above.

Default to the last 7 days.

If those tools aren't available, OpenStory isn't connected — say so, don't guess.

## Phase 2 — render

```
What you reach for — last <N> days
Read:Write <ratio> · most-used: <tool> (<pct>%)

Tools
<tool>   <count>   <bar>
...

Top commands            # only with tool_histogram (bash parsing)
<cmd> · <count>   ...
```

Close with one line: your single most-used tool, and the Read:Write balance
(read-heavy = careful; write-heavy = fast iteration).

## Honest limit

Without `tool_histogram`, this is **tool-level only** (Bash/Read/Edit), composed
from a sample of heavy sessions — command-level frequency needs the server tool.
Say which mode you ran in.

## When NOT to use this skill

- For *time* spent (duration), use `/openstory:time`.
- For token/dollar cost, use `/openstory:cost`.
