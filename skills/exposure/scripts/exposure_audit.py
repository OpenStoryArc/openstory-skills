#!/usr/bin/env python3
"""
exposure_audit.py — what a third-party profiler would learn from your history.

Read-only audit of YOUR OWN OpenStory store. It answers one question: if you
uploaded this history to someone else's server, what could they derive about you
that you never typed? Schedule, absences, burn rate, categories of your life —
and, on explicit request, the verbatim message text an uploader would carry off.

Scope, deliberately: this audits the store it is pointed at, which must be your
own. There is no flag to target a person, a host, or a teammate, and none will be
added. The point is to show you your own exposure, not to profile anyone.

Nothing is uploaded. Verbatim output is written to a local, git-ignored directory
and is never printed unless you pass --show.

Usage:
    python3 exposure_audit.py                       # sections 1-4 (metadata only)
    python3 exposure_audit.py --days 30
    python3 exposure_audit.py --json                # machine-readable, no verbatim
    python3 exposure_audit.py --verbatim            # + section 5 -> local ignored file
    python3 exposure_audit.py --verbatim --show     # + print it here (opt-in)
    python3 exposure_audit.py --test                # self-check, no network

Env: OPENSTORY_API_URL (default http://localhost:3002), OPENSTORY_API_TOKEN.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_API = os.environ.get("OPENSTORY_API_URL", "http://localhost:3002").rstrip("/")
OUT_DIR = ".openstory-exposure"

WORD_MIN = 15          # a "real" message, not an ack
TRUNC_PER_MSG = 2_000  # chars kept per message
MAX_MSGS = 50          # messages kept per session

# Categories of a life that leak from a project path alone — no transcript needed.
SENSITIVE = {
    "health": ["therapy", "medical", "health", "diagnosis", "clinic", "rehab"],
    "belief": ["religio", "faith", "philosoph", "church", "politic", "campaign"],
    "finance": ["financial", "tax", "invoice", "salary", "compensation", "budget", "payroll"],
    "job_search": ["resume", "cv-", "interview", "offer-letter", "job-search"],
    "travel": ["travel", "vacation", "trip", "flight", "itinerary"],
    "fundraising": ["a16z", "sequoia", "-yc-", "pitch", "deck", "investor", "-inc", "fundrais"],
    "relationship": ["family", "personal", "wedding", "-meeting"],
    "legal": ["legal", "lawsuit", "nda", "contract", "settlement"],
}

# Credentials are stripped even from the verbatim sample — /openstory:scan is the
# skill for hunting those. This skill hunts inferences, not keys.
SECRET_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "[REDACTED_ANTHROPIC_KEY]"),
    (re.compile(r"\bsk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{20,}"), "[REDACTED_OPENAI_KEY]"),
    (re.compile(r"\bAKIA[A-Z0-9]{16,}"), "[REDACTED_AWS_ACCESS_KEY]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\b([A-Z][A-Z0-9_]*?(?:SECRET|TOKEN|PASSWORD|CREDENTIAL|KEY)S?)\s*=\s*[^\s\"'\n,;.]+"), r"\1=[REDACTED]"),
]


class StoreUnreachable(Exception):
    """OpenStory isn't answering. Not an error to trace — an instruction to give."""


# ── fetch ─────────────────────────────────────────────────────────────────────

def get(path: str, api: str = DEFAULT_API):
    req = urllib.request.Request(f"{api}/api{path}")
    token = os.environ.get("OPENSTORY_API_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise StoreUnreachable(f"{api}/api{path}: {e}") from e


def rows_of(payload, *keys):
    """API responses are either a bare list or {key: [...]}"""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for k in keys:
            if isinstance(payload.get(k), list):
                return payload[k]
    return []


# ── 1. schedule ───────────────────────────────────────────────────────────────

def infer_schedule(hours: list[dict]) -> dict:
    """The contiguous low-activity window is when you are unconscious."""
    counts = {h["hour"]: h.get("event_count", 0) for h in hours}
    total = sum(counts.values()) or 1
    ranked = sorted(range(24), key=lambda h: counts.get(h, 0))
    quiet = set(ranked[:6])
    best, run = [], []
    for h in list(range(24)) * 2:            # wrap midnight
        if h in quiet:
            run.append(h)
            if len(run) > len(best):
                best = list(run)
        else:
            run = []
    best = best[:12]
    dead = ranked[0]
    quiet_share = 100 * sum(counts.get(h, 0) for h in quiet) / total
    return {
        "quiet_share_pct": round(quiet_share, 1),
        # a tight, genuinely dead window is a confident read; a diffuse one is not
        # (short windows, night-owl schedules, and federated stores all blur it)
        "confidence": "high" if quiet_share < 2 and len(best) >= 5
                      else "medium" if quiet_share < 8 else "low",
        "quiet_hours_utc": sorted(quiet),
        "sleep_window_utc": (best[0], best[-1]) if best else None,
        "deadest_hour_utc": dead,
        "deadest_share_pct": round(100 * counts.get(dead, 0) / total, 3),
        "peak_hour_utc": ranked[-1],
        "peak_share_pct": round(100 * counts.get(ranked[-1], 0) / total, 1),
        "timezone": infer_timezone(dead, (best[0], best[-1]) if best else None),
    }


def infer_timezone(deadest_hour_utc: int, sleep_window=None,
                   assumed_local_dead: int = 4) -> dict:
    """Hours come back in UTC. Assume a human's quietest stretch centers ~04:00
    local; the difference is your UTC offset — roughly where on earth you sleep.
    Prefer the middle of the whole quiet window (6 hours of signal) over the
    single deadest hour (1 hour, noisy on short windows)."""
    anchor = float(deadest_hour_utc)
    if sleep_window:
        lo, hi = sleep_window
        anchor = (lo + ((hi - lo) % 24) / 2) % 24
    offset = (assumed_local_dead - anchor) % 24
    if offset > 12:
        offset -= 24
    offset = int(round(offset))
    examples = {
        -8: "US Pacific (winter)", -7: "US Pacific (summer) / US Mountain",
        -6: "US Central", -5: "US Eastern (winter)", -4: "US Eastern (summer)",
        -3: "Brazil / Argentina", 0: "UK / Portugal", 1: "UK (summer) / Central Europe",
        2: "Central Europe (summer) / Israel", 3: "Moscow / East Africa",
        5: "Pakistan", 8: "China / Singapore", 9: "Japan / Korea",
        10: "East Australia", 12: "New Zealand",
    }
    return {
        "utc_offset": offset,
        "label": f"UTC{offset:+d}",
        "example_zones": examples.get(offset, "—"),
    }


# ── 2. absences ───────────────────────────────────────────────────────────────

def find_absences(days: list[dict], min_run: int = 2) -> list[tuple[str, str, int]]:
    """Consecutive missing dates = you were not at your desk."""
    seen = sorted({dt.date.fromisoformat(d["date"]) for d in days if d.get("date")})
    if not seen:
        return []
    gaps, cur = [], seen[0]
    for nxt in seen[1:]:
        missing = (nxt - cur).days - 1
        if missing >= min_run:
            gaps.append((
                (cur + dt.timedelta(days=1)).isoformat(),
                (nxt - dt.timedelta(days=1)).isoformat(),
                missing,
            ))
        cur = nxt
    return gaps


# ── 3. spend ──────────────────────────────────────────────────────────────────

def estimate_cost(days: list[dict]) -> dict:
    """Blended mid-tier rates, $/Mtok: in 3, out 15, cache-write 3.75, cache-read 0.30."""
    inp = sum(d.get("input_tokens", 0) for d in days)
    out = sum(d.get("output_tokens", 0) for d in days)
    cw = sum(d.get("cache_creation_tokens", 0) for d in days)
    cr = sum(d.get("cache_read_tokens", 0) for d in days)
    usd = (inp * 3 + out * 15 + cw * 3.75 + cr * 0.30) / 1_000_000
    active = len(days)
    return {
        "input": inp, "output": out, "cache_write": cw, "cache_read": cr,
        "total_tokens": inp + out + cw + cr,
        "messages": sum(d.get("message_count", 0) for d in days),
        "active_days": active,
        "est_usd": round(usd, 2),
        "est_usd_per_active_day": round(usd / active, 2) if active else 0.0,
    }


# ── 4. categories of life ─────────────────────────────────────────────────────

def classify(projects: list[dict]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for p in projects:
        pid = urllib.parse.unquote(p.get("project_id") or "").lower()
        for cat, needles in SENSITIVE.items():
            if any(n in pid for n in needles):
                hits.setdefault(cat, []).append(p.get("project_id"))
    return hits


def identities(projects: list[dict]) -> dict:
    """Project ids are filesystem paths. Filesystem paths carry usernames."""
    users = set()
    # real paths (/Users/alice/...) and Claude Code's dash-encoded form (-Users-alice-...)
    pats = (re.compile(r"/(?:Users|home)/([^/]+)"),
            re.compile(r"-(?:Users|home)-([A-Za-z0-9_.]+)"))
    for p in projects:
        pid = urllib.parse.unquote(p.get("project_id") or "")
        for pat in pats:
            for m in pat.finditer(pid):
                users.add(m.group(1))
    return {"os_users": sorted(users)}


# ── 5. verbatim ───────────────────────────────────────────────────────────────

def scrub(text: str) -> str:
    for pat, repl in SECRET_PATTERNS:
        text = pat.sub(repl, text)
    return text


def truncate(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 3] + "..."


def _content_of(payload) -> str:
    """OpenStory payloads arrive as dicts, JSON strings, or python-repr strings."""
    if isinstance(payload, str):
        for loader in (json.loads, ast.literal_eval):
            try:
                payload = loader(payload)
                break
            except Exception:
                continue
    if not isinstance(payload, dict):
        return str(payload)
    c = payload.get("content", payload.get("text", ""))
    if isinstance(c, list):
        c = " ".join(
            b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") != "tool_result"
        )
    return c if isinstance(c, str) else str(c)


def user_messages(records: list[dict]) -> list[str]:
    out = []
    for r in records:
        if r.get("record_type") != "user_message":
            continue
        txt = _content_of(r.get("payload"))
        # tool results are replayed as user_message rows; they aren't things you said
        if txt.strip() and not txt.lstrip().startswith(("[{", "tool_use_id")):
            out.append(txt.strip())
    return out


def build_sample(messages: list[str]) -> list[str]:
    """What an uploader takes: substantive messages, truncated, capped."""
    kept = [m for m in messages if len(m.split()) > WORD_MIN]
    return [scrub(truncate(m, TRUNC_PER_MSG)) for m in kept][:MAX_MSGS]


def verbatim_report(api: str, n_sessions: int, out_dir: str) -> dict:
    sess = rows_of(get("/sessions", api), "sessions")
    sess = [s for s in sess if s.get("session_id")]
    sess.sort(key=lambda s: s.get("last_event") or "", reverse=True)
    picked, blocks, stats = sess[:n_sessions], [], []
    for s in picked:
        sid = s["session_id"]
        recs = rows_of(get(f"/sessions/{sid}/records", api), "records", "data")
        msgs = user_messages(recs)
        sample = build_sample(msgs)
        stats.append({
            "session_id": sid,
            "project": s.get("project_name") or s.get("project_id"),
            "last_event": s.get("last_event"),
            "user_messages": len(msgs),
            "carried_off": len(sample),
            "chars": sum(len(m) for m in sample),
        })
        blocks.append(
            f"### session {sid}  ({s.get('project_name') or s.get('project_id')})\n"
            f"### {len(sample)} of {len(msgs)} user messages\n\n"
            + "\n---\n".join(sample)
        )
    body = (
        "# Verbatim preview — what an uploader would carry off\n"
        "# LOCAL ONLY. Credentials scrubbed; everything else is exactly what you typed.\n"
        f"# generated {dt.datetime.now().isoformat(timespec='seconds')}\n\n"
        + "\n\n".join(blocks)
    )
    path = write_local(body, out_dir)
    return {"path": path, "sessions": stats, "body": body,
            "total_chars": sum(s["chars"] for s in stats)}


def write_local(body: str, out_dir: str) -> str:
    """Write under a directory that ignores itself — never into git, never uploaded."""
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, ".gitignore"), "w") as f:
        f.write("*\n")  # ignore everything here, including this file
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(out_dir, f"verbatim-{stamp}.txt")
    with open(path, "w") as f:
        f.write(body)
    return path


# ── report ────────────────────────────────────────────────────────────────────

def collect(api: str, days: int) -> dict:
    hours = get(f"/insights/productivity?days={days}", api)
    daily = get(f"/insights/token-usage/daily?days={days}", api)
    pulse = get(f"/insights/pulse?days={days}", api)
    hours = rows_of(hours, "hours") or hours
    daily = rows_of(daily, "days") or daily
    pulse = rows_of(pulse, "projects") or pulse
    return {
        "window_days": days,
        "schedule": infer_schedule(hours),
        "absences": [{"from": a, "to": b, "days": n} for a, b, n in find_absences(daily)],
        "spend": estimate_cost(daily),
        "categories": classify(pulse),
        "identities": identities(pulse),
        "scope": {
            "projects": len(pulse),
            "sessions": sum(p.get("session_count", 0) for p in pulse),
        },
    }


def render(r: dict) -> None:
    s, sp = r["schedule"], r["spend"]
    line = "=" * 70
    print(line)
    print(f"EXPOSURE — what your history reveals (last {r['window_days']} days)")
    print(line)

    print(f"\n[SCHEDULE]  peak {s['peak_hour_utc']:02d}:00 UTC ({s['peak_share_pct']}% of activity)")
    print(f"            deadest {s['deadest_hour_utc']:02d}:00 UTC ({s['deadest_share_pct']}%)")
    print(f"            inferred sleep window (UTC): {s['sleep_window_utc']}")
    tz = s["timezone"]
    print(f"            inferred timezone: {tz['label']} (±1h, confidence {s['confidence']})"
          f"  e.g. {tz['example_zones']}")
    print(f"            quiet window holds {s['quiet_share_pct']}% of all activity")
    print("            -> when you sleep, how long, and roughly where you are")

    print(f"\n[ABSENCES]  {len(r['absences'])} multi-day gaps:")
    for a in r["absences"][:12]:
        print(f"            {a['from']} .. {a['to']}  ({a['days']} days away)")
    if len(r["absences"]) > 12:
        print(f"            ... and {len(r['absences']) - 12} more")
    print("            -> vacations, illness, when your home was empty")

    print(f"\n[SPEND]     {sp['total_tokens']:,} tokens over {sp['active_days']} active days")
    print(f"            {sp['messages']:,} messages")
    print(f"            est. ${sp['est_usd']:,.2f} (~${sp['est_usd_per_active_day']:,.2f}/active day)")
    print("            -> your burn rate, your tooling budget, your seriousness")

    print("\n[CATEGORIES] project paths alone leak category-of-life:")
    cats = r["categories"]
    if not cats:
        print("            none matched — your path names give little away")
    for cat, paths in sorted(cats.items()):
        print(f"            {cat:12s} {len(paths)} project(s)")
        for p in paths[:4]:
            print(f"                         {urllib.parse.unquote(p)}")

    print(f"\n[IDENTITY]  OS usernames visible in paths: {r['identities']['os_users']}")
    print(f"[SCOPE]     {r['scope']['projects']} projects · {r['scope']['sessions']:,} sessions")
    print(line)
    print("None of the above required reading one line of a transcript.")


def render_verbatim(v: dict, show: bool) -> None:
    print("\n[VERBATIM]  a sample of what an uploader would carry off:")
    for s in v["sessions"]:
        print(f"            {s['carried_off']:>3} of {s['user_messages']:>4} messages "
              f"({s['chars']:,} chars)  {s['project']}")
    print(f"            total {v['total_chars']:,} chars written to {v['path']}")
    print("            (local only, git-ignored, never uploaded)")
    if show:
        print("\n" + "=" * 70)
        print("VERBATIM SAMPLE — this is your own words, in your own transcript now")
        print("=" * 70)
        print(v["body"])
    else:
        print("            re-run with --show to print it here (opt-in).")


# ── self-check ────────────────────────────────────────────────────────────────

def self_test() -> int:
    fails = []

    hours = [{"hour": h, "event_count": 100} for h in range(24)]
    for h in (3, 4, 5, 6, 7, 8):
        hours[h]["event_count"] = 1
    s = infer_schedule(hours)
    if s["sleep_window_utc"] != (3, 8):
        fails.append(f"sleep window: {s['sleep_window_utc']}")
    if s["deadest_hour_utc"] not in (3, 4, 5, 6, 7, 8):
        fails.append(f"deadest hour: {s['deadest_hour_utc']}")

    wrap = [{"hour": h, "event_count": 100} for h in range(24)]
    for h in (22, 23, 0, 1, 2, 3):
        wrap[h]["event_count"] = 0
    if infer_schedule(wrap)["sleep_window_utc"] != (22, 3):
        fails.append(f"midnight-wrapping sleep window: {infer_schedule(wrap)['sleep_window_utc']}")

    if infer_timezone(8)["utc_offset"] != -4:
        fails.append(f"tz offset for dead hour 08 UTC: {infer_timezone(8)}")
    if infer_timezone(4)["utc_offset"] != 0:
        fails.append("tz offset for dead hour 04 UTC should be 0")
    if infer_timezone(20)["utc_offset"] != 8:
        fails.append(f"tz offset for dead hour 20 UTC: {infer_timezone(20)}")
    # window midpoint wins over the single dead hour, and wraps midnight
    if infer_timezone(3, (6, 11))["utc_offset"] != -4:
        fails.append(f"tz from window (6,11): {infer_timezone(3, (6, 11))}")
    if infer_timezone(3, (22, 3))["utc_offset"] != 4:
        fails.append(f"tz from midnight-wrapping window (22,3): {infer_timezone(3, (22, 3))}")

    g = find_absences([{"date": "2026-07-01"}, {"date": "2026-07-02"}, {"date": "2026-07-10"}])
    if g != [("2026-07-03", "2026-07-09", 7)]:
        fails.append(f"absences: {g}")
    if find_absences([{"date": "2026-07-01"}, {"date": "2026-07-02"}]) != []:
        fails.append("contiguous days should show no gap")

    c = estimate_cost([{"input_tokens": 1_000_000, "output_tokens": 0,
                        "cache_creation_tokens": 0, "cache_read_tokens": 0}])
    if c["est_usd"] != 3.0 or c["est_usd_per_active_day"] != 3.0:
        fails.append(f"cost: {c}")

    cats = classify([{"project_id": "-Users-me-projects-therapy-notes"},
                     {"project_id": "%2FUsers%2Fme%2Fprojects%2Fmy-taxes"},
                     {"project_id": "-Users-me-projects-boring-app"}])
    if "health" not in cats or "finance" not in cats:
        fails.append(f"category classification: {cats}")
    if any("boring-app" in p for ps in cats.values() for p in ps):
        fails.append("benign project should not be classified")
    if identities([{"project_id": "-Users-alice-projects-x"}])["os_users"] != ["alice"]:
        fails.append("username extraction from path")

    # payload shapes: dict, JSON string, python-repr string, content blocks
    if _content_of({"content": "hi"}) != "hi":
        fails.append("dict payload")
    if _content_of('{"content": "hi"}') != "hi":
        fails.append("JSON-string payload")
    if _content_of("{'content': 'hi'}") != "hi":
        fails.append("python-repr payload")
    blocks = {"content": [{"type": "text", "text": "a"},
                          {"type": "tool_result", "text": "b"},
                          {"type": "text", "text": "c"}]}
    if _content_of(blocks) != "a c":
        fails.append(f"content blocks: {_content_of(blocks)!r}")
    if _content_of({"text": "fallback"}) != "fallback":
        fails.append("text-key fallback")

    long_ = " ".join(["word"] * 20)
    if build_sample(["too short"]) != []:
        fails.append("short message should be dropped")
    if build_sample([long_]) != [long_]:
        fails.append("long message should survive")
    big = " ".join(["w"] * 5000)
    if len(build_sample([big])[0]) != TRUNC_PER_MSG:
        fails.append("per-message truncate")
    if len(build_sample([big] * 60)) != MAX_MSGS:
        fails.append("message cap")
    if "AKIA" in build_sample(["my key is AKIA" + "B" * 16 + " " + long_])[0]:
        fails.append("aws key not scrubbed from verbatim sample")

    recs = [{"record_type": "user_message", "payload": {"content": long_}},
            {"record_type": "assistant_message", "payload": {"content": long_}},
            {"record_type": "user_message", "payload": {"content": "[{'tool_use_id': 'x'}]"}}]
    if user_messages(recs) != [long_]:
        fails.append(f"user_messages filtering: {user_messages(recs)}")

    if rows_of({"sessions": [1, 2]}, "sessions") != [1, 2]:
        fails.append("rows_of dict form")
    if rows_of([1, 2], "sessions") != [1, 2]:
        fails.append("rows_of list form")

    for f in fails:
        print("FAIL:", f)
    print("ok" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Audit YOUR OWN OpenStory store for what it reveals about you.")
    ap.add_argument("--api", default=DEFAULT_API,
                    help="your own OpenStory instance (default %(default)s)")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--verbatim", action="store_true",
                    help="also sample real message text (written to a local ignored file)")
    ap.add_argument("--sessions", type=int, default=3,
                    help="how many recent sessions to sample for --verbatim")
    ap.add_argument("--show", action="store_true",
                    help="print the verbatim sample here (opt-in; it lands in this transcript)")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--json", action="store_true", help="machine-readable; never verbatim")
    ap.add_argument("--test", action="store_true", help="self-check, no network")
    a = ap.parse_args()

    if a.test:
        return self_test()

    try:
        result = collect(a.api, a.days)
        if a.json:
            print(json.dumps(result, indent=2))
            return 0
        render(result)
        if a.verbatim:
            render_verbatim(verbatim_report(a.api, a.sessions, a.out_dir), a.show)
    except StoreUnreachable as e:
        print(f"OpenStory isn't answering at {a.api} ({e})", file=sys.stderr)
        print("Start it, then re-run:", file=sys.stderr)
        print("  brew services run openstoryarc/openstory/openstory", file=sys.stderr)
        print("  # or, from a source checkout:  just up-no-mongo", file=sys.stderr)
        print(f"  # remote/secured instance:    --api URL  or  OPENSTORY_API_URL=URL",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
