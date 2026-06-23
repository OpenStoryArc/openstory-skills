---
name: prime
description: Prime yourself with prior OpenStory context before starting — pick up exactly where the last session on this project left off: what was done, what's open, the tools used. Use at the START of work, or when the user says "where did we leave off", "resume", "pick up where I left off", "catch up on this project", or "what was I doing here".
---

# prime

The highest-leverage habit: lean on the record instead of guessing. Pull the last
session's context so you resume instead of restart. Two phases.

## Phase 1 — pull

OpenStory MCP tools (`mcp__openstory__*`):

- `mcp__openstory__list_sessions` — the most recent session(s) for this project /
  host (sort by `last_event`).
- `mcp__openstory__session_synopsis` — what that session did + open threads.
- `mcp__openstory__session_transcript` — the trailing/unfinished messages, to see
  exactly where it stopped (the "what's mid-flight" tail).

Scope to the current project by `project_name` when known.

If those tools aren't available, OpenStory isn't connected — say so, don't guess.

## Phase 2 — render

```
Resuming <project> — last session <date> · <events> events
Did:    <2–4 bullets of what the last session accomplished>
Tools:  <top tools, e.g. Bash×36 · Edit×23>
Open:   <unfinished threads>

→ Resume here: <the concrete next step the last session was mid-way through>
```

Keep it tight — the goal is a running start, not a full history. Close with the
single most actionable "resume here" line.

## When NOT to use this skill

- To search across *all* history for a topic, use `/openstory:recall`.
- For a multi-project week summary, use `/openstory:recap`.
- Pairs well as a CLAUDE.md routing rule ("before starting, run /openstory:prime").
