---
name: exposure
description: Show what a third party could infer about you from your coding history if you uploaded it — your schedule and timezone, the days you were away, your burn rate, the categories of your life visible in project names, and the message text an uploader would carry off. Distinct from /openstory:scan, which hunts secrets; this hunts inferences no secret-scanner would flag. Use when the user asks "what does my history reveal about me", "what would a profiler learn", "is it safe to upload my sessions", "what would <vendor> see", or "how exposed am I".
---

# exposure

Answer one question: **if you handed this history to someone else's server, what
could they derive about you that you never typed?** Not secrets — inferences.
Schedule, absences, spend, categories of a life, and the words themselves.

Two phases: measure (deterministic, via the bundled script or MCP), then render
plainly. Never soften the findings and never invent one.

## Scope — read this before running anything

- **Your own store, only.** This audits the OpenStory instance the user owns and
  points at. There is no flag to target a person, a host, a teammate, or someone
  else's store, and you must not build one, improvise one, or filter the output
  down to one named individual. A polished "profile a developer from their
  transcripts" tool is a recipe as much as a warning — this stays a mirror.
- **Read-only.** Nothing here writes to the store or touches a transcript file.
- **Local only.** Nothing is uploaded. Verbatim message text goes to a local,
  git-ignored file — never into this conversation unless the user explicitly
  asks with `--show`.
- **Federated stores blend people.** If `list_sessions` shows more than one
  `user`/`host`, say so: the schedule and spend numbers are the *store's*, not
  one person's. Do not split them per teammate to "fix" it.

## Phase 1 — measure

Run the bundled script. It is stdlib-only Python 3, read-only, and does the
fiddly inference (contiguous sleep window across midnight, gap detection, payload
shape handling) deterministically so nothing has to be eyeballed:

```bash
AUDIT="${CLAUDE_PLUGIN_ROOT:-}/skills/exposure/scripts/exposure_audit.py"
[ -f "$AUDIT" ] || AUDIT=$(find ~/.claude/plugins -path '*skills/exposure/scripts/exposure_audit.py' 2>/dev/null | head -1)

python3 "$AUDIT" --days 90            # human-readable report
python3 "$AUDIT" --days 90 --json     # same numbers, machine-readable
```

(The script sits in `scripts/` next to this SKILL.md — if you already know that
absolute path, just use it directly.)

Add `--verbatim` for section 5. It writes the sample to `.openstory-exposure/`
in the working directory (the directory ignores itself via its own `.gitignore`)
and prints only counts. **Only add `--show` if the user explicitly asks to see
the text** — `--show` prints their own words into this transcript.

If Python isn't available, fall back to the MCP tools and do the arithmetic
yourself (all `mcp__openstory__*`; fetch schemas with ToolSearch first):

- `mcp__openstory__productivity` — events per hour (UTC) → peak, quiet window,
  timezone. The hours come back in **UTC**; a human's deadest hour is ~04:00
  local, so `offset ≈ 4 − deadest_hour_utc` is roughly their UTC offset.
- `mcp__openstory__daily_token_usage` — the per-day series → missing dates are
  absences; the token columns are the spend.
- `mcp__openstory__project_pulse` — project ids are filesystem paths → the
  categories, and the OS usernames baked into them.
- `mcp__openstory__list_sessions` — scope, and whether the store is federated.

In MCP-fallback mode, **skip section 5 entirely** — pulling raw message text
through MCP dumps it straight into the transcript, which is the thing this skill
exists to warn about.

If neither path works, OpenStory isn't running. Say so and tell the user to start
it (`brew services run openstoryarc/openstory/openstory`, or `just up-no-mongo`
from a source checkout) — don't guess numbers.

## Phase 2 — render

```
Exposure — last <N> days · <projects> projects · <sessions> sessions

Schedule     peak <HH>:00 UTC (<pct>%) · deadest <HH>:00 UTC
             sleep window <HH>–<HH> UTC → inferred <UTC±N>, e.g. <zones>
Absences     <count> gaps ≥2 days
             <from> .. <to>  (<n> days)
Spend        <tokens> tokens · <messages> messages · ~$<usd> (~$<usd>/active day)
Categories   <category>  <n> project(s)   <example path>
Identity     usernames visible in paths: <names>
Verbatim     <kept> of <total> messages, <chars> chars → <path>
```

Then one paragraph, in plain language, of what someone would conclude about this
person from the above — the sharpest single inference, named. Close with the line
the data earns: none of sections 1–4 required reading one line of a transcript.

Label the soft numbers as soft: cost is a blended-rate **estimate**; the timezone
is inferred from a sleep-hour assumption and carries a `confidence` field — say it
out loud, and don't assert a location when it's `low` (a night-owl schedule, a
short window, or a federated store all blur it); an absence only means "not at
this desk", not proof of a vacation.

## When NOT to use this skill

- **Secrets, keys, credentials before sharing** → `/openstory:scan`. That one
  hunts values that must never leave (and prints only `[REDACTED]`). This one
  hunts inferences a secret-scanner would pass clean — a store with zero secrets
  can still give away where you sleep and when your house was empty.
- Your spend as a budgeting question → `/openstory:cost`.
- Where your hours go as a productivity question → `/openstory:time`.
- Anything about another person → nothing here. Not this skill's job.
