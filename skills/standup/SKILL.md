---
name: standup
description: Turn today's coding sessions into a standup update — what you did, what's blocked, what's next — from your own OpenStory store. Use when the user asks "write my standup", "what did I do today", "standup", or "summarize today's work".
---

# standup

Compose a standup from the day's sessions. Pull → synthesize. Ground every line
in the sessions; don't pad.

## Phase 1 — pull today's sessions

Call the OpenStory MCP tools (named `mcp__openstory__*`):

- `mcp__openstory__list_sessions` with a 1-day window — today's sessions (label,
  project, branch, event counts).
- For the substantive ones, `mcp__openstory__session_synopsis` (goal, tools,
  errors) and/or `mcp__openstory__session_story` to recover what happened and what
  was left open.

## Phase 2 — render

```
Standup — <date>
Did:
  • <completed work, grounded in the sessions>
Blocked:
  • <unresolved errors / open threads, or "nothing blocking">
Next:
  • <queued or explicit next steps surfaced in the sessions>

<N> sessions · <M> turns · top tools: <short histogram>
```

Infer **Blocked** from unresolved errors or trailing unfinished work; infer
**Next** from explicit TODOs or where a session left off. If a field is genuinely
empty, say so rather than inventing filler.

## When NOT to use this skill

- For a multi-day summary, use `/openstory:recap`.
