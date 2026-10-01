"""贰 · Toolkit: the Analects on tools, and a row of struck-gold medallions."""

from __future__ import annotations

import math

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

from .. import content as C
from .. import theme as T
from ..icons import ICONS
from ..svg import W, Doc, P, anim, background, diamond, frame, gold_fill, section_header, sky, text
from ..text import num
from ..theme import Theme

H = 540
CY = 356
R = 60
GAP = 196


def icon_d(name: str, cx: float, cy: float, box: float) -> tuple[str, bool]:
    """The mark scaled to fit `box` and centred on (cx, cy)."""
    _, evenodd, ds = ICONS[name]
    bp = BoundsPen(None)
    for d in ds:
        parse_path(d, bp)
    x0, y0, x1, y1 = bp.bounds
    s = box / max(x1 - x0, y1 - y0)
    tx = cx - (x0 + x1) / 2 * s
    ty = cy - (y0 + y1) / 2 * s
    pen = SVGPathPen(None, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    for d in ds:
        parse_path(d, TransformPen(pen, (s, 0, 0, s, tx, ty)))
    return pen.getCommands(), evenodd


def medallion(doc: Doc, i: int, name: str, cx: float, delay: float) -> str:
    t = doc.t
    face_id = f"coin-{i}"
    if t.dark:
        stops = '<stop offset="0" stop-color="#1e2840"/><stop offset=".7" stop-color="#121a2a"/><stop offset="1" stop-color="#0b101a"/>'
    else:
        stops = '<stop offset="0" stop-color="#fffdf6"/><stop offset=".7" stop-color="#f6eedb"/><stop offset="1" stop-color="#e9dcbd"/>'
    face = doc.define("coin", f'<radialGradient id="coin" cx=".4" cy=".35" r=".75">{stops}</radialGradient>')
    rim = gold_fill(doc, CY - R, CY + R, "rim")
    ticks = []
    for k in range(96):
        a = math.tau * k / 96
        ticks.append(f"M{num(cx + math.cos(a) * (R - 7.5))} {num(CY + math.sin(a) * (R - 7.5))}"
                     f"L{num(cx + math.cos(a) * (R - 4))} {num(CY + math.sin(a) * (R - 4))}")
    box = {"java": 66, "mysql": 66}.get(name, 46)
    d, evenodd = icon_d(name, cx, CY, box)
    mark = gold_fill(doc, CY - box / 2, CY + box / 2, "mark")
    doc.define(face_id, f'<clipPath id="{face_id}"><circle cx="{num(cx)}" cy="{CY}" r="{R}"/></clipPath>')
    shine = "#fff8e6"
    doc.define("coin-glint", f'<linearGradient id="coin-glint" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{shine}" stop-opacity="0"/>'
               f'<stop offset=".5" stop-color="{shine}" stop-opacity="{.22 if t.dark else .55}"/><stop offset="1" stop-color="{shine}" stop-opacity="0"/></linearGradient>')
    doc.style(f"@keyframes coin-glint{{0%{{transform:translateX(0)}}18%,100%{{transform:translateX({2 * R + 120}px)}}}}")
    return (
        f'<g class="fb" {anim("grow", 1.1, delay)}>'
        f'<circle cx="{num(cx)}" cy="{CY}" r="{R}" fill="{face}"/>'
        f'<circle cx="{num(cx)}" cy="{CY}" r="{R - .7}" fill="none" stroke="{rim}" stroke-width="1.6"/>'
        f'<g style="transform-origin:{num(cx)}px {CY}px;animation:spin 120s linear infinite">'
        f'<path d="{"".join(ticks)}" stroke="{t.gold}" stroke-width=".9" opacity="{.55 if t.dark else .6}"/></g>'
        f'<circle cx="{num(cx)}" cy="{CY}" r="{R - 11}" fill="none" stroke="{t.gold}" stroke-width=".6" opacity=".45"/>'
        + P(d, fill=mark, fill_rule="evenodd" if evenodd else None)
        + f'<g clip-path="url(#{face_id})"><g transform="skewX(-22)">'
        f'<rect x="{num(cx - R - 60 + (CY * math.tan(math.radians(22))))}" y="{CY - R}" width="60" height="{2 * R}" fill="url(#coin-glint)" '
        f'style="animation:coin-glint 8s ease-in-out {delay + 2.2 + i * .35:.2f}s infinite;transform:translateX(0)"/></g></g>'
        f'</g>')


def build(t: Theme) -> str:
    doc = Doc(t, H, "Toolkit — 利器",
              f"{C.TOOLKIT_QUOTE} {C.TOOLKIT_QUOTE_EN} Tools: " + ", ".join(f"{n.title()} ({r})" for _, n, r in C.TOOLS) + ".")
    background(doc, W / 2, H * .5)
    sky(doc, 52, seed=33, avoid=[(120, 150, 1080, 500)], clear=[(250, 20, 950, 270)], y_max=H - 40, twinkle_every=4, delay=.2)
    frame(doc)
    section_header(doc, "toolkit", 66)

    doc.add(f'<g {anim("rise-s", 1.3, .9)}>'
            + text(T.song_bold(), C.TOOLKIT_QUOTE, 25, W / 2, 190, tracking=.32, fill=t.ink) + "</g>")
    doc.add(f'<g {anim("rise-s", 1.3, 1.2)}>'
            + text(T.italic(), C.TOOLKIT_QUOTE_EN, 20, W / 2, 224, fill=t.ink2)
            + text(T.song(), C.TOOLKIT_SOURCE, 13.5, W / 2, 252, tracking=.18, fill=t.ink3) + "</g>")

    n = len(C.TOOLS)
    xs = [W / 2 + (i - (n - 1) / 2) * GAP for i in range(n)]
    # the string the medallions hang on
    op = ".35" if t.dark else ".45"
    beads = "".join(diamond((a + b) / 2, CY, 4.2, t.gold, op) for a, b in zip(xs, xs[1:]))
    doc.add(f'<g {anim("fade", 1.6, 1.0)}>'
            f'<path d="M{num(xs[0] - GAP * .62)} {CY}H{num(xs[-1] + GAP * .62)}" stroke="{t.gold}" stroke-width=".8" opacity="{op}"/>'
            f'{beads}{diamond(xs[0] - GAP * .62 - 6, CY, 3.5, t.gold, op)}{diamond(xs[-1] + GAP * .62 + 6, CY, 3.5, t.gold, op)}</g>')
    for i, ((key, label, role), x) in enumerate(zip(C.TOOLS, xs)):
        delay = 1.3 + i * .16
        doc.add(medallion(doc, i, key, x, delay))
        doc.add(f'<g {anim("rise-s", 1.1, delay + .35)}>'
                + text(T.caps(), label, 15.5, x, CY + R + 40, tracking=.3, fill=t.ink)
                + text(T.italic(), role, 18, x, CY + R + 66, fill=t.ink3) + "</g>")
    return doc.render()
