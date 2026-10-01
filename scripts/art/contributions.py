"""The contribution calendar, fetched from GitHub's GraphQL API."""

from __future__ import annotations

import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount } }
      }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": f"{login}-profile-constellation"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[{"date": d["date"], "weekday": d["weekday"], "count": d["contributionCount"]}
              for d in w["contributionDays"]] for w in cal["weeks"]]
    return {"login": login, "total": cal["totalContributions"], "weeks": weeks,
            "charted": dt.datetime.now(dt.timezone.utc).date().isoformat()}


def load(login: str, refresh: bool = False) -> dict | None:
    """Fresh data when asked (needs GITHUB_TOKEN), else the last saved chart, else None."""
    if refresh:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            raise SystemExit("--fetch needs GITHUB_TOKEN")
        data = fetch(login, token)
        DATA.parent.mkdir(exist_ok=True)
        DATA.write_text(json.dumps(data, separators=(",", ":")) + "\n")
        return data
    if DATA.exists():
        return json.loads(DATA.read_text())
    return None


def summarise(data: dict) -> dict:
    days = [d for w in data["weeks"] for d in w]
    counts = [d["count"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    # today's empty square doesn't break a streak until the day is over
    current = 0
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    for c in reversed(tail):
        if not c:
            break
        current += 1
    nonzero = sorted(c for c in counts if c)

    def q(p):
        return nonzero[min(len(nonzero) - 1, int(p * len(nonzero)))] if nonzero else 0

    return {
        "total": data["total"], "active": len(nonzero), "longest": longest, "current": current,
        "thresholds": (q(.25), q(.5), q(.8)),
        "first": days[0]["date"] if days else None, "last": days[-1]["date"] if days else None,
    }


def level(count: int, thresholds: tuple[int, int, int]) -> int:
    if count <= 0:
        return 0
    a, b, c = thresholds
    return 1 if count <= a else 2 if count <= b else 3 if count <= c else 4
