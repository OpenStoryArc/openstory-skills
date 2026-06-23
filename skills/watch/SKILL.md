---
name: watch
description: Watch the work happening on a branch or project through OpenStory and summarize it live as it streams — a real-time feed of tools and edits plus a rolling summary of what the work is converging on. Use when the user says "watch this branch", "what's happening on <branch> right now", "stream the work", "follow along live", "show me activity as it happens", or "tail the agent on <project>".
---

# watch

Real-time co-presence with a running agent: open a live stream and narrate the
work as it arrives. The skill argument is the branch or project to watch, e.g.
`/openstory:watch feat/cover-common-prompts`. Two phases: subscribe via MCP,
then render a live feed.

## Phase 1 — subscribe

OpenStory MCP tools (`mcp__openstory__*`):

- `mcp__openstory__list_sessions` — find the session(s) to watch. Every session
  carries `project_name`, `host`, `user`, `status`, `last_event`. Match the
  branch/project the user named, then pick the live one (`status` ongoing and
  `last_event` within minutes). If several match, take the most recent.
- `mcp__openstory__subscribe_session` — open the **live event stream** for that
  session. Events arrive as they happen (tool uses, edits, messages); the skill
  summarizes each as it lands. Optionally pair with
  `mcp__openstory__subscribe_tokens` for a live token/cost ticker.

These are streaming tools — they deliver events continuously, not a one-shot
answer. The skill runs as a live tail: it keeps reporting until the user stops or
the session goes idle.

**Want a point-in-time snapshot instead of a live tail?** Fall back to the most
recent state: `mcp__openstory__session_activity` (recent activity for the session)
or `mcp__openstory__tool_journey` (the ordered tool sequence so far). Use these
when the user wants "what's it done so far" rather than "show me as it happens".

If those tools aren't available, OpenStory isn't connected — say so, don't guess.

## Phase 2 — render

A live feed (timestamp · tool · one-line) under a rolling summary, like a ticker:

```
Watching <project>/<branch> — session <id-prefix> · live since <time>

12:04:31  Edit       skills/watch/SKILL.md — added Phase 1
12:04:48  Bash       node scripts/build-citations.mjs
12:05:02  Read       citations.json
12:05:19  Edit       README.md — Skills table row

Rolling summary: building the watch skill — SKILL.md drafted, citation tree
being regenerated, README updated. Converging on: a green 21/21 citation run.
```

Each event is one terse line: time · tool · the one thing it touched. Above it,
keep a 1–2 sentence rolling summary that you revise as new events land. Close each
update with **what the branch is currently converging on** — the goal the recent
events are bending toward. Keep it tight; this is a tail, not a transcript.

## When NOT to use this skill

- For an **after-the-fact recap** of a window of work, use `/openstory:recap`.
- For one **finished** session narrated start-to-finish, use a synopsis flow
  (`/openstory:recall` or `session_synopsis`).
- To **pick up where a past session left off**, use `/openstory:prime`.
