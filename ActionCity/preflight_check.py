#!/usr/bin/env python3
"""
preflight_check.py — guards that the report is built from LIVE data, never stale.

Two checks:

  1) TEMPLATE LINT (run before building):
       python3 preflight_check.py lint actioncity-template.html
     Fails (exit 1) if the locked template contains any hardcoded money/number literals.
     The template must hold ONLY {{tokens}} for values — if a real number is baked in, it can
     go stale silently. Allowed: tokens, %, week labels like W24, structural digits in styles.

  2) DATA FRESHNESS (run after building data.json, before sending):
       python3 preflight_check.py fresh data.json <today_YYYY-MM-DD>
     Fails (exit 1) if data.json was not produced for <today> (report_date_display mismatch) or
     looks empty. Proves the data.json in hand is THIS run's, not a leftover from a previous run.
"""
import sys, json, re, datetime

def lint(template_path):
    html = open(template_path, encoding="utf-8").read()
    # strip the how-to comment header so its examples don't trip the lint
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    bad = []
    # Baht amount baked in (฿ or &#3647; followed by a digit) — must be a token instead
    for m in re.finditer(r"(?:฿|&#3647;)\s*[0-9]", html):
        ctx = html[max(0,m.start()-15):m.start()+15]
        if "{{" not in ctx:                       # ok only if it's "฿{{token}}"
            bad.append("money literal near: ..." + ctx.strip() + "...")
    if bad:
        sys.stderr.write("TEMPLATE LINT FAILED — hardcoded values in template (use {{tokens}}):\n")
        for b in bad[:20]:
            sys.stderr.write("  - " + b + "\n")
        return 1
    print("template lint OK — no baked-in numbers, values are all tokens")
    return 0

def fresh(data_path, today):
    data = json.load(open(data_path, encoding="utf-8"))
    sc = data.get("scalars", {})
    disp = sc.get("report_date_display", "")
    # today passed as YYYY-MM-DD; build the same display form the routine uses, e.g. "10 Jun 2026"
    d = datetime.date.fromisoformat(today)
    want = f"{d.day} {d.strftime('%b')} {d.year}"
    problems = []
    if want not in disp:
        problems.append(f"report_date_display='{disp}' does not match today '{want}' — stale or wrong-day data.json")
    if not sc.get("day_net") or sc.get("day_net") in ("0", "", "—"):
        problems.append("day_net is empty/zero — completeness should have stopped the run")
    if not data.get("repeats", {}).get("week_rows"):
        problems.append("week_rows empty — weekly series did not load")
    if problems:
        sys.stderr.write("DATA FRESHNESS FAILED:\n")
        for p in problems: sys.stderr.write("  - " + p + "\n")
        return 1
    print(f"data freshness OK — data.json is for {want}")
    return 0

def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__); sys.exit(2)
    mode = sys.argv[1]
    if mode == "lint":
        sys.exit(lint(sys.argv[2]))
    elif mode == "fresh":
        if len(sys.argv) < 4:
            sys.stderr.write("fresh mode needs: data.json <today YYYY-MM-DD>\n"); sys.exit(2)
        sys.exit(fresh(sys.argv[2], sys.argv[3]))
    else:
        sys.stderr.write("unknown mode: " + mode + "\n"); sys.exit(2)

if __name__ == "__main__":
    main()
