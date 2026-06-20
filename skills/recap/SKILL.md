---
name: recap
description: Recap what you've worked on over a window — grouped by project, with what shipped — from your own OpenStory store. Use when the user asks "what did I work on this week", "what have I been doing", "recap my work", "what shipped lately", or wants a summary of recent activity across projects.
---

# recap

Summarize the user's recent work across projects. Pull the activity (via MCP),
then group + narrate. Report only what the tools return.

## Phase 1 — pull activity

Call the OpenStory MCP tools (named `mcp__openstory__*`; fetch schemas via
ToolSearch if they aren't loaded):

- `mcp__openstory__project_pulse` — per-project activity (sessions, events, last
  active) over a window. Pass `days` (default 7).
- `mcp__openstory__list_sessions` — recent sessions with project, label (the first
  prompt), branch, timestamps. Use the labels to infer *what shipped*.

If the user names a window ("this week", "last month"), pass it through.

If the tools aren't available, OpenStory isn't connected — say so, don't guess.

## Phase 2 — render

```
Week in review — <range>
<N> sessions · <M> projects · <K> events

Project           Sessions   Activity   What shipped
<project>         <n>        <events>   <1-line outcome inferred from labels>
...

Highlights: <2-3 concrete outcomes across the window>
```

Infer "what shipped" from session labels/topics — the skill has **no repo or git
access**, so never claim a commit you can't see. Order projects by activity. Keep
it tight; don't enumerate every session.

## When NOT to use this skill

- For one session's blow-by-blow, use a session-story flow.
- For just today as a standup, use `/openstory:standup`.
