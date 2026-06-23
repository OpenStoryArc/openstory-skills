# Citation tree — prompts → skills → tools → endpoints → code

> **Generated** from `citations.json` by `scripts/build-citations.mjs`. Do not edit by
> hand — edit the JSON and run `node scripts/build-citations.mjs`. CI runs
> `--check` so this can never drift from the skills on disk. Citations are
> grounded against OpenStory `master`: `rs/mcp/src/http_store.rs` (the MCP→REST
> endpoint map) and live API probes.

**Coverage:** 20/21 common prompts are backed by a built skill — 15 live · 5 heuristic · 1 pending.

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
  → `watch` _(pending — not built)_
  - `subscribe_session` — `mcp__openstory__subscribe_session` → `NATS/WS subscription (not REST)` — _rs/mcp streaming tools_

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
| `tool_histogram` | `mcp__openstory__tool_histogram (proposed)` | `would wrap GET /api/insights/tool-evolution (live) + bash-command parsing` | PROPOSED — see docs/BACKLOG.md | pending |

## Skills

| Skill | Question | Status | Tools |
|---|---|---|---|
| `/openstory:recap` | What did I work on this week? | live | `project_pulse`, `list_sessions` |
| `/openstory:cost` | What did my agent sessions cost? | live | `token_usage`, `daily_token_usage` |
| `/openstory:scan` | Anything sensitive before I share? | heuristic | `search` |
| `/openstory:recall` | How/where did I do X last time? | live | `search`, `session_synopsis`, `tool_journey`, `session_errors` |
| `/openstory:standup` | Write my standup for today. | live | `list_sessions`, `session_synopsis` |
| `/openstory:coach` | How do I work / where do I get stuck? | heuristic | `session_patterns`, `session_errors`, `productivity`, `search`, `list_sessions` |
| `/openstory:time` | Where does my time actually go? | live | `productivity`, `list_sessions` |
| `/openstory:tools` | Which tools/commands do I rely on most? | heuristic | `tool_journey`, `list_sessions`, `tool_histogram` |
| `/openstory:team` | Who on my team is working on what? | live | `list_sessions`, `session_synopsis` |
| `/openstory:arc` | Tell the story of <project/topic>. | live | `search`, `session_synopsis` |
| `/openstory:prime` | Pick up where the last session left off. | live | `list_sessions`, `session_synopsis`, `session_transcript` |
| `watch` | Watch a branch's work as it streams. | pending | `subscribe_session` |

## Gaps

- **[06.3]** needs `watch` (not yet built)

**Pending server tools** (skills degrade gracefully until these land):
- `tool_histogram` — PROPOSED — see docs/BACKLOG.md

---
_Evidence tags: **live** = queried against your store · **heuristic** = composed from existing tools, sharper when a dedicated tool lands · **illustrative** = representative shape._
