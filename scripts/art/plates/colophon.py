"""跋 · Colophon: a farewell in running script, the name seal, and the sea-and-cliff hem."""

from __future__ import annotations

from .. import content as C
from .. import theme as T
from ..svg import W, Doc, anim, background, frame, gold_fill, rule, seal_name, sky, text
from ..text import num
from ..theme import Theme

H = 420
WAVE_TOP = 318
PERIOD = 56


def waves(doc: Doc) -> None:
    """海水江崖: rows of scalloped waves with a three-peaked cliff rising from them."""
    t = doc.t
    op_line = .7 if t.dark else .75
    rows = []
    for r in range(6):
        y = WAVE_TOP + r * 15
        shift = (r % 2) * PERIOD / 2
        x = x_start = -PERIOD * 2 + shift
        arcs, inner = [], []
        while x < W + PERIOD * 2:
            arcs.append(f"a{PERIOD / 2} 11 0 0 1 {PERIOD} 0")
            inner.append(f"M{num(x + PERIOD * .22)} {num(y)}a{num(PERIOD * .28)} 6 0 0 1 {num(PERIOD * .56)} 0")
            x += PERIOD
        outline = f"M{num(x_start)} {num(y)}" + "".join(arcs)
        body = outline + f"L{num(x)} {H}L{num(x_start)} {H}Z"
        fade = 1 - r * .1
        drift = "wave-l" if r % 2 else "wave-r"
        # bodies are filled with the page itself (slightly sheer so the paper grain survives)
        rows.append(f'<g style="animation:{drift} {16 + r * 2}s linear infinite">'
                    f'<path d="{body}" fill="url(#bg)" fill-opacity=".9"/>'
                    f'<path d="{outline}" fill="none" stroke="{t.gold}" stroke-width="1.1" opacity="{num(op_line * fade)}"/>'
                    f'<path d="{"".join(inner)}" fill="none" stroke="{t.gold}" stroke-width=".7" opacity="{num(op_line * fade * .6)}"/></g>')
    doc.style(f"@keyframes wave-r{{to{{transform:translateX({PERIOD}px)}}}}@keyframes wave-l{{to{{transform:translateX(-{PERIOD}px)}}}}")

    # the cliff: pointed peaks drawn as nested outlines, the middle one tallest
    cx, base = W / 2, H + 4
    rocks = []
    for dx, top, half in ((-64, WAVE_TOP - 22, 40), (64, WAVE_TOP - 18, 38), (0, WAVE_TOP - 64, 48)):
        x = cx + dx
        layers = []
        for k, inset in enumerate((0, .3, .58)):
            hh = half * (1 - inset)
            tt = top + (base - top) * inset * .62
            d = (f"M{num(x - hh)} {num(base)}C{num(x - hh * .82)} {num(tt + 46)} {num(x - 5)} {num(tt + 9)} {num(x)} {num(tt)}"
                 f"C{num(x + 5)} {num(tt + 9)} {num(x + hh * .82)} {num(tt + 46)} {num(x + hh)} {num(base)}")
            if k == 0:
                layers.append(f'<path d="{d}Z" fill="url(#bg)" stroke="{t.gold}" stroke-width="1.3"/>')
            else:
                layers.append(f'<path d="{d}" fill="none" stroke="{t.gold}" stroke-width=".8" opacity="{.7 - k * .15}"/>')
        rocks.append("".join(layers))
    cliff = f'<g {anim("rise", 2.2, .8)}>{"".join(rocks)}</g>'
    doc.add(f'<g clip-path="url(#card)"><g {anim("rise-s", 2, .4)}>{"".join(rows[:3])}</g>{cliff}'
            f'<g {anim("rise-s", 2, .4)}>{"".join(rows[3:])}</g></g>')


def build(t: Theme) -> str:
    doc = Doc(t, H, "Colophon — 后会有期", f"{C.FAREWELL} — {C.FAREWELL_EN} {C.COLOPHON.title()}")
    background(doc, W / 2, H * .4)
    sky(doc, 44, seed=77, clear=[(220, 30, 980, 290)], y_max=300, twinkle_every=3, delay=.2)
    waves(doc)
    frame(doc)

    # the farewell, written in running script and signed with the name seal
    fy = 116
    brush = T.cursive().shape(C.FAREWELL, 56, .04)
    seal_size = 50
    total = brush.width + 34 + seal_size
    x0 = W / 2 - total / 2
    gold = gold_fill(doc, fy - 50, fy + 8, "farewell")
    glyphs = brush.glyph_ds(x0, fy)
    doc.add(f'<g fill="{gold}">' + "".join(f'<path {anim("rise-s", 1.2, .6 + i * .14)} d="{d}"/>'
                                           for i, (d, *_r) in enumerate(glyphs)) + "</g>")
    sx, sy = x0 + brush.width + 34 + seal_size / 2, fy - 18
    doc.style("@keyframes stamp{0%{opacity:0;transform:scale(1.6) rotate(-7deg)}55%{opacity:1;transform:scale(.95) rotate(0)}75%{transform:scale(1.02)}}")
    doc.add(f'<g class="fb" style="animation:stamp .9s 2.2s backwards cubic-bezier(.3,.6,.2,1)">'
            f'{seal_name(doc, C.NAME_SEAL, sx, sy, seal_size)}</g>')

    doc.add(f'<g {anim("rise-s", 1.3, 1.9)}>' + text(T.italic(), C.FAREWELL_EN, 23, W / 2, 168, fill=t.ink2) + "</g>")
    rule(doc, 204, 150, delay=2.3)
    doc.add(f'<g {anim("fade", 1.4, 2.8)}>' + text(T.caps(), C.COLOPHON, 10.5, W / 2, 246, tracking=.2, fill=t.ink3) + "</g>")
    return doc.render()
