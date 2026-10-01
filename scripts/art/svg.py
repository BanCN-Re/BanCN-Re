"""Shared drawing vocabulary: documents, frames, rules, seals, stars, mountains."""

from __future__ import annotations

import math
import random
import re
from html import escape

from . import theme as T
from .content import SECTIONS
from .text import num
from .theme import Theme

W = 1200            # every plate shares this width
FRAME = 14          # outer hairline inset
FRAME2 = 21         # inner hairline inset
RADIUS = 22


class Doc:
    """Collects defs, CSS and body markup for one SVG plate."""

    def __init__(self, t: Theme, height: int, title: str, desc: str):
        self.t, self.h, self.title, self.desc = t, height, title, desc
        self.defs: list[str] = []
        self.css: list[str] = []
        self.body: list[str] = []
        self._ids: set[str] = set()

    def add(self, *markup: str) -> None:
        self.body.extend(markup)

    def define(self, id_: str, markup: str) -> str:
        if id_ not in self._ids:
            self._ids.add(id_)
            self.defs.append(markup)
        return f"url(#{id_})"

    def style(self, css: str) -> None:
        if css not in self.css:
            self.css.append(css)

    def render(self) -> str:
        css = BASE_CSS + "\n".join(self.css)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{self.h}" viewBox="0 0 {W} {self.h}" '
            f'role="img" aria-labelledby="t d">\n'
            f'<title id="t">{escape(self.title)}</title>\n<desc id="d">{escape(self.desc)}</desc>\n'
            f"<style>{css}</style>\n<defs>{''.join(self.defs)}</defs>\n" + "\n".join(self.body) + "\n</svg>\n"
        )


# Every entrance animation fills "backwards": the resting style is the final
# frame, so viewers who prefer reduced motion simply see the finished plate.
BASE_CSS = """
.fb{transform-box:fill-box;transform-origin:center}
@keyframes fade{from{opacity:0}}
@keyframes rise{from{opacity:0;transform:translateY(14px)}}
@keyframes rise-s{from{opacity:0;transform:translateY(6px)}}
@keyframes grow{from{opacity:0;transform:scale(.86)}}
@keyframes unfold{from{transform:scaleX(0)}}
@keyframes twinkle{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes spin-r{to{transform:rotate(-360deg)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def anim(name: str, dur: float, delay: float = 0.0) -> str:
    """Inline entrance animation; `backwards` hides the element until its delay has passed."""
    return f'style="animation:{name} {dur:g}s cubic-bezier(.2,.7,.2,1) {delay:.2f}s backwards"'


def P(d: str, **attrs) -> str:
    return f'<path d="{d}"{_attrs(attrs)}/>'


def _attrs(attrs: dict) -> str:
    return "".join(f' {k.rstrip("_").replace("_", "-")}="{v}"' for k, v in attrs.items() if v is not None)


# ── colour ────────────────────────────────────────────────────────────────

def gold_fill(doc: Doc, y0: float, y1: float, key: str = "") -> str:
    """Metallic gold, banded top→bottom across y0..y1 (user space)."""
    r = doc.t.gold_ramp
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in zip((0, .38, .55, .78, 1), r))
    id_ = f"gold-{key or int(y0)}-{int(y1)}"
    return doc.define(id_, f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" x1="0" y1="{num(y0)}" x2="0" y2="{num(y1)}">{stops}</linearGradient>')


def background(doc: Doc, cx: float = W / 2, cy: float | None = None) -> None:
    t, h = doc.t, doc.h
    cy = h * 0.42 if cy is None else cy
    bg = doc.define("bg", f'<radialGradient id="bg" gradientUnits="userSpaceOnUse" cx="{num(cx)}" cy="{num(cy)}" r="{num(W * 0.62)}">'
                    f'<stop offset="0" stop-color="{t.bg[0]}"/><stop offset=".55" stop-color="{t.bg[1]}"/>'
                    f'<stop offset="1" stop-color="{t.bg[2]}"/></radialGradient>')
    doc.define("card", f'<clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="{RADIUS}"/></clipPath>')
    doc.add(f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="{RADIUS}" fill="{bg}"/>')
    if t.dark:
        grain = doc.define("grain", '<filter id="grain" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
                           '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="4"/>'
                           '<feColorMatrix values="0 0 0 0 1  0 0 0 0 .95  0 0 0 0 .85  0 0 0 .07 0"/></filter>')
    else:
        # xuan paper: soft cloudy fibre plus fine grain
        grain = doc.define("grain", '<filter id="grain" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
                           '<feTurbulence type="fractalNoise" baseFrequency=".012 .05" numOctaves="3" seed="9" result="c"/>'
                           '<feColorMatrix in="c" values="0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .3  0 0 0 .15 -.04" result="cloud"/>'
                           '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="2" result="g"/>'
                           '<feColorMatrix in="g" values="0 0 0 0 .4  0 0 0 0 .32  0 0 0 0 .2  0 0 0 .11 0" result="fine"/>'
                           '<feMerge><feMergeNode in="cloud"/><feMergeNode in="fine"/></feMerge></filter>')
    doc.add(f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="{RADIUS}" filter="{grain}"/>')
    if not t.dark:
        fibres(doc)


def fibres(doc: Doc, n: int = 70, seed: int = 11) -> None:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(30, W - 30), rnd.uniform(30, doc.h - 30)
        a = rnd.uniform(0, math.pi)
        L = rnd.uniform(8, 30)
        dx, dy = math.cos(a) * L, math.sin(a) * L
        bx, by = rnd.uniform(-6, 6), rnd.uniform(-6, 6)
        out.append(f"M{num(x)} {num(y)}q{num(dx / 2 + bx)} {num(dy / 2 + by)} {num(dx)} {num(dy)}")
    doc.add(P("".join(out), fill="none", stroke="#8a7a5c", stroke_width=".5", opacity=".22"))


# ── frame ─────────────────────────────────────────────────────────────────

def meander(size: float = 40) -> str:
    """Top-left 回纹 corner key, drawn in a size×size box."""
    key = "M0 40V0H40M7 40V7H40M14 30V14H30V25H20V20"
    return re.sub(r"\d+", lambda m: num(int(m.group()) * size / 40), key)


def frame(doc: Doc, delay: float = 0.0) -> None:
    t, h = doc.t, doc.h
    g = t.gold
    a1, a2 = (".55", ".25") if t.dark else (".7", ".32")
    gap = 26  # break in the outer line for the top/bottom ornaments
    cx = W / 2
    x0, y0, x1, y1 = FRAME, FRAME, W - FRAME, h - FRAME
    r = RADIUS - FRAME + 6
    outer = (f"M{cx - gap} {y0}H{x0 + r}A{r} {r} 0 0 0 {x0} {y0 + r}V{y1 - r}A{r} {r} 0 0 0 {x0 + r} {y1}H{cx - gap}"
             f"M{cx + gap} {y1}H{x1 - r}A{r} {r} 0 0 0 {x1} {y1 - r}V{y0 + r}A{r} {r} 0 0 0 {x1 - r} {y0}H{cx + gap}")
    inner = f"M{FRAME2} {FRAME2}H{W - FRAME2}V{h - FRAME2}H{FRAME2}Z"
    m = meander(34)
    corners = "".join(
        f'<path d="{m}" transform="translate({x} {y}) scale({sx} {sy})"/>'
        for x, y, sx, sy in ((FRAME2 + 7, FRAME2 + 7, 1, 1), (W - FRAME2 - 7, FRAME2 + 7, -1, 1),
                             (FRAME2 + 7, h - FRAME2 - 7, 1, -1), (W - FRAME2 - 7, h - FRAME2 - 7, -1, -1)))
    doc.add(f'<g {anim("fade", 1.6, delay)} fill="none" stroke="{g}">'
            f'<path d="{outer}" stroke-width="1.2" opacity="{a1}"/>'
            f'<path d="{inner}" stroke-width=".7" opacity="{a2}"/>'
            f'<g stroke-width="1.3" stroke-linecap="square" opacity="{a1}">{corners}</g>'
            f'{diamond(cx, y0, 6, g, a1)}{diamond(cx, y1, 6, g, a1)}'
            f'<circle cx="{cx - 15}" cy="{y0}" r="1.6" fill="{g}" stroke="none" opacity="{a1}"/>'
            f'<circle cx="{cx + 15}" cy="{y0}" r="1.6" fill="{g}" stroke="none" opacity="{a1}"/>'
            f'<circle cx="{cx - 15}" cy="{y1}" r="1.6" fill="{g}" stroke="none" opacity="{a1}"/>'
            f'<circle cx="{cx + 15}" cy="{y1}" r="1.6" fill="{g}" stroke="none" opacity="{a1}"/>'
            f'</g>')


def diamond(x: float, y: float, r: float, fill: str, opacity: str = "1") -> str:
    return f'<path d="M{num(x)} {num(y - r)}L{num(x + r * .62)} {num(y)}L{num(x)} {num(y + r)}L{num(x - r * .62)} {num(y)}Z" fill="{fill}" stroke="none" opacity="{opacity}"/>'


def rule(doc: Doc, y: float, half: float, inner: float = 16, delay: float = 0.0, opacity: str | None = None) -> None:
    """A hairline that unfolds from a central diamond."""
    t = doc.t
    op = opacity or (".75" if t.dark else ".85")
    cx = W / 2
    doc.style(".ur{transform-box:fill-box;transform-origin:right center}.ul{transform-box:fill-box;transform-origin:left center}")
    doc.add(
        f'<g fill="none">'
        f'<path class="ur" {anim("unfold", 1.4, delay)} d="M{num(cx - inner)} {num(y)}H{num(cx - half)}" stroke="{t.gold}" stroke-width="1" opacity="{op}"/>'
        f'<path class="ul" {anim("unfold", 1.4, delay)} d="M{num(cx + inner)} {num(y)}H{num(cx + half)}" stroke="{t.gold}" stroke-width="1" opacity="{op}"/>'
        f'<g class="fb" {anim("grow", .8, delay)}>{diamond(cx, y, 5.5, t.gold, op)}</g>'
        f'<circle {anim("fade", 1, delay + .9)} cx="{num(cx - half - 7)}" cy="{num(y)}" r="1.7" fill="{t.gold}" opacity="{op}"/>'
        f'<circle {anim("fade", 1, delay + .9)} cx="{num(cx + half + 7)}" cy="{num(y)}" r="1.7" fill="{t.gold}" opacity="{op}"/>'
        f'</g>')


# ── type helpers ──────────────────────────────────────────────────────────

def text(face, s: str, size: float, x: float, y: float, anchor: str = "middle", tracking: float = 0.0, **attrs) -> str:
    run = face.shape(s, size, tracking)
    return P(run.d(x, y, anchor), **attrs)


def letters(face, s: str, size: float, x: float, y: float, fill: str, anchor: str = "middle", tracking: float = 0.0,
            start: float = 0.0, step: float = 0.05, dur: float = 1.0, kind: str = "rise-s") -> str:
    """Text whose glyphs arrive one after another."""
    run = face.shape(s, size, tracking)
    out = []
    for i, (d, *_rest) in enumerate(run.glyph_ds(x, y, anchor)):
        out.append(f'<path {anim(kind, dur, start + i * step)} d="{d}"/>')
    return f'<g fill="{fill}">{"".join(out)}</g>'


def section_header(doc: Doc, key: str, y: float = 66, delay: float = 0.2) -> float:
    """Brush numeral between hairlines, then the bilingual title. Returns the next free y."""
    t = doc.t
    numeral, en, zh = SECTIONS[key]
    cx = W / 2
    gold = gold_fill(doc, y - 40, y + 12, "hdr")
    doc.add(f'<g class="fb" {anim("grow", 1.2, delay)}>' + text(T.brush(), numeral, 58, cx, y + 12, fill=gold) + "</g>")
    op = ".6" if t.dark else ".75"
    for sgn in (-1, 1):
        x0, x1 = cx + sgn * 52, cx + sgn * 250
        cls = "ur" if sgn < 0 else "ul"
        doc.add(f'<path class="{cls}" {anim("unfold", 1.4, delay + .3)} d="M{x0} {num(y - 8)}H{x1}" stroke="{t.gold}" stroke-width="1" opacity="{op}"/>'
                f'<g {anim("fade", 1, delay + 1.1)}>{diamond(x1 + sgn * 9, y - 8, 4.5, t.gold, op)}</g>')
    doc.style(".ur{transform-box:fill-box;transform-origin:right center}.ul{transform-box:fill-box;transform-origin:left center}")
    title_y = y + 62
    en_run = T.caps().shape(en, 19, .42)
    zh_run = T.song_bold().shape(zh, 19, .3)
    dot = 26
    total = en_run.width + dot * 2 + zh_run.width
    x = cx - total / 2
    doc.add(f'<g {anim("rise-s", 1.1, delay + .5)}>'
            + P(en_run.d(x, title_y), fill=t.ink)
            + f'<circle cx="{num(x + en_run.width + dot)}" cy="{num(title_y - 6.5)}" r="2" fill="{t.gold}"/>'
            + P(zh_run.d(x + en_run.width + dot * 2, title_y + 1), fill=t.ink2)
            + "</g>")
    return title_y


# ── seals ─────────────────────────────────────────────────────────────────

def seal_filter(doc: Doc) -> str:
    return doc.define("stone", '<filter id="stone" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">'
                      '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" result="n"/>'
                      '<feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" xChannelSelector="R" yChannelSelector="G" result="d"/>'
                      '<feTurbulence type="fractalNoise" baseFrequency=".22" numOctaves="3" seed="21" result="m"/>'
                      '<feColorMatrix in="m" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -16 0 0 0 11.2" result="holes"/>'
                      '<feComposite in="d" in2="holes" operator="in"/></filter>')


def seal_square(doc: Doc, chars: str, cx: float, cy: float, size: float, rotate: float = -3) -> str:
    """白文 seal: four characters carved out of a cinnabar block, read right column first."""
    t = doc.t
    flt = seal_filter(doc)
    s = size
    x0, y0 = cx - s / 2, cy - s / 2
    face = T.song_black()
    pad, gap = s * .1, s * .045
    cell = (s - 2 * pad - gap) / 2
    fs = cell * 1.1
    order = [(1, 0), (1, 1), (0, 0), (0, 1)]  # (col, row): right column top→bottom, then left
    glyphs = []
    for ch, (col, row) in zip(chars, order):
        gx = x0 + pad + col * (cell + gap) + cell / 2
        gy = y0 + pad + row * (cell + gap) + cell / 2 + fs * .36
        glyphs.append(P(face.shape(ch, fs).d(gx, gy, "middle"), fill=t.seal_text))
    block = (f'<rect x="{num(x0)}" y="{num(y0)}" width="{num(s)}" height="{num(s)}" rx="{num(s * .07)}" fill="{t.seal}"/>'
             + "".join(glyphs))
    return f'<g transform="rotate({rotate} {num(cx)} {num(cy)})" filter="{flt}">{block}</g>'


def seal_name(doc: Doc, rows: tuple[str, ...], cx: float, cy: float, size: float, rotate: float = 2) -> str:
    """朱文 seal: the name standing in relief inside a cinnabar border."""
    t = doc.t
    flt = seal_filter(doc)
    s = size
    x0, y0 = cx - s / 2, cy - s / 2
    face = T.display()
    inner = []
    fs = s * 0.34
    for i, row in enumerate(rows):
        y = y0 + s * (0.44 if i == 0 else 0.82)
        run = face.shape(row, fs, 0.06)
        k = min(1.0, (s * 0.78) / run.width)
        inner.append(f'<g transform="translate({num(cx)} {num(y)}) scale({num(k) if k < 1 else 1} 1) translate({num(-cx)} {num(-y)})">'
                     + P(run.d(cx, y, "middle"), fill=t.seal) + "</g>")
    border = (f'<rect x="{num(x0 + 2)}" y="{num(y0 + 2)}" width="{num(s - 4)}" height="{num(s - 4)}" rx="{num(s * .05)}" '
              f'fill="none" stroke="{t.seal}" stroke-width="{num(s * .07)}"/>')
    divider = f'<path d="M{num(x0 + s * .14)} {num(y0 + s * .55)}H{num(x0 + s * .86)}" stroke="{t.seal}" stroke-width="{num(s * .025)}"/>'
    return f'<g transform="rotate({rotate} {num(cx)} {num(cy)})" filter="{flt}">{border}{divider}{"".join(inner)}</g>'


# ── sky & paper ───────────────────────────────────────────────────────────

def sparkle(x: float, y: float, r: float) -> str:
    """Four-pointed star with concave sides."""
    k = r * 0.16
    return (f"M{num(x)} {num(y - r)}Q{num(x + k)} {num(y - k)} {num(x + r)} {num(y)}"
            f"Q{num(x + k)} {num(y + k)} {num(x)} {num(y + r)}Q{num(x - k)} {num(y + k)} {num(x - r)} {num(y)}"
            f"Q{num(x - k)} {num(y - k)} {num(x)} {num(y - r)}Z")


def fleck(rnd: random.Random, x: float, y: float, r: float) -> str:
    """An irregular flake of gold leaf."""
    n = rnd.choice((4, 5, 5, 6))
    rot = rnd.uniform(0, math.tau)
    pts = []
    for i in range(n):
        a = rot + i * math.tau / n + rnd.uniform(-.35, .35)
        rr = r * rnd.uniform(.45, 1.15)
        pts.append(f"{num(x + math.cos(a) * rr)} {num(y + math.sin(a) * rr)}")
    return "M" + "L".join(pts) + "Z"


def glow(doc: Doc) -> str:
    t = doc.t
    c = "#fff1c9" if t.dark else "#d9a441"
    return doc.define("glow", f'<radialGradient id="glow"><stop offset="0" stop-color="{c}" stop-opacity="{".55" if t.dark else ".35"}"/>'
                      f'<stop offset=".35" stop-color="{c}" stop-opacity="{".16" if t.dark else ".1"}"/>'
                      f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')


def sky(doc: Doc, n: int, seed: int, avoid=(), y_max: float | None = None, bright: list[tuple[float, float, float]] = (),
        twinkle_every: int = 5, delay: float = 0.0, clear=()) -> None:
    """Night: a field of stars.  Day: the same field as flecks of gold leaf on paper."""
    t = doc.t
    rnd = random.Random(seed)
    y_max = doc.h - 30 if y_max is None else y_max
    dim, twinkly = [], []
    pts = []
    while len(pts) < n:
        x, y = rnd.uniform(34, W - 34), rnd.uniform(34, y_max)
        r = rnd.random() ** 2.4
        if any(ax0 < x < ax1 and ay0 < y < ay1 for ax0, ay0, ax1, ay1 in avoid) and r > .25:
            continue
        if any(ax0 < x < ax1 and ay0 < y < ay1 for ax0, ay0, ax1, ay1 in clear):
            continue
        pts.append((x, y, r))
    for i, (x, y, r) in enumerate(pts):
        if t.dark:
            rad = .45 + r * 1.25
            op = .25 + r * .7
            el = f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(rad)}" opacity="{num(op)}"/>'
        else:
            size = 1.0 + r * 2.4 + (rnd.random() ** 6) * 4.5
            el = f'<path d="{fleck(rnd, x, y, size)}" opacity="{num(.5 + r * .45)}"/>'
        if i % twinkle_every == 0:
            dur = rnd.uniform(3.5, 7.5)
            twinkly.append(f'<g style="animation:twinkle {dur:.1f}s ease-in-out {rnd.uniform(0, 6) + delay:.1f}s infinite">{el}</g>')
        else:
            dim.append(el)
    fill = t.speck if t.dark else doc.define("leaf", '<linearGradient id="leaf" x1="0" y1="0" x2="1" y2="1">'
                                             '<stop offset="0" stop-color="#f1d58e"/><stop offset=".5" stop-color="#c79a3f"/>'
                                             '<stop offset="1" stop-color="#8f6420"/></linearGradient>')
    doc.add(f'<g {anim("fade", 2.4, delay)} fill="{fill}">{"".join(dim)}{"".join(twinkly)}</g>')
    if bright:
        g = glow(doc)
        out = []
        for i, (x, y, r) in enumerate(bright):
            star = f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r * 2.6)}" fill="{g}"/>' + P(sparkle(x, y, r), fill=t.speck if t.dark else t.gold)
            out.append(f'<g class="fb" style="animation:twinkle {5 + i * 1.3:.1f}s ease-in-out {delay + 1 + i * .7:.1f}s infinite">{star}</g>')
        doc.add(f'<g {anim("fade", 2, delay + .6)}>{"".join(out)}</g>')


def _noise(rnd: random.Random, n: int, rough: float) -> list[float]:
    """1-D midpoint displacement, n a power of two."""
    ys = [0.0] * (n + 1)
    span, amp = n, rough
    while span > 1:
        half = span // 2
        for i in range(half, n, span):
            ys[i] = (ys[i - half] + ys[i + half]) / 2 + rnd.uniform(-amp, amp)
        span, amp = half, amp * 0.58
    return ys


def smooth_path(pts: list[tuple[float, float]]) -> str:
    d = [f"M{num(pts[0][0])} {num(pts[0][1])}"]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        d.append(f"Q{num(xa)} {num(ya)} {num((xa + xb) / 2)} {num((ya + yb) / 2)}")
    d.append(f"L{num(pts[-1][0])} {num(pts[-1][1])}")
    return "".join(d)


# (x, height, half-width) of the summits in each layer, far → near
RANGES = (
    ((40, 170, 120), (205, 120, 95), (360, 58, 80), (560, 18, 120), (790, 46, 90), (960, 128, 110), (1150, 182, 120)),
    ((-10, 132, 130), (150, 98, 90), (300, 50, 85), (640, 12, 140), (880, 60, 95), (1060, 112, 100), (1220, 120, 110)),
    ((80, 84, 150), (250, 40, 90), (980, 44, 100), (1140, 92, 140)),
)


def mountains(doc: Doc, base_y: float, seed: int = 5, delay: float = 0.0, scale: float = 1.0) -> None:
    """Ink-wash ranges: summits at the edges, a misty valley in the middle."""
    t = doc.t
    h = doc.h
    rnd = random.Random(seed)
    if t.dark:
        tones = (("#1d2740", .95), ("#141c2d", .97), ("#0b0f19", 1))
    else:
        tones = (("#8f8470", .30), ("#6e6351", .42), ("#4a4236", .55))
    n = 256
    out = []
    for i, (peaks, (col, op)) in enumerate(zip(RANGES, tones)):
        ys = _noise(rnd, n, 30)
        pts = []
        for k in range(n + 1):
            x = W * k / n
            lift = max(H * math.exp(-((x - X) / hw) ** 2) for X, H, hw in peaks) * scale
            jag = ys[k] * (0.25 + 0.75 * min(1.0, lift / 90))
            pts.append((x, base_y + i * 16 - lift - jag * scale))
        d = smooth_path(pts) + f"L{W} {h}L0 {h}Z"
        top = min(y for _, y in pts)
        if t.dark:
            fill = col
        else:  # ink pooled at the ridge, washing out towards the foot
            gid = f"wash{i}"
            fill = doc.define(gid, f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{num(top)}" x2="0" y2="{num(base_y + i * 16 + 40)}">'
                              f'<stop offset="0" stop-color="{col}" stop-opacity="{op}"/><stop offset=".55" stop-color="{col}" stop-opacity="{num(op * .45)}"/>'
                              f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient>')
        out.append(P(d, fill=fill, opacity=str(op) if t.dark else None))
        if t.dark and i == 0:  # moonlight along the farthest ridge
            out.append(P(smooth_path(pts), fill="none", stroke=t.gold, stroke_width=".8", opacity=".22"))
        if i < len(RANGES) - 1:
            mid = doc.define(f"mist{i}", f'<linearGradient id="mist{i}" gradientUnits="userSpaceOnUse" x1="0" y1="{num(base_y - 60)}" x2="0" y2="{h}">'
                             f'<stop offset="0" stop-color="{t.bg[1]}" stop-opacity="0"/>'
                             f'<stop offset="1" stop-color="{t.bg[1]}" stop-opacity="{".5" if t.dark else ".7"}"/></linearGradient>')
            out.append(f'<rect x="0" y="{num(base_y - 200)}" width="{W}" height="{num(h - base_y + 200)}" fill="{mid}"/>')
    doc.add(f'<g clip-path="url(#card)" {anim("rise-s", 2.6, delay)}>{"".join(out)}</g>')


def moon(doc: Doc, x: float, y: float, r: float, delay: float = 0.0) -> None:
    """Night: a crescent moon.  Day: the red sun of ink paintings."""
    t = doc.t
    if t.dark:
        halo = doc.define("moonglow", '<radialGradient id="moonglow"><stop offset=".3" stop-color="#f6e6b8" stop-opacity=".22"/>'
                          '<stop offset="1" stop-color="#f6e6b8" stop-opacity="0"/></radialGradient>')
        doc.define("crescent", f'<mask id="crescent"><circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="#fff"/>'
                   f'<circle cx="{num(x + r * .42)}" cy="{num(y - r * .2)}" r="{num(r * .86)}" fill="#000"/></mask>')
        lit = doc.define("moonlit", '<linearGradient id="moonlit" x1="0" y1="0" x2="1" y2="1">'
                         '<stop offset="0" stop-color="#fff6da"/><stop offset="1" stop-color="#d9b46a"/></linearGradient>')
        body = (f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r * 3.2)}" fill="{halo}"/>'
                f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="{lit}" mask="url(#crescent)"/>')
    else:
        halo = doc.define("sunglow", f'<radialGradient id="sunglow"><stop offset=".35" stop-color="{t.seal}" stop-opacity=".16"/>'
                          f'<stop offset="1" stop-color="{t.seal}" stop-opacity="0"/></radialGradient>')
        body = (f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r * 2.4)}" fill="{halo}"/>'
                f'<circle cx="{num(x)}" cy="{num(y)}" r="{num(r)}" fill="{t.seal}" opacity=".82"/>')
    doc.add(f'<g {anim("fade", 3, delay)}>{body}</g>')
