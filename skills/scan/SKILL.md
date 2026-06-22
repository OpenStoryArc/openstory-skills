---
name: scan
description: Scan your session history for anything sensitive before you share it — secrets, API keys, credentials, private details — and report a redacted summary. From your own OpenStory store. Use when the user asks "is there anything sensitive in my history", "scan before I share", "any secrets in my sessions", or "check my data before I export it".
---

# scan

A pre-share sovereignty check: surface likely exposures so the user can decide
what to scrub. **Never print an actual secret value — only categories, counts,
and `[REDACTED]`.** This is the one skill where leaking the thing you're scanning
for would be the whole failure.

## Phase 1 — look for exposures

Prefer a dedicated tool if it exists:

- `mcp__openstory__sensitivity_scan` — if available, use it. **May not exist yet**
  — if not, fall back to search below.

Fallback: search for known patterns with `mcp__openstory__search` (one query per
category) and count hits + sessions. Do **not** echo matched text — you only need
the counts:

- credentials: `password`, `secret`, `api_key`, `token`, `Bearer`
- key prefixes: `sk-`, `ghp_`, `AKIA`, `BEGIN PRIVATE KEY`
- personal: email addresses, private IPs

## Phase 2 — render (redacted)

```
Sensitivity scan — <scope>
Scanned <events> events across <sessions> sessions.

Category               Hits     Sessions   Severity
<category>             <count>   <count>    <Low/Medium/High>
...

Sample (redacted): <category> → [REDACTED]
Recommendation: <scrub these N sessions / safe to share>
```

Severity: credentials & key-prefixes = **High**; emails & private IPs = **Medium**;
file paths = **Low**. Print only counts and `[REDACTED]`, never a value.

> Note: search-based scanning is a heuristic (FTS misses some token shapes). A
> server-side regex sweep — the future `sensitivity_scan` MCP tool — is more
> thorough; until it ships, treat this as a first-pass safety net, not a guarantee.
