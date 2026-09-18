---
name: remember
description: Answer a question about your own past work by traversal, not transcripts — carry story handles, descend only where needed, report the tokens it cost. Use when the user asks "what did I decide about X", "why did we switch from A to B", "what did I say I'd come back to", "what's my position on Z", or "what happened in that arc". Reads the OpenStory store through the memory hands; never writes history.
---

# remember

Answer a creator question by traversal over the story layer. The skill argument
is the question, e.g. `/openstory:remember why did we drop the Python host`.

This is a thin wrapper: the procedure, budget, and laws live in the OpenStory
MCP itself. The one source of truth is the `remember` prompt.

## Phase 0 — get the instruction from the MCP

Call `prompts/get` on the OpenStory MCP with `{ "name": "remember", "arguments":
{ "question": <the question> } }` (in Claude Code this is the `/mcp__openstory__remember`
prompt; other hosts call `prompts/get` directly). Follow the returned instruction.
If your host cannot call MCP prompts, the procedure below is the same text.

## The procedure (mirror of the MCP prompt)

Tools are `mcp__openstory__story_*`; fetch schemas via ToolSearch if needed.

1. **Find handles.** `story_search { query }` when you have words; `story_list
   { session_id }` when you know the session. Hits are handles, about fifty
   tokens each. Pick at most three.
2. **Read the top node.** `story_summary { handle }` — question, resolution,
   entities, `down` (exchange handles), `across` (related arcs). Often enough.
3. **Descend only where the answer needs it.** `story_descend { node }` one
   level at a time, or `story_context { node }` to keep ancestors and siblings
   with it. You never get a naked event.
4. **Stop** when the question is answered, or when about 1,400 tokens of tool
   results have been read. Do not keep digging past the budget: say what you
   found and what would need another call.

## Render

```
<answer, two to five sentences, quoting the human's words for any stance>
Handles visited: <arc/exchange handles you actually read>
Evidence: session <id-prefix>, <event ids or exchange handles> — <date>
Tokens spent (tool results): <your estimate>
```

Cite only handles and ids you saw in a tool result. Never invent one. If the
store has nothing, say so and suggest a broader `story_search` term.

## When NOT to use this skill

- A whole-session narration → `/openstory:arc` or `session_story`.
- A verbatim command you once ran → `/openstory:recall` (full-text over events).
- To narrate arcs as they close → `/openstory:listen`.
