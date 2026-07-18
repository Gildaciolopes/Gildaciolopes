#!/usr/bin/env python3
"""Fetch the public contribution calendar for a GitHub user. No token needed.

GitHub serves the calendar as public HTML at
    https://github.com/users/<username>/contributions
(the same fragment the profile page uses). Parse the day cells and write
data/contributions.json with raw days + derived stats.

Username resolution order: $GH_USERNAME env, argv[1], else the default below.
"""
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

DEFAULT_USER = "Gildaciolopes"
OUT = "data/contributions.json"
URL = "https://github.com/users/{user}/contributions"

# GitHub's level buckets on the tool cell -> our 0..4 (5 handled at render)
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch(user: str) -> list[dict]:
    r = requests.get(
        URL.format(user=user),
        headers={"User-Agent": "Mozilla/5.0 (profile-art)", "X-Requested-With": "XMLHttpRequest"},
        timeout=30,
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Real counts live in <tool-tip> text ("4 contributions on July 13th.",
    # "1 contribution on...", "No contributions on..."), matched to a day cell
    # by tool-tip[for] == td[id]. data-count is no longer on the cell.
    counts: dict[str, int] = {}
    for tip in soup.select("tool-tip"):
        cid = tip.get("for")
        if not cid:
            continue
        txt = tip.get_text(strip=True)
        m = re.match(r"(\d+)\s+contribution", txt)
        counts[cid] = int(m.group(1)) if m else 0

    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        date = cell.get("data-date")
        if not date:
            continue
        count = counts.get(cell.get("id"), 0)
        level = LEVELS.get((cell.get("data-level-name") or "").upper(), 0)
        if not level and cell.get("data-level"):
            level = int(cell.get("data-level"))
        days.append({"date": date, "count": count, "level": level})
    days.sort(key=lambda d: d["date"])
    return days


def derive(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}

    # streaks (consecutive days with count > 0, up to today)
    cur = longest = run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    # current streak = trailing run
    for d in reversed(days):
        if d["count"] > 0:
            cur += 1
        else:
            break

    months = OrderedDict()
    for d in days:
        m = d["date"][:7]
        months[m] = months.get(m, 0) + d["count"]

    return {
        "total": total,
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "months": months,
    }


def main() -> None:
    user = os.environ.get("GH_USERNAME") or (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER)
    print(f"[fetch] user: {user}")
    days = fetch(user)
    if not days:
        raise SystemExit("[fetch] no day cells found — GitHub markup may have changed")
    stats = derive(days)
    payload = {
        "user": user,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(payload, open(OUT, "w"), indent=2)
    print(f"[fetch] {len(days)} days, {stats['total']} contributions -> {OUT}")


if __name__ == "__main__":
    main()
