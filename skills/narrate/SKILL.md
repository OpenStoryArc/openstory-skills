---
name: narrate
description: Enrich a closed story arc from your OpenStory history — title, opening question, resolution, summary, and the slots (decisions, deferrals, tradeoffs, failures, stance) — as an author-stamped enrichment over stable handles. Use when the user asks "narrate that arc", "title what we just did", "summarize the last hour as a story", or hands you an arc handle. Reads through the memory hands; the model's judgment is the only thing added.
---

# narrate

Produce the enrichment for one closed arc. The skill argument is an arc handle
(16 hex, or a 4+ char prefix), optionally with a session id, e.g.
`/openstory:narrate 3f9a2c 8b0e…`. With no argument, take the most recent arc
from `mcp__openstory__story_list {}`.

This is a thin wrapper: the instruction, output shape, budget, and laws live in
the OpenStory MCP `narrate_arc` prompt. Do not restate them from memory.

## Phase 1 — fetch the instruction with the arc's context

Call `prompts/get { "name": "narrate_arc", "arguments": { "handle", "session_id"? } }`
(in Claude Code: the `/mcp__openstory__narrate_arc` prompt). You receive two
messages: the instruction (what to produce, the JSON shape, the budget, the
laws) and an embedded resource holding `story_context(handle)` plus the arc's
exchanges in order. If you need more than the context gives, use
`mcp__openstory__story_descend` on an exchange — never raw events first.

## Phase 2 — produce the enrichment

Follow the instruction. The output is one JSON object matching
`openstory://schemas/enrichment` (read it with `resources/read` if unsure):
handle, title, question, resolution, summary, slots, author `{ host, model }`.

Laws the write hand will enforce, so obey them now:
- every handle you output appears in the context you were given; never invent one;
- quote the human's words for `stance`; never strengthen a stance;
- your output changes no handle and no skeleton.

## Phase 3 — land it

Until the `enrich` write hand ships (memory hands group D), an enrichment has
no durable home in the store. Do one of:
- show it to the user as the JSON block, and
- if they want it kept, `mcp__openstory__save_reel` with the arc's opening
  and closing events as stops and the title as the reel title — a reel is a
  saved, replayable artifact and lives in their history.
Never write it into a repo that would carry real session text.

## When NOT to use this skill

- To read arcs into paragraphs → `/openstory:segment`.
- To answer a question → `/openstory:remember`.
- To narrate arcs as they close → `/openstory:listen`.
