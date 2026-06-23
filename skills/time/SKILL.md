---
name: time
description: Show where your time actually goes across coding sessions — by project, by hour, and how focused vs scattered your work is. Distinct from cost (money) and tools (frequency). Use when the user asks "where does my time go", "how much time on X", "when am I most productive", "am I focused or scattered", or "time breakdown".
---

# time

Where your *attention* goes — wall-clock and rhythm, not token cost (that's
`/openstory:cost`) and not call counts (that's `/openstory:tools`). Two phases:
pull the numbers via MCP, then render + narrate. Report only what the tools return.

## Phase 1 — pull the numbers

OpenStory MCP tools (`mcp__openstory__*` — fetch schemas with ToolSearch if not loaded):

- `mcp__openstory__productivity` — events per hour of day (your working rhythm).
- `mcp__openstory__list_sessions` — each session's `first_event` / `last_event`
  (span = wall-clock time) and `project_name` (for time-by-project).

Default to the last 7 days; pass a window through if the user names one.

Time-by-project = sum each session's (`last_event` − `first_event`), grouped by
`project_name`.

If those tools aren't available, OpenStory isn't connected — say so, don't guess.

## Phase 2 — render

```
Where your time goes — last <N> days
<total active span> across <sessions> sessions

By project
<project>   <hours>h   <bar>
...

When you work (events/hour, UTC)
<hour>  <bar>
...
```

Close with one line: your peak hour and your single heaviest project.

## Honest limit

v1 measures **wall-clock span** (first→last event) and **rhythm** (events/hour) —
a good proxy, but it counts idle time inside a session. True *active minutes*
(subtracting idle gaps) wants a server-side `active_time` analytic; this skill
will prefer it the moment it exists.

## When NOT to use this skill

- For money/token spend, use `/openstory:cost`.
- For *which* tools/commands you use (counts, not duration), use `/openstory:tools`.
