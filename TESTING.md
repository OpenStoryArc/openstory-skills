# Testing the skills

Skills are markdown instructions an LLM interprets, so there's no single "unit
test." Instead we test in **layers**, from cheapest/most-deterministic to richest.
Layers 0–2 are mechanical and gate every change; Layer 3 is a rubric an agent
follows. All of them lean on `citations.json` as the spec — the citation tree is
the test plan.

| Layer | What it proves | How | Deterministic? | Gate |
|---|---|---|---|---|
| 0 · Contract | Wiring + metadata are consistent | `node --test test/` · `build-citations.mjs --check` | yes | **CI** |
| 1 · Availability | The MCP server actually exposes every tool a skill cites | `probe-skills.mjs` (tools/list) | yes | local / seeded CI |
| 2 · Liveness | Every cited endpoint returns real, non-empty data | `probe-skills.mjs` (REST) | yes | local / seeded CI |
| 3 · Behavior | The skill, when run, does the right thing | agent rubric (below) | no (LLM-judged) | manual / eval |

## Layer 0 — static contract (runs in CI)

```bash
node --test test/mcp-contract.test.mjs    # .mcp.json: no ${...}, only env vars the binary reads
node scripts/build-citations.mjs --check  # every skill has a SKILL.md, frontmatter matches, every cited tool registered, tree fresh
```

Catches: broken manifest, undocumented skill, a citation pointing at a tool that
isn't registered, a stale `CITATIONS.md`. **Does not** prove a skill works against
data — a skill could cite a 404 endpoint and pass Layer 0.

## Layers 1 & 2 — data-path probe (run against a real OpenStory)

```bash
node scripts/probe-skills.mjs                          # against localhost:3002
OPENSTORY_API_URL=https://your-instance node scripts/probe-skills.mjs
```

For every built skill, reads its cited tools from `citations.json` and checks:
- **Layer 1** — spawns `open-story-mcp`, `tools/list`, asserts each cited tool is exposed.
- **Layer 2** — hits each tool's REST endpoint, asserts `200` + a non-trivial body.

A skill passes only if all its live tools pass both; `pending` tools are skipped,
not failed. Exit non-zero on any failure. **This is the layer that would have
caught both the silent-zeros `.mcp.json` bug and the 404 `session_story`
citation.** It needs a running OpenStory with data, so it runs locally or in CI
against a seeded store (see "Toward CI" below).

## Layer 3 — behavioral rubric (an agent follows this)

A human or agent invokes the skill against a real store and scores the output.
Per skill, check:

1. **Tool use** — did it call the tools `citations.json` says it should, and no
   ad-hoc shell/SQL instead?
2. **No invention** — every number/date/name in the output traces to a tool
   result. Nothing fabricated. (Cross-check a figure against the raw tool call.)
3. **Format** — matches the `## Phase 2 — render` block in the `SKILL.md`.
4. **Honest mode** — `heuristic` skills say which mode they ran in; the
   "OpenStory isn't connected" path triggers when tools are unavailable (test by
   pointing at a dead `OPENSTORY_API_URL`).
5. **Scope discipline** — respects the "When NOT to use this skill" boundaries.

A lightweight way to run Layer 3 programmatically: invoke the skill in a subagent
against a seeded store, capture the transcript, and have a judge agent score it
against the five points above. Golden-output snapshots work for the deterministic
parts (which tools were called) but not the prose.

## Toward CI for Layers 1–2

The probe needs data, which CI doesn't have by default. The path is the OpenStory
repo's testcontainers harness (`start_open_story` with seed fixtures): boot a
seeded OpenStory in a container, build `open-story-mcp`, point the probe at it.
That's the "T2" integration test tracked in the OpenStory repo — when it lands,
Layers 1–2 become a PR gate here too.

## Adding a skill — the checklist

1. Write `skills/<name>/SKILL.md` (frontmatter `name` must equal the directory).
2. Add it + its prompts to `citations.json` (skill entry + prompt entries, tools
   that already exist in the `tools` registry).
3. `node scripts/build-citations.mjs` — regenerate `CITATIONS.md`; fix any
   validation error it prints.
4. `node scripts/probe-skills.mjs` — confirm the data path is green.
5. Commit. CI re-runs Layers 0 on the PR.
