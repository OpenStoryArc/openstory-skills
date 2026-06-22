---
name: cost
description: Report what your AI coding sessions have cost — total spend, cache savings, and a tokens-per-day timeline — from your own OpenStory store. Use when the user asks "what did this cost", "my agent spend", "how much have I spent", "tokens per day", or anything about token usage or cost of coding sessions.
---

# cost

Report agent spend from the user's own OpenStory data. Two phases: pull the
numbers (deterministic, via MCP), then render + narrate. Never invent figures —
report only what the tools return.

## Phase 1 — pull the numbers

Call the OpenStory MCP tools (fetch their schemas with ToolSearch first if they
aren't loaded — they're named `mcp__openstory__*`):

- `mcp__openstory__token_usage` — totals: input / output / cache tokens + estimated cost.
- `mcp__openstory__daily_token_usage` — the per-day series for the timeline.

If the user names a window ("this week", "last 30 days"), pass it through (most
tools take a `days` argument). Default to the last 7 days.

**Scope to one session.** `token_usage` also takes `session_id`. If the user passes
a session id — or says "this session", "latest", or "current" — report just that
one session instead of a window:
- a specific id → `token_usage(session_id=<id>)`.
- "this session" / "latest" / "current" → call `mcp__openstory__list_sessions`,
  take the most recent `ongoing` session for this host/user, then pass its id.
- skip `daily_token_usage` in this mode (there's no multi-day timeline for one session).

If those tools aren't available, OpenStory isn't connected. Say so and tell the
user to start it (`openstory serve`) and connect the MCP — don't guess numbers.

## Phase 2 — render the report

Emit a compact spend report:

```
Agent spend — last <N> days
Total $<total> · <sessions> sessions · cache saved $<saved> (<pct>% off retail)

Tokens / day
<date>  $<cost>  <bar>        # ASCII bar; longest bar = the priciest day
...
```

Round money to whole dollars. Build the bar lengths proportional to each day's
cost. Close with one line of narration: the spendiest day, and the single biggest
call if the data exposes it.

**Single-session mode** (when scoped to one `session_id`): skip the daily timeline
and emit one tight block instead —

```
Agent spend — this session (<model>)
$<total> · <messages> messages · <total_tokens> tokens · cache saved $<saved> (<pct>% off)
<first_event date> → <last_event date> · <project>
```

## When NOT to use this skill

- For one specific session's detail, use `/openstory:recall` or a session synopsis.
- For team-wide spend across people, that's a future `/openstory:team` skill.
