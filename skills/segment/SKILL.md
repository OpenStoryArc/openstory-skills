---
name: segment
description: Read a closed story arc into paragraphs — consecutive exchanges sharing one intent — as a final, author-stamped reading over the arc's exchange handles. Use when the user asks "what were the threads in that arc", "group what happened", "segment that session", or wants the intents behind a run of prompts. Hindsight reading; never moves a handle.
---

# segment

Produce the final reading of one closed arc. The skill argument is an arc
handle (or prefix), optionally with a session id, e.g. `/openstory:segment 3f9a2c`.

Thin wrapper: the instruction, shape, and laws are the OpenStory MCP
`segment_arc` prompt.

## Phase 1 — fetch the instruction with the exchanges

`prompts/get { "name": "segment_arc", "arguments": { "handle", "session_id"? } }`
(Claude Code: `/mcp__openstory__segment_arc`). The embedded resource carries the
arc's exchanges in order, each with its handle, prompt, verbs, entities. That
list is the universe of handles you may group.

## Phase 2 — read with hindsight

Group the exchange handles, in order, into paragraphs that each share one
intent. A shift that turns out to be the answer to the previous question is
the same paragraph (the dogfood run found the live, no-lookahead fold
over-segments by about a third; hindsight is the point of this skill).

Output one JSON object matching `openstory://schemas/reading`:
`{ handle, standing: "final", paragraphs: [ { exchanges: [handle…], intent } ], author }`.

Laws (enforced by the validator behind the write hand):
- every exchange handle of the arc in exactly one paragraph, in arc order;
- never a handle the arc does not hold; never an empty paragraph;
- a final reading supersedes a provisional one and never deletes it.

## Phase 3 — land it

Until group D ships, show the reading as JSON and, if the user wants it kept,
save a reel whose stops are the first event of each paragraph with the intent
as the line. Never write real session text into a repo.

## When NOT to use this skill

- Title and slots for an arc → `/openstory:narrate`.
- Live, provisional reading as exchanges close → `/openstory:listen`.
