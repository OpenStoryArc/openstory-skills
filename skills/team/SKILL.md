---
name: team
description: See who on your team has an active or recent OpenStory session and what each person is working on — live roster, per-teammate summaries, and recent focus. Requires federated sessions (multiple hosts/users reporting to one store). Use when the user asks "who's working right now", "what is <teammate> on", "team activity", "what did my team do today", or "sync me before our standup".
---

# team

Co-presence: when sessions federate, OpenStory is a shared room. Show who's in
it and on what. Two phases: pull via MCP, then render. Report only what's there.

## Phase 1 — pull the numbers

OpenStory MCP tools (`mcp__openstory__*`):

- `mcp__openstory__list_sessions` — every session carries `host`, `user`,
  `project_name`, `last_event`, `status`. Group by `host`/`user` for the roster;
  a session is **live** if `status` is ongoing and `last_event` is within your
  window (< 5 min = live, < 1 h = idle).
- `mcp__openstory__session_synopsis` — per teammate's recent session, for a
  one-paragraph "what they're on".

If the user names a teammate, filter to that `user`/`host`. Default window: live
+ last 24 h.

If only one host/user shows up, the store isn't federated yet — say so (this skill
needs multiple machines streaming to one OpenStory; see the distributed setup).

## Phase 2 — render

```
Team — <live> live · <idle> idle · <hosts> hosts
●  <teammate>   <project> · <branch>   idle <Xm>
○  <teammate>   <project>              idle <Xh>

This week
<teammate> — <one-paragraph synopsis of their focus>
```

`●` = live, `○` = idle. Close with the single most active thread to sync on.

## When NOT to use this skill

- For *your own* recap, use `/openstory:recap`; your own standup, `/openstory:standup`.
- For one specific session's detail, use `/openstory:recall` or a synopsis.
