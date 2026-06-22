---
name: coach
description: Coach yourself — honest feedback on how you work with coding agents: prompt quality, recurring failure patterns, and what your work has been pointing at. From your own OpenStory store. Use when the user asks "how am I doing", "feedback on my prompting", "where do I get stuck", "what am I focused on lately", or "coach me".
---

# coach

Hold up the mirror: what does the record say about how the user works. Pull
signals, then assess honestly — anchored in data, not flattery.

## Phase 1 — pull signals

Prefer a dedicated scorecard tool if it exists:

- `mcp__openstory__prompt_scorecard` — if available, use it (prompt-length
  distribution, one-shot rate, turns/session, edit-thrash). **This tool may not
  exist yet** — if not, compose the signals below.

Fallback (existing tools, all `mcp__openstory__*`):

- `mcp__openstory__list_sessions` — volume + session labels (for themes).
- `mcp__openstory__session_patterns` / `mcp__openstory__session_errors` — failure
  signals (loops, errors, recovery) on recent sessions.
- `mcp__openstory__productivity` — when the user works.
- `mcp__openstory__tool_journey` on a few heavy sessions — repeated identical tool
  calls are an edit-thrash signal.

## Phase 2 — render

```
How you work — <window>
Strengths:
  • <a strength tied to a measurable signal>
Watch-outs:
  • <a recurring failure pattern + a concrete fix>
Direction:
  • <themes your recent work clusters into, from session labels>
```

Anchor every claim to a signal you actually pulled, and name it ("error rate
N%", "M sessions on <theme>"). If you could only estimate (no scorecard tool),
label it an estimate. Be direct and useful, not flattering.

> Note: the deepest metrics (precise prompt-length distribution, edit-thrash
> rate) want the server-side `prompt_scorecard` MCP tool. Until it ships, this
> skill gives a solid heuristic read from patterns, errors, and labels.
