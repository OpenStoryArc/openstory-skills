---
name: arc
description: Narrate the story of a project or topic from your session history — the key decisions and turning points, as a deterministic timeline grounded in real sessions and git. Use when the user asks "tell the story of <project>", "how did <X> come to be", "trace the arc of <topic>", "what's the history of this", or wants a narrative built from the record (not a vibe summary).
---

# arc

Your session log is canonical memory; turn it into a story you can read or stand
up on. Deterministic = grounded in the record + git, reproducible. Two phases.

## Phase 1 — gather

OpenStory MCP tools (`mcp__openstory__*`):

- `mcp__openstory__search` with the topic/project → every session that touched it.
- `mcp__openstory__session_synopsis` on the key sessions → what each was about.
- For project-origin arcs, anchor milestones to `git log` (first commit, big
  merges) so the timeline is reproducible, not invented.

If the user gives a topic, search it; for a whole project, walk sessions oldest→newest.

If those tools aren't available, OpenStory isn't connected — say so, don't guess.

## Phase 2 — render

```
The arc of <project/topic> — <date range> · <N> sessions

<date>  <milestone>
        <one line: what happened / what it decided>
...

Through-line: <the single sentence the arc adds up to>
```

Order strictly by date. Each milestone ties to a real session or commit. Close
with the through-line — the decision or shift the whole arc points at.

## When NOT to use this skill

- To *find* a specific fix + commands, use `/openstory:recall`.
- For a week's activity by project, use `/openstory:recap`.
- For one session, use a session synopsis directly.
