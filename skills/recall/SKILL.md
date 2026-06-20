---
name: recall
description: Find the last time you did or solved something across all your coding sessions, and show how — the exact commands, the session, the date. Use when the user asks "how did I fix X", "did I ever set up Y", "where did I do Z", "find the session where…", or "have we hit this before". Searches the user's own OpenStory store.
---

# recall

Recover prior work from the user's OpenStory history. The skill argument is the
topic to recall, e.g. `/openstory:recall nats leaf federation`.

## Phase 1 — search

Call the OpenStory MCP search tools (named `mcp__openstory__*`; fetch schemas via
ToolSearch if needed):

- `mcp__openstory__search` — full-text across all events. Best for a specific
  error string, command, or phrase.
- `mcp__openstory__agent_search` — the same, grouped by session. Best for
  "which sessions touched X".

Take the most relevant, most recent hits. For a promising session, pull detail
with `mcp__openstory__session_synopsis` (goal, tools, errors) or
`mcp__openstory__tool_journey` (the ordered command sequence) to recover the
actual steps.

## Phase 2 — render

Answer in the recall shape:

```
<topic> — last seen <date> · session <id-prefix>
What happened: <one line>
How it was solved (the steps that worked):
  1. <command / edit>
  2. <command / edit>
Verified by: <the check that proved it worked>
Related: <other sessions that touched it>, oldest <date>
```

Quote real commands from the record verbatim. Sanitize obvious secrets to
placeholders (`<host>`, `<KEY>`, `<path>`). If nothing matches, say so plainly
and suggest a broader search term — never fabricate a memory.

## When NOT to use this skill

- To narrate a whole session start-to-finish, use a session-story flow instead.
- To list everything you've worked on lately, that's a future `/openstory:recap`.
