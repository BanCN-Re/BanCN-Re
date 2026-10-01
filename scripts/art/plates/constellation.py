"""叁 · Constellation: a year of contributions as a star chart, redrawn daily by CI.

Each day is a star whose brightness follows that day's contributions; the
brightest are joined into constellations.  By day the chart becomes gold leaf
and cinnabar dots on paper.
"""

from __future__ import annotations

import datetime as dt
import math
import random

from .. import content as C
from .. import theme as T
from ..contributions import level, summarise
from ..svg import W, Doc, P, anim, background, frame, glow, gold_fill, section_header, sky, sparkle, text
from ..text import num
from ..theme import Theme

NEEDS_DATA = True

H = 576
CELL = 17.6
GRID_Y = 262
STATS_Y = 452


def _positions(data: dict | None):
    """[(x, y, date, count)] for every day; a blank year while waiting for data."""
    if data:
        weeks = data["weeks"]
    else:
        start = dt.date(2025, 1, 5)
        weeks = [[{"date": (start + dt.timedelta(days=w * 7 + d)).isoformat(), "weekday": d, "count": 0}
                  for d in range(7)] for w in range(53)]
    x0 = W / 2 - (len(weeks) - 1) * CELL / 2
    out = []
    for col, week in enumerate(weeks):
        for day in week:
            rnd = random.Random(day["date"])
            x = x0 + col * CELL + rnd.uniform(-3.4, 3.4)
            y = GRID_Y + day["weekday"] * CELL * 1.12 + rnd.uniform(-3.4, 3.4)
            out.append((x, y, day["date"], day["count"], col))
    return out, weeks, x0


def _links(stars):
    """Join bright stars into chains: greedy shortest edges, degree ≤ 2, no cycles."""
    pts = [(x, y) for x, y, lv in stars if lv >= 3]
    edges = []
    for i, (xa, ya) in enumerate(pts):
        for j in range(i + 1, len(pts)):
            xb, yb = pts[j]
            d = math.hypot(xa - xb, ya - yb)
            if d < CELL * 2.05:
                edges.append((d, i, j))
    edges.sort()
    parent = list(range(len(pts)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    degree = [0] * len(pts)
    chosen = []
    for d, i, j in edges:
        if degree[i] < 2 and degree[j] < 2 and root(i) != root(j):
            parent[root(i)] = root(j)
            degree[i] += 1
            degree[j] += 1
            chosen.append((pts[i], pts[j]))
    return chosen


def _month_labels(weeks, x0):
    labels, last_col = [], -9
    for col, week in enumerate(weeks):
        for day in week:
            d = dt.date.fromisoformat(day["date"])
            if d.day == 1 and col - last_col >= 3:
                labels.append((x0 + col * CELL, d.strftime("%b").upper()))
                last_col = col
                break
    return labels


def build(t: Theme, data: dict | None = None) -> str:
    stats = summarise(data) if data else None
    if stats:
        desc = (f"A star chart of {C.NAME}'s GitHub contributions: {stats['total']} contributions in the last year "
                f"over {stats['active']} active days; longest streak {stats['longest']} days, current streak {stats['current']} days.")
    else:
        desc = f"A star chart of {C.NAME}'s GitHub contributions, waiting for its first update."
    doc = Doc(t, H, "Constellation — 星图", desc)
    background(doc, W / 2, H * .5)
    sky(doc, 40, seed=51, avoid=[(80, 140, 1120, 520)], clear=[(250, 20, 950, 215), (80, 225, 1120, 405)],
        y_max=H - 40, twinkle_every=4, delay=.2)
    frame(doc)
    section_header(doc, "constellation", 66)
    doc.add(f'<g {anim("rise-s", 1.2, .9)}>'
            + text(T.italic(), C.CONSTELLATION_LINE, 22, W / 2, 174, fill=t.ink2)
            + text(T.song(), C.CONSTELLATION_LINE_ZH, 14, W / 2, 202, tracking=.3, fill=t.ink3) + "</g>")

    pos, weeks, x0 = _positions(data)
    thresholds = stats["thresholds"] if stats else (1, 1, 1)

    if data:  # month names above the chart
        labels = "".join(text(T.caps(), m, 11.5, x, GRID_Y - 24, anchor="start", tracking=.18, fill=t.ink3)
                         for x, m in _month_labels(weeks, x0))
        doc.add(f'<g {anim("fade", 1.4, 1.1)}>{labels}</g>')

    gl = glow(doc)
    hot = t.seal if not t.dark else t.speck
    cols: dict[int, list[str]] = {}
    bright = []
    rnd = random.Random(7)
    for x, y, date, count, col in pos:
        lv = level(count, thresholds)
        if lv == 0:
            el = f'<circle cx="{num(x)}" cy="{num(y)}" r=".95" fill="{t.speck if t.dark else t.ink3}" opacity="{.2 if t.dark else .28}"/>'
        elif lv == 1:
            el = f'<circle cx="{num(x)}" cy="{num(y)}" r="1.6" fill="{t.speck if t.dark else t.gold}" opacity=".62"/>'
        elif lv == 2:
            el = (f'<circle cx="{num(x)}" cy="{num(y)}" r="7" fill="{gl}"/>'
                  f'<circle cx="{num(x)}" cy="{num(y)}" r="2.2" fill="{t.speck if t.dark else t.gold}" opacity=".9"/>')
        else:
            r = 4.6 if lv == 3 else 6.4
            fill = (t.speck if t.dark else t.gold) if lv == 3 else hot
            el = (f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r * 2.2)}" fill="{gl}"/>' + P(sparkle(x, y, r), fill=fill))
            if lv == 4:
                el = f'<g style="animation:twinkle {rnd.uniform(3.5, 7):.1f}s ease-in-out {rnd.uniform(3, 9):.1f}s infinite">{el}</g>'
        if lv >= 2:
            bright.append((x, y, lv))
        cols.setdefault(col, []).append(el)
    for col, els in sorted(cols.items()):
        doc.add(f'<g {anim("fade", .9, 1.2 + col * .035)}>{"".join(els)}</g>')

    if not data:  # the first chart is drawn by CI; until then, say so
        mid = GRID_Y + 3 * CELL * 1.12
        veil = doc.define("veil", f'<radialGradient id="veil"><stop offset=".45" stop-color="{t.bg[1]}" stop-opacity=".95"/>'
                          f'<stop offset="1" stop-color="{t.bg[1]}" stop-opacity="0"/></radialGradient>')
        doc.add(f'<ellipse cx="{W / 2}" cy="{num(mid)}" rx="250" ry="48" fill="{veil}"/>'
                f'<g style="animation:twinkle 4s ease-in-out infinite">'
                + text(T.caps(), C.CHARTING, 15, W / 2, mid - 2, tracking=.42, fill=t.gold)
                + text(T.song(), C.CHARTING_ZH, 13, W / 2, mid + 24, tracking=.5, fill=t.ink3) + "</g>")

    # constellation lines draw themselves once the sky is lit
    links = _links(bright)
    if links:
        doc.style("@keyframes draw{from{stroke-dashoffset:1}}")
        ds = "".join(f'<path pathLength="1" d="M{num(a[0])} {num(a[1])}L{num(b[0])} {num(b[1])}" '
                     f'style="animation:draw 1.2s {3.2 + k * .012:.2f}s backwards"/>' for k, (a, b) in enumerate(links))
        doc.add(f'<g fill="none" stroke="{t.gold}" stroke-width=".8" stroke-dasharray="1" '
                f'opacity="{.42 if t.dark else .55}">{ds}</g>')

    # the four numbers beneath the chart
    xs = [W / 2 + (i - 1.5) * 232 for i in range(4)]
    gold = gold_fill(doc, STATS_Y - 36, STATS_Y + 4, "stat")
    parts = []
    for (key, en, zh), x in zip(C.STATS, xs):
        value = f"{stats[key]:,}" if stats else "—"
        parts.append(text(T.numerals(), value, 46, x, STATS_Y, fill=gold)
                     + text(T.caps(), en, 12, x, STATS_Y + 30, tracking=.26, fill=t.ink2)
                     + text(T.song(), zh, 12.5, x, STATS_Y + 52, tracking=.35, fill=t.ink3))
    seps = "".join(f'<path d="M{num((a + b) / 2)} {STATS_Y - 34}V{STATS_Y + 50}" stroke="{t.gold}" stroke-width=".7" opacity=".35"/>'
                   for a, b in zip(xs, xs[1:]))
    doc.add(f'<g {anim("rise-s", 1.3, 2.6)}>{seps}{"".join(parts)}</g>')

    if stats:
        first = dt.date.fromisoformat(stats["first"]).strftime("%b %Y").upper()
        last = dt.date.fromisoformat(stats["last"]).strftime("%b %Y").upper()
        charted = dt.date.fromisoformat(data["charted"])
        foot = f"{first} — {last}   ·   CHARTED {charted.day} {charted.strftime('%b %Y').upper()}"
    else:
        foot = "REDRAWN EVERY DAY BY GITHUB ACTIONS"
    doc.add(f'<g {anim("fade", 1.4, 3.2)}>' + text(T.caps(), foot, 11, W / 2, H - 42, tracking=.24, fill=t.ink3) + "</g>")
    return doc.render()
