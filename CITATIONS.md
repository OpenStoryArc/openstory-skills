# Citation tree — prompts → skills → tools → endpoints → code

> **Generated** from `citations.json` by `scripts/build-citations.mjs`. Do not edit by
> hand — edit the JSON and run `node scripts/build-citations.mjs`. CI runs
> `--check` so this can never drift from the skills on disk. Citations are
> grounded against OpenStory `master`: `rs/mcp/src/http_store.rs` (the MCP→REST
> endpoint map) and live API probes.

**Coverage:** 31/31 common prompts are backed by a built skill — 26 live · 5 heuristic · 0 pending.

This is the trace an agent can follow to trust a skill: a prompt → the skill that
serves it → the MCP tools it calls → the REST endpoint each tool wraps → the
source line that defines it.

## Prompt → skill → tools

### 01 · Know your own work

- **[01.1]** "Summarize everything I've worked on this week across all my projects — group it by project and tell me what actually shipped."
  → **`/openstory:recap`** _(live)_
  - `project_pulse` — `mcp__openstory__project_pulse` → `GET /api/insights/pulse?days=` — _rs/mcp/src/http_store.rs:29_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_

- **[01.2]** "What have my agent sessions cost me? Give me the total spend, and a tokens-per-day timeline."
  → **`/openstory:cost`** _(live)_
  - `token_usage` — `mcp__openstory__token_usage` → `GET /api/insights/token-usage?days=&model=` — _rs/mcp/src/http_store.rs:33_
  - `daily_token_usage` — `mcp__openstory__daily_token_usage` → `GET /api/insights/token-usage/daily?days=` — _rs/mcp/src/http_store.rs:34_

- **[01.3]** "Before I share my session history, scan it for anything sensitive — secrets, API keys, private details."
  → **`/openstory:scan`** _(heuristic)_
  - `search` — `mcp__openstory__search` → `GET /api/search?q=&limit=&session_id=` — _rs/mcp/src/http_store.rs:35_

- **[01.4]** "Which tools and commands do I rely on most?"
  → **`/openstory:tools`** _(heuristic)_
  - `tool_journey` — `mcp__openstory__tool_journey` → `GET /api/sessions/{id}/tool-journey` — _rs/mcp/src/http_store.rs:26_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_

- **[01.5]** "Where does my time actually go?"
  → **`/openstory:time`** _(live)_
  - `productivity` — `mcp__openstory__productivity` → `GET /api/insights/productivity?days=` — _rs/mcp/src/http_store.rs:32_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_

- **[01.6]** "If I uploaded my coding history to a third party, what would they actually learn about me?"
  → **`/openstory:exposure`** _(live)_
  - `productivity` — `mcp__openstory__productivity` → `GET /api/insights/productivity?days=` — _rs/mcp/src/http_store.rs:32_
  - `daily_token_usage` — `mcp__openstory__daily_token_usage` → `GET /api/insights/token-usage/daily?days=` — _rs/mcp/src/http_store.rs:34_
  - `project_pulse` — `mcp__openstory__project_pulse` → `GET /api/insights/pulse?days=` — _rs/mcp/src/http_store.rs:29_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_

### 02 · Sense your team

- **[02.1]** "Who on my team has an active session right now, and what is each person working on?"
  → **`/openstory:team`** _(live)_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_

- **[02.2]** "Summarize my teammates' sessions from the last day — one short paragraph each."
  → **`/openstory:team`** _(live)_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_
  - `session_synopsis` — `mcp__openstory__session_synopsis` → `GET /api/sessions/{id}/synopsis` — _rs/mcp/src/http_store.rs:25_

- **[02.3]** "Show me live activity across the team in the last hour — who's streaming, on what branch."
  → **`/openstory:team`** _(live)_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_

- **[02.4]** "Find a teammate's sessions and summarize what they've been focused on this week."
  → **`/openstory:team`** _(live)_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_
  - `session_synopsis` — `mcp__openstory__session_synopsis` → `GET /api/sessions/{id}/synopsis` — _rs/mcp/src/http_store.rs:25_

### 03 · Narrate the story

- **[03.1]** "Trace the story of how this project came to be from my session history. Highlight the key decisions and turning points."
  → **`/openstory:arc`** _(live)_
  - `search` — `mcp__openstory__search` → `GET /api/search?q=&limit=&session_id=` — _rs/mcp/src/http_store.rs:35_
  - `session_synopsis` — `mcp__openstory__session_synopsis` → `GET /api/sessions/{id}/synopsis` — _rs/mcp/src/http_store.rs:25_

- **[03.2]** "Compile every session related to <topic> and narrate the arc, start to finish."
  → **`/openstory:arc`** _(live)_
  - `search` — `mcp__openstory__search` → `GET /api/search?q=&limit=&session_id=` — _rs/mcp/src/http_store.rs:35_
  - `session_synopsis` — `mcp__openstory__session_synopsis` → `GET /api/sessions/{id}/synopsis` — _rs/mcp/src/http_store.rs:25_

- **[03.3]** "Write me a standup update from today's sessions: what I did, what's blocked, and what's next."
  → **`/openstory:standup`** _(live)_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_
  - `session_synopsis` — `mcp__openstory__session_synopsis` → `GET /api/sessions/{id}/synopsis` — _rs/mcp/src/http_store.rs:25_

### 04 · Coach yourself

- **[04.1]** "Analyze my sessions from the last month and give me honest feedback on my prompt engineering."
  → **`/openstory:coach`** _(heuristic)_
  - `session_patterns` — `mcp__openstory__session_patterns` → `GET /api/sessions/{id}/patterns?type=` — _rs/mcp/src/http_store.rs:24_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_

- **[04.2]** "Find where my sessions tend to stall, loop, or repeat work. What are my recurring failure patterns?"
  → **`/openstory:coach`** _(heuristic)_
  - `session_patterns` — `mcp__openstory__session_patterns` → `GET /api/sessions/{id}/patterns?type=` — _rs/mcp/src/http_store.rs:24_
  - `session_errors` — `mcp__openstory__session_errors` → `GET /api/sessions/{id}/errors` — _rs/mcp/src/http_store.rs:28_

- **[04.3]** "What direction has my work been pointing lately? Cluster my recent sessions by theme."
  → **`/openstory:coach`** _(heuristic)_
  - `search` — `mcp__openstory__search` → `GET /api/search?q=&limit=&session_id=` — _rs/mcp/src/http_store.rs:35_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_

### 05 · Recall anything

- **[05.1]** "Find the last time I solved <problem>, and show me exactly how I did it."
  → **`/openstory:recall`** _(live)_
  - `search` — `mcp__openstory__search` → `GET /api/search?q=&limit=&session_id=` — _rs/mcp/src/http_store.rs:35_
  - `session_synopsis` — `mcp__openstory__session_synopsis` → `GET /api/sessions/{id}/synopsis` — _rs/mcp/src/http_store.rs:25_
  - `tool_journey` — `mcp__openstory__tool_journey` → `GET /api/sessions/{id}/tool-journey` — _rs/mcp/src/http_store.rs:26_

- **[05.2]** "Did I ever set up <X>? Locate the session and pull out the precise commands."
  → **`/openstory:recall`** _(live)_
  - `search` — `mcp__openstory__search` → `GET /api/search?q=&limit=&session_id=` — _rs/mcp/src/http_store.rs:35_
  - `tool_journey` — `mcp__openstory__tool_journey` → `GET /api/sessions/{id}/tool-journey` — _rs/mcp/src/http_store.rs:26_

- **[05.3]** "Search my sessions for <topic> and list every session that touched it, newest first."
  → **`/openstory:recall`** _(live)_
  - `search` — `mcp__openstory__search` → `GET /api/search?q=&limit=&session_id=` — _rs/mcp/src/http_store.rs:35_

### 06 · Ground your agent

- **[06.1]** "Before you start, query OpenStory for prior context on this project and pick up where the last session left off."
  → **`/openstory:prime`** _(live)_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_
  - `session_synopsis` — `mcp__openstory__session_synopsis` → `GET /api/sessions/{id}/synopsis` — _rs/mcp/src/http_store.rs:25_
  - `session_transcript` — `mcp__openstory__session_transcript` → `GET /api/sessions/{id}/transcript` — _rs/server/src/router.rs (verified 200)_

- **[06.2]** "Use OpenStory to check whether we've hit this error before — and what fixed it — before debugging from scratch."
  → **`/openstory:recall`** _(live)_
  - `search` — `mcp__openstory__search` → `GET /api/search?q=&limit=&session_id=` — _rs/mcp/src/http_store.rs:35_
  - `session_errors` — `mcp__openstory__session_errors` → `GET /api/sessions/{id}/errors` — _rs/mcp/src/http_store.rs:28_

- **[06.3]** "Watch the work happening on <branch> through OpenStory and summarize it for me as it streams."
  → **`/openstory:watch`** _(live)_
  - `subscribe_session` — `mcp__openstory__subscribe_session` → `NATS/WS subscription (not REST)` — _rs/mcp streaming tools_
  - `list_sessions` — `mcp__openstory__list_sessions` → `GET /api/sessions` — _rs/mcp/src/http_store.rs:22_
  - `session_activity` — `mcp__openstory__session_activity` → `GET /api/sessions/{id}/activity` — _rs/server/src/router.rs (verified 200)_

### 07 · Tell it as a reel

- **[07.1]** "Turn the story of the nats leaf migration into a reel I can save and replay."
  → **`/openstory:reel`** _(live)_
  - `agent_search` — `mcp__openstory__agent_search` → `GET /api/search?q=&limit= (grouped by session)` — _rs/mcp/src/tools/search.rs_
  - `session_story` — `mcp__openstory__session_story` → `GET /api/sessions/{id}/events (+ patterns, composed)` — _rs/mcp/src/tools/story.rs_
  - `save_reel` — `mcp__openstory__save_reel` → `POST /api/reels` — _rs/mcp/src/tools/reels.rs, rs/server/src/api.rs (merged to master in OpenStory PR #106, 2026-08-07)_

- **[07.2]** "Save this session as a reel with a closer line, then play it for me."
  → **`/openstory:reel`** _(live)_
  - `search` — `mcp__openstory__search` → `GET /api/search?q=&limit=&session_id=` — _rs/mcp/src/http_store.rs:35_
  - `session_synopsis` — `mcp__openstory__session_synopsis` → `GET /api/sessions/{id}/synopsis` — _rs/mcp/src/http_store.rs:25_
  - `save_reel` — `mcp__openstory__save_reel` → `POST /api/reels` — _rs/mcp/src/tools/reels.rs, rs/server/src/api.rs (merged to master in OpenStory PR #106, 2026-08-07)_

- **[07.3]** "Replay that reel we made about the mongo migration."
  → **`/openstory:reel`** _(live)_
  - `list_reels` — `mcp__openstory__list_reels` → `GET /api/reels` — _rs/mcp/src/tools/reels.rs, rs/server/src/api.rs (merged to master in OpenStory PR #106, 2026-08-07)_
  - `play_reel` — `mcp__openstory__play_reel` → `POST /api/control {action: navigate_to, params: {kind: reel}}` — _rs/mcp/src/tools/reels.rs (merged to master in OpenStory PR #106, 2026-08-07)_
  - `where_is_user` — `mcp__openstory__where_is_user` → `GET /api/ui-state` — _rs/mcp/src/tools/control.rs_

### 08 · Remember (memory hands)

- **[08.1]** "Why did we switch from <A> to <B>? Cite the arc where it was decided."
  → **`/openstory:remember`** _(live)_
  - `story_search` — `mcp__openstory__story_search` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_
  - `story_summary` — `mcp__openstory__story_summary` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_
  - `story_context` — `mcp__openstory__story_context` → `GET /api/sessions/{id}/patterns?type=story.exchange` — _rs/mcp/src/tools/memory.rs_

- **[08.2]** "What did I say I'd come back to and never did?"
  → **`/openstory:remember`** _(live)_
  - `story_list` — `mcp__openstory__story_list` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_
  - `story_summary` — `mcp__openstory__story_summary` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_
  - `story_related` — `mcp__openstory__story_related` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_

- **[08.3]** "What is my position on <topic>, in my own words, and when did it change?"
  → **`/openstory:remember`** _(live)_
  - `story_search` — `mcp__openstory__story_search` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_
  - `story_summary` — `mcp__openstory__story_summary` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_
  - `story_descend` — `mcp__openstory__story_descend` → `GET /api/sessions/{id}/patterns?type=story.exchange` — _rs/mcp/src/tools/memory.rs_

- **[08.4]** "Narrate the arc we just finished: title, the question that opened it, how it closed, what we decided and deferred."
  → **`/openstory:narrate`** _(live)_
  - `story_list` — `mcp__openstory__story_list` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_
  - `story_context` — `mcp__openstory__story_context` → `GET /api/sessions/{id}/patterns?type=story.exchange` — _rs/mcp/src/tools/memory.rs_
  - `story_descend` — `mcp__openstory__story_descend` → `GET /api/sessions/{id}/patterns?type=story.exchange` — _rs/mcp/src/tools/memory.rs_

- **[08.5]** "Break that arc into its threads and name the intent of each."
  → **`/openstory:segment`** _(live)_
  - `story_list` — `mcp__openstory__story_list` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_
  - `story_context` — `mcp__openstory__story_context` → `GET /api/sessions/{id}/patterns?type=story.exchange` — _rs/mcp/src/tools/memory.rs_

- **[08.6]** "Keep a running story of this session: narrate each arc as it closes."
  → **`/openstory:listen`** _(live)_
  - `story_list` — `mcp__openstory__story_list` → `GET /api/sessions/{id}/patterns?type=story.arc` — _rs/mcp/src/tools/memory.rs_
  - `subscribe_arcs` — `mcp__openstory__subscribe_arcs` → `NATS patterns.{project}.{session} (JSON array of PatternEvent)` — _rs/mcp/src/subscription.rs_

## Data sources (every tool the skills cite)

| Tool | MCP | REST endpoint | Source | Status |
|---|---|---|---|---|
| `list_sessions` | `mcp__openstory__list_sessions` | `GET /api/sessions` | rs/mcp/src/http_store.rs:22 | live |
| `search` | `mcp__openstory__search` | `GET /api/search?q=&limit=&session_id=` | rs/mcp/src/http_store.rs:35 | live |
| `session_synopsis` | `mcp__openstory__session_synopsis` | `GET /api/sessions/{id}/synopsis` | rs/mcp/src/http_store.rs:25 | live |
| `session_transcript` | `mcp__openstory__session_transcript` | `GET /api/sessions/{id}/transcript` | rs/server/src/router.rs (verified 200) | live |
| `session_patterns` | `mcp__openstory__session_patterns` | `GET /api/sessions/{id}/patterns?type=` | rs/mcp/src/http_store.rs:24 | live |
| `session_errors` | `mcp__openstory__session_errors` | `GET /api/sessions/{id}/errors` | rs/mcp/src/http_store.rs:28 | live |
| `tool_journey` | `mcp__openstory__tool_journey` | `GET /api/sessions/{id}/tool-journey` | rs/mcp/src/http_store.rs:26 | live |
| `project_pulse` | `mcp__openstory__project_pulse` | `GET /api/insights/pulse?days=` | rs/mcp/src/http_store.rs:29 | live |
| `productivity` | `mcp__openstory__productivity` | `GET /api/insights/productivity?days=` | rs/mcp/src/http_store.rs:32 | live |
| `token_usage` | `mcp__openstory__token_usage` | `GET /api/insights/token-usage?days=&model=` | rs/mcp/src/http_store.rs:33 | live |
| `daily_token_usage` | `mcp__openstory__daily_token_usage` | `GET /api/insights/token-usage/daily?days=` | rs/mcp/src/http_store.rs:34 | live |
| `subscribe_session` | `mcp__openstory__subscribe_session` | `NATS/WS subscription (not REST)` | rs/mcp streaming tools | live |
| `session_activity` | `mcp__openstory__session_activity` | `GET /api/sessions/{id}/activity` | rs/server/src/router.rs (verified 200) | live |
| `tool_histogram` | `mcp__openstory__tool_histogram (proposed)` | `would wrap GET /api/insights/tool-evolution (live) + bash-command parsing` | PROPOSED — see docs/BACKLOG.md | pending |
| `agent_search` | `mcp__openstory__agent_search` | `GET /api/search?q=&limit= (grouped by session)` | rs/mcp/src/tools/search.rs | live |
| `session_story` | `mcp__openstory__session_story` | `GET /api/sessions/{id}/events (+ patterns, composed)` | rs/mcp/src/tools/story.rs | live |
| `navigate_to` | `mcp__openstory__navigate_to` | `POST /api/control {action: navigate_to}` | rs/mcp/src/tools/control.rs (merged to master in OpenStory PR #106, 2026-08-07) | live |
| `where_is_user` | `mcp__openstory__where_is_user` | `GET /api/ui-state` | rs/mcp/src/tools/control.rs | live |
| `save_reel` | `mcp__openstory__save_reel` | `POST /api/reels` | rs/mcp/src/tools/reels.rs, rs/server/src/api.rs (merged to master in OpenStory PR #106, 2026-08-07) | live |
| `list_reels` | `mcp__openstory__list_reels` | `GET /api/reels` | rs/mcp/src/tools/reels.rs, rs/server/src/api.rs (merged to master in OpenStory PR #106, 2026-08-07) | live |
| `play_reel` | `mcp__openstory__play_reel` | `POST /api/control {action: navigate_to, params: {kind: reel}}` | rs/mcp/src/tools/reels.rs (merged to master in OpenStory PR #106, 2026-08-07) | live |
| `story_list` | `mcp__openstory__story_list` | `GET /api/sessions/{id}/patterns?type=story.arc` | rs/mcp/src/tools/memory.rs | live |
| `story_summary` | `mcp__openstory__story_summary` | `GET /api/sessions/{id}/patterns?type=story.arc` | rs/mcp/src/tools/memory.rs | live |
| `story_descend` | `mcp__openstory__story_descend` | `GET /api/sessions/{id}/patterns?type=story.exchange` | rs/mcp/src/tools/memory.rs | live |
| `story_surface` | `mcp__openstory__story_surface` | `GET /api/sessions/{id}/patterns?type=story.exchange` | rs/mcp/src/tools/memory.rs | live |
| `story_context` | `mcp__openstory__story_context` | `GET /api/sessions/{id}/patterns?type=story.exchange` | rs/mcp/src/tools/memory.rs | live |
| `story_search` | `mcp__openstory__story_search` | `GET /api/sessions/{id}/patterns?type=story.arc` | rs/mcp/src/tools/memory.rs | live |
| `story_related` | `mcp__openstory__story_related` | `GET /api/sessions/{id}/patterns?type=story.arc` | rs/mcp/src/tools/memory.rs | live |
| `subscribe_arcs` | `mcp__openstory__subscribe_arcs` | `NATS patterns.{project}.{session} (JSON array of PatternEvent)` | rs/mcp/src/subscription.rs | live |
| `enrich` | `mcp__openstory__enrich` | `POST /api/memory kind=enrichment` | rs/mcp/src/tools/memory_write.rs | live |
| `adjudicate_boundary` | `mcp__openstory__adjudicate_boundary` | `POST /api/memory kind=verdict` | rs/mcp/src/tools/memory_write.rs | live |
| `link_saga` | `mcp__openstory__link_saga` | `POST /api/memory kind=saga` | rs/mcp/src/tools/memory_write.rs | live |
| `propose_keep` | `mcp__openstory__propose_keep` | `POST /api/memory kind=keep` | rs/mcp/src/tools/memory_write.rs | live |

## Skills

| Skill | Question | Status | Tools |
|---|---|---|---|
| `/openstory:recap` | What did I work on this week? | live | `project_pulse`, `list_sessions` |
| `/openstory:cost` | What did my agent sessions cost? | live | `token_usage`, `daily_token_usage` |
| `/openstory:scan` | Anything sensitive before I share? | heuristic | `search` |
| `/openstory:exposure` | What would a third party infer about me from my history? | live | `productivity`, `daily_token_usage`, `project_pulse`, `list_sessions` |
| `/openstory:recall` | How/where did I do X last time? | live | `search`, `session_synopsis`, `tool_journey`, `session_errors` |
| `/openstory:standup` | Write my standup for today. | live | `list_sessions`, `session_synopsis` |
| `/openstory:coach` | How do I work / where do I get stuck? | heuristic | `session_patterns`, `session_errors`, `productivity`, `search`, `list_sessions` |
| `/openstory:time` | Where does my time actually go? | live | `productivity`, `list_sessions` |
| `/openstory:tools` | Which tools/commands do I rely on most? | heuristic | `tool_journey`, `list_sessions`, `tool_histogram` |
| `/openstory:team` | Who on my team is working on what? | live | `list_sessions`, `session_synopsis` |
| `/openstory:arc` | Tell the story of <project/topic>. | live | `search`, `session_synopsis` |
| `/openstory:prime` | Pick up where the last session left off. | live | `list_sessions`, `session_synopsis`, `session_transcript` |
| `/openstory:watch` | Watch a branch's work as it streams. | live | `subscribe_session`, `list_sessions`, `session_activity`, `tool_journey` |
| `/openstory:reel` | Turn <topic> into a saved, replayable reel. | live | `agent_search`, `search`, `session_story`, `session_synopsis`, `save_reel`, `list_reels`, `play_reel`, `where_is_user` |
| `/openstory:remember` | What did I decide / say / defer about X, by traversal under a token budget? | live | `story_search`, `story_list`, `story_summary`, `story_descend`, `story_context`, `story_related` |
| `/openstory:narrate` | Title, question, resolution, summary and slots for a closed arc? | live | `story_list`, `story_context`, `story_descend`, `enrich` |
| `/openstory:segment` | What were the intents (paragraphs) inside a closed arc? | live | `story_list`, `story_context`, `save_reel` |
| `/openstory:listen` | Narrate arcs as they close, live or by polling? | live | `story_list`, `story_context`, `subscribe_arcs`, `enrich`, `adjudicate_boundary` |

## Gaps

- None — every prompt resolves to a built skill.

**Pending server tools** (skills degrade gracefully until these land):
- `tool_histogram` — PROPOSED — see docs/BACKLOG.md

---
_Evidence tags: **live** = queried against your store · **heuristic** = composed from existing tools, sharper when a dedicated tool lands · **illustrative** = representative shape._
