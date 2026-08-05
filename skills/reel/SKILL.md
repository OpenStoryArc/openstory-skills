---
name: reel
description: Turn a topic from your own OpenStory history into a saved, replayable reel — then play it on your dashboard. Use when the user asks to "make a reel", "save this story", "tell the story of X as a reel", "turn this into a reel", or "replay that story". Three phases, MCP-only.
---

# reel

Turn a topic from the user's own OpenStory history into a saved, replayable
reel — then play it on their dashboard. Three phases, MCP-only. The skill
argument is the topic, e.g. `/openstory:reel the nats leaf migration`.

## Phase 1 — research (honesty rules)

Call the OpenStory MCP tools (named `mcp__openstory__*`; fetch schemas via
ToolSearch if they aren't loaded):

- `mcp__openstory__agent_search` / `mcp__openstory__search` — find the story
  in the record for the given topic.
- `mcp__openstory__session_story` / `mcp__openstory__session_synopsis` — on
  hit sessions, pull the moments that carry the story.

Collect 4–8 moments, each a REAL `(session_id, event_id)` pair pulled from a
tool result. Rules:

- Quote display values verbatim — don't paraphrase a command or error into
  something cleaner than what happened.
- Never fabricate an id or a line the record doesn't support. If a moment
  feels right but you can't find a real event backing it, drop it.
- Exclude THIS conversation's own request — a reel about "make me a reel"
  is the circularity trap, not a story.
- Note out loud what the record does NOT contain (gaps, missing sessions,
  topics with thin coverage) rather than papering over them.

## Phase 2 — author

Call `mcp__openstory__save_reel` with:

```
{ title, stops: [{ sessionId, eventId, line, clipAt? }], closer?, author? }
```

Write each `line` for the ear: contractions, no symbols, 1–3 sentences — this
gets read aloud on the dashboard, not skimmed on a page.

If the result comes back with `invalid_stops`, an id was wrong. Re-search and
re-save with a corrected id from a fresh tool result — never guess a "fixed"
id to make the error go away.

## Phase 3 — show

Call `mcp__openstory__play_reel { id }` — this drives the dashboard's Reels
tab, which plays the saved sequence (Event Spotlight per stop, caption +
voice). Then:

1. `mcp__openstory__where_is_user` — confirm the reel actually landed in
   front of them.
2. Hand the wheel back and ask for a reaction — don't keep narrating over
   a reel that's already playing.
3. Mention the reel is saved and replayable any time from the Reels tab —
   this isn't a one-shot demo, it's now part of their history.

**Replaying an existing reel.** If the user is asking to replay something
already saved ("play that reel again", "replay the one about X") rather than
make a new one, skip Phase 1 and 2 entirely:

1. Call `mcp__openstory__list_reels` — it returns every saved reel
   (`{id, title, created, author, stopCount}`).
2. Match by title/topic against what the user described. If more than one
   is a plausible match, ask which one rather than guessing.
3. If nothing matches, say so plainly and offer to make a new reel instead
   — never guess an id or invent a reel that isn't in the list.
4. Once matched, `play_reel { id }` with the real id from `list_reels`, then
   follow the same `where_is_user` → hand back → confirm steps above.

## When NOT to use this skill

- One-off session narration without saving → `session_story` + `navigate_to`
  directly, no reel needed.
- Cost/time/recall questions → the dedicated `/openstory:cost`,
  `/openstory:time`, `/openstory:recall` skills.
- If `save_reel` / `list_reels` / `play_reel` aren't available, the reels
  feature isn't in your OpenStory build yet — say so, don't fall back to
  faking a reel with `navigate_to` calls alone.
