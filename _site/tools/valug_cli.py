#!/usr/bin/env python3
"""Update the VALUG weekly 4% reversal model and publish to GitHub Pages."""
from __future__ import annotations
import argparse, csv, subprocess, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "_data" / "valug.csv"
POSTS = ROOT / "_posts"

def calculate(rows):
    rows = sorted(rows, key=lambda r: r["date"])
    if not rows:
        raise ValueError("No observations found.")
    state = "BUY"  # Explicit initialization assumption for 2025-10-31.
    extreme = rows[0]["close"]
    extreme_date = rows[0]["date"]
    events = []
    for row in rows:
        close = row["close"]
        if state == "BUY":
            if close > extreme:
                extreme, extreme_date = close, row["date"]
            trigger = extreme * 0.96
            if close <= trigger:
                state = "SELL"
                extreme, extreme_date = close, row["date"]
                events.append({"date": row["date"], "close": close, "signal": state})
        else:
            if close < extreme:
                extreme, extreme_date = close, row["date"]
            trigger = extreme * 1.04
            if close >= trigger:
                state = "BUY"
                extreme, extreme_date = close, row["date"]
                events.append({"date": row["date"], "close": close, "signal": state})
        row["signal"] = state
        row["extreme"] = extreme
        row["trigger"] = extreme * (0.96 if state == "BUY" else 1.04)
        row["extreme_date"] = extreme_date
    return rows, events

def main():
    p = argparse.ArgumentParser(description="Add a weekly VALUG close and update the signal history.")
    p.add_argument("close", type=float, help="Weekly closing value")
    p.add_argument("--date", required=True, help="Observation date, YYYY-MM-DD")
    p.add_argument("--dry-run", action="store_true", help="Calculate and preview without writing or publishing")
    p.add_argument("--no-push", action="store_true", help="Write files and commit locally, but do not push")
    args = p.parse_args()
    try:
        d = date.fromisoformat(args.date)
        if args.close <= 0:
            raise ValueError("Close must be greater than zero.")
        rows = []
        with DATA.open(newline="") as f:
            for r in csv.DictReader(f):
                rows.append({"date": r["date"], "close": float(r["close"])})
        if any(r["date"] == d.isoformat() for r in rows):
            raise ValueError(f"An observation already exists for {d.isoformat()}. No changes made.")
        if rows and d.isoformat() <= max(r["date"] for r in rows):
            raise ValueError("New observations must be later than the latest date. Correct historical data manually and rerun.")
        rows.append({"date": d.isoformat(), "close": round(args.close, 2)})
        rows, events = calculate(rows)
        latest = rows[-1]
        trigger = latest["trigger"]
        distance = abs(trigger - latest["close"])
        pct = distance / latest["close"] * 100
        prior = rows[-2]["close"] if len(rows) > 1 else latest["close"]
        change = latest["close"] - prior
        print(f'{d}: {latest["close"]:.2f} | {latest["signal"]}')
        print(f'Next {"SELL" if latest["signal"] == "BUY" else "BUY"} trigger: {trigger:.2f} ({distance:.2f} points / {pct:.2f}% away)')
        if args.dry_run:
            print("Dry run: no files changed.")
            return
        DATA.parent.mkdir(parents=True, exist_ok=True)
        with DATA.open("w", newline="") as f:
            w = csv.writer(f); w.writerow(["date", "close"])
            for r in rows: w.writerow([r["date"], f'{r["close"]:.2f}'])
        # Store derived values separately for the dashboard; recomputed from source CSV each run.
        derived = ROOT / "_data" / "valug_signals.json"
        public_data = ROOT / "assets" / "valug_signals.json"
        import json
        payload = json.dumps({
            "observations": [{"date":r["date"],"close":r["close"],"signal":r["signal"],
                              "extreme":round(r["extreme"],2),"trigger":round(r["trigger"],2)} for r in rows],
            "events": events
        }, indent=2) + "\n"
        derived.write_text(payload)
        public_data.parent.mkdir(parents=True, exist_ok=True)
        public_data.write_text(payload)
        event_text = "\n".join(f'- **{e["date"]} — {e["signal"]}** at {e["close"]:.2f}' for e in events)
        post = f'''---
layout: post
title: "VALUG Weekly Update — {d.isoformat()}"
date: {d.isoformat()} 16:00:00 -0400
categories: [VALUG]
---

## VALUG trend signal: {latest["signal"]}

**Weekly close:** {latest["close"]:.2f}  
**Weekly change:** {change:+.2f}  
**Next reversal trigger:** {trigger:.2f}  
**Distance to trigger:** {distance:.2f} points ({pct:.2f}%)

The model changes from BUY to SELL after a 4% decline from the highest weekly close since the BUY signal. It changes from SELL to BUY after a 4% rise from the lowest weekly close since the SELL signal.

### Signal history

{event_text}

[View the interactive VALUG dashboard]({{% raw %}}/valug/{{% endraw %}})
'''
        post_path = POSTS / f"{d.isoformat()}-valug-weekly-update.md"
        if post_path.exists():
            raise ValueError(f"Post already exists: {post_path.name}")
        post_path.write_text(post)
        subprocess.run(["git", "add", str(DATA.relative_to(ROOT)), str(derived.relative_to(ROOT)), str(public_data.relative_to(ROOT)), str(post_path.relative_to(ROOT))], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", f"Add VALUG weekly close {d.isoformat()}"], cwd=ROOT, check=True)
        if not args.no_push:
            subprocess.run(["git", "push"], cwd=ROOT, check=True)
            print("Published. GitHub Pages will rebuild the site.")
        else:
            print("Committed locally; not pushed.")
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    main()
