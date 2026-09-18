---
name: listen
description: Narrate your OpenStory history as it closes — watch for newly closed story arcs and exchanges in a session (or the whole store) and run the narrate and segment readings on each, author-stamped, over stable handles. Use when the user says "narrate as I go", "keep a running story of this session", "listen to that session", or wants live readings. Read-only over history; pairs with /loop.
---

# listen

Run the memory motions live: each time an arc closes, narrate it; each time an
exchange closes, extend the provisional reading. The skill argument is a
session id (or nothing, for every session), e.g. `/openstory:listen 8b0e…`.

Thin wrapper: the per-node instructions are the OpenStory MCP prompts
(`narrate_arc`, `segment_arc`, `read_exchange`, `adjudicate_seam`). This skill
only decides *when* to run them.

## How the stream reaches you

The MCP stream hand `subscribe_arcs { session_id?, from_seq? }` emits a
notification per closed exchange or arc, each carrying `needs` and the exact
`prompts/get` calls to make (`data.prompts`). Two ways to receive it:

- **Push (Claude Code, research preview)** — run open-story-mcp in channel
  mode: set `OPENSTORY_CHANNEL=all` (or a session id) in the server's env in
  `.mcp.json`, and start Claude Code with
  `claude --dangerously-load-development-channels server:openstory`. Each
  closed node then lands in the session as
  `<channel source="openstory" kind="arc" handle="…" needs="enrich,adjudicate">JSON</channel>`
  with the `prompts/get` calls to make in the body. No tool call needed;
  act on each as it arrives.
- **Poll (works everywhere)** — treat history as a lazy list. Keep a cursor
  (the last arc `started_at` you have read) and on each tick call
  `mcp__openstory__story_list { session_id?, limit }`, take arcs newer than the
  cursor, and act on each. Pair with `/loop`:

  `/loop 10m /openstory:listen <session_id>`

  A tick with nothing new is a no-op; say so in one line and advance nothing.

## On each closed arc

1. `prompts/get narrate_arc { handle, session_id }` → produce the enrichment
   (see `/openstory:narrate`, Phase 2 and 3).
2. `prompts/get segment_arc { handle, session_id }` → produce the final reading
   (see `/openstory:segment`).
3. If the arc's `ambiguous_seams` is non-empty, `prompts/get adjudicate_seam
   { handle, session_id, seam }` per seam → a verdict with a reason.
4. Land each through the write hands: `mcp__openstory__enrich` for the
   enrichment, `mcp__openstory__adjudicate_boundary` per seam verdict, a
   `reading` memory write for the final reading. Each returns the stored,
   author-stamped record; the next `story_summary` carries it.

## On each closed exchange (push mode only)

`prompts/get read_exchange { handle, session_id, reading }` with the
provisional reading so far → Continue or Break, and an updated intent. This is
the streaming fold: no lookahead, superseded by `segment_arc` when the arc
closes. Skip it in poll mode; polling sees arcs, and the final reading covers
them.

## Laws (enforced by the validator behind the write hands; obey them now)

- Every handle you output appears in the context you were given. Never invent one.
- Author-stamp everything `{ host, model }`.
- A final reading supersedes a provisional one and never deletes it.
- Nothing you produce changes a handle or the skeleton.

## When NOT to use this skill

- One arc, once → `/openstory:narrate` or `/openstory:segment`.
- A question about the past → `/openstory:remember`.
- Raw live events as they land → `subscribe_session` (the observation stream).
