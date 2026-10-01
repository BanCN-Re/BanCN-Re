"""Frontispiece: greeting, name, astrolabe, mountains and the leisure seal."""

from __future__ import annotations

import math

from .. import content as C
from .. import theme as T
from ..svg import (W, Doc, P, anim, background, frame, glow, gold_fill, letters, moon, mountains, rule, seal_square,
                   sky, sparkle, text)
from ..text import num
from ..theme import Theme

H = 540
CX, CY = W / 2, 250


def astrolabe(doc: Doc, delay: float) -> None:
    t = doc.t
    R = 212
    g = t.gold
    ticks = []
    for i in range(120):
        a = math.radians(i * 3)
        r0 = R - (11 if i % 10 == 0 else 6 if i % 5 == 0 else 3.5)
        ticks.append(f"M{num(CX + math.sin(a) * r0)} {num(CY - math.cos(a) * r0)}L{num(CX + math.sin(a) * R)} {num(CY - math.cos(a) * R)}")
    branch_face = T.song_bold()
    rb = R - 32
    glyphs, dots = [], []
    for i, ch in enumerate(C.BRANCHES):
        a = i * 30
        rad = math.radians(a)
        x, y = CX + math.sin(rad) * rb, CY - math.cos(rad) * rb
        run = branch_face.shape(ch, 17)
        glyphs.append(f'<path transform="rotate({a} {num(x)} {num(y)})" d="{run.d(x, y + 6, "middle")}"/>')
        rad2 = math.radians(a + 15)
        dots.append(f'<circle cx="{num(CX + math.sin(rad2) * rb)}" cy="{num(CY - math.cos(rad2) * rb)}" r="1.4"/>')
    spokes = []
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        spokes.append(f"M{num(CX + math.sin(a) * 92)} {num(CY - math.cos(a) * 92)}L{num(CX + math.sin(a) * (R - 52))} {num(CY - math.cos(a) * (R - 52))}")
    op = ".5" if t.dark else ".42"
    doc.add(
        f'<g class="fb" {anim("grow", 2.6, delay)} opacity="{op}" fill="none" stroke="{g}">'
        f'<g style="transform-origin:{num(CX)}px {num(CY)}px;animation:spin 600s linear infinite">'
        f'<circle cx="{CX}" cy="{CY}" r="{R}" stroke-width="1.1"/>'
        f'<path d="{"".join(ticks)}" stroke-width=".8"/>'
        f'<circle cx="{CX}" cy="{CY}" r="{R - 14}" stroke-width=".6"/>'
        f'<g fill="{g}" stroke="none">{"".join(glyphs)}{"".join(dots)}</g>'
        f'<circle cx="{CX}" cy="{CY}" r="{R - 50}" stroke-width=".8"/>'
        f'</g>'
        f'<g style="transform-origin:{num(CX)}px {num(CY)}px;animation:spin-r 900s linear infinite">'
        f'<circle cx="{CX}" cy="{CY}" r="{R - 64}" stroke-width=".9" stroke-dasharray="1.5 6"/>'
        f'<path d="{"".join(spokes)}" stroke-width=".5" opacity=".7"/>'
        f'<circle cx="{CX}" cy="{CY}" r="92" stroke-width=".6"/>'
        f'</g></g>')


def orbits(doc: Doc, delay: float) -> None:
    t = doc.t
    gl = glow(doc)
    out = []
    for rx, ry, rot, dur, op, rev in ((338, 66, -11, 34, .32, False), (304, 112, 17, 52, .22, True)):
        d = f"M{num(CX - rx)} {CY}a{rx} {ry} 0 1 {0 if rev else 1} {2 * rx} 0a{rx} {ry} 0 1 {0 if rev else 1} {-2 * rx} 0"
        orb_fill = t.speck if t.dark else t.gold
        out.append(
            f'<g transform="rotate({rot} {CX} {CY})">'
            f'<path d="{d}" fill="none" stroke="{t.gold}" stroke-width=".8" opacity="{op}"/>'
            f'<g><circle r="13" fill="{gl}"/><circle r="2.6" fill="{orb_fill}"/>'
            f'<animateMotion dur="{dur}s" repeatCount="indefinite" path="{d}"/></g></g>')
    doc.add(f'<g {anim("fade", 2.2, delay)}>{"".join(out)}</g>')


def shooting_star(doc: Doc) -> None:
    t = doc.t
    col = t.speck if t.dark else t.gold
    grad = doc.define("trail", f'<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0">'
                      f'<stop offset="0" stop-color="{col}" stop-opacity="0"/><stop offset="1" stop-color="{col}" stop-opacity=".9"/></linearGradient>')
    doc.style("@keyframes meteor{0%{opacity:0;transform:translate(0,0)}2%{opacity:1}9%{opacity:0;transform:translate(-260px,92px)}100%{opacity:0;transform:translate(-260px,92px)}}")
    doc.add(f'<g transform="translate(1010 70) rotate(160)"><g style="opacity:0;animation:meteor 13s linear 6s infinite">'
            f'<rect x="-120" y="-.8" width="120" height="1.6" rx=".8" fill="{grad}"/>'
            f'</g></g>')


def build(t: Theme) -> str:
    doc = Doc(t, H, f"{C.NAME} — {C.ROLE.title()}",
              f"{C.GREETING.title()}. {C.NAME}, {C.ROLE.lower()}. {C.TAGLINE} {C.MOTTO}")
    background(doc, CX, CY)
    sky(doc, 170, seed=7, avoid=[(280, 110, 920, 450)], clear=[(330, 120, 870, 160), (340, 320, 860, 445)], y_max=470,
        bright=[(1004, 92, 8.5), (1096, 262, 5.5), (96, 236, 5), (842, 64, 4.5), (300, 70, 4)],
        delay=.2)
    moon(doc, 172, 112, 21, delay=.6)
    clear = doc.define("clear-grad", '<radialGradient id="clear-grad"><stop offset=".55" stop-color="#000"/>'
                       '<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>')
    doc.define("clear", f'<mask id="clear" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
               f'<rect width="{W}" height="{H}" fill="#fff"/>'
               f'<ellipse cx="{CX}" cy="146" rx="190" ry="26" fill="{clear}"/>'
               f'<ellipse cx="{CX}" cy="226" rx="300" ry="62" fill="{clear}" opacity=".85"/>'
               f'<ellipse cx="{CX}" cy="342" rx="300" ry="24" fill="{clear}"/>'
               f'<ellipse cx="{CX}" cy="386" rx="290" ry="26" fill="{clear}"/>'
               f'<ellipse cx="{CX}" cy="428" rx="230" ry="22" fill="{clear}"/></mask>')
    doc.add('<g mask="url(#clear)">')
    astrolabe(doc, .3)
    orbits(doc, 1.2)
    doc.add('</g>')
    if t.dark:
        shooting_star(doc)
    mountains(doc, base_y=530, seed=5, delay=.5)

    frame(doc)

    # HELLO, WORLD — the ritual first words of every program
    gy = 146
    greet = T.caps().shape(C.GREETING, 16.5, .62)
    doc.add(letters(T.caps(), C.GREETING, 16.5, CX, gy, t.gold, tracking=.62, start=.9, step=.05))
    for sgn in (-1, 1):
        x = CX + sgn * (greet.width / 2 + 30)
        doc.add(f'<g {anim("fade", 1.2, 1.6)}>' + P(sparkle(x, gy - 6, 6.5), fill=t.gold) + "</g>")

    # the name, gilded
    ny = 262
    name_face = T.display()
    run = name_face.shape(C.NAME, 120, .1)
    gold = gold_fill(doc, ny - 88, ny + 4, "name")
    shadow = doc.define("lift", '<filter id="lift" x="-10%" y="-30%" width="120%" height="160%">'
                        f'<feDropShadow dx="0" dy="{3 if t.dark else 2}" stdDeviation="{5 if t.dark else 3}" '
                        f'flood-color="{"#000" if t.dark else "#6b4a12"}" flood-opacity="{.55 if t.dark else .22}"/></filter>')
    glyphs = run.glyph_ds(CX, ny, "middle")
    doc.add(f'<g filter="{shadow}" fill="{gold}">' + "".join(
        f'<path {anim("rise", 1.5, 1.3 + i * .13)} d="{d}"/>' for i, (d, *_r) in enumerate(glyphs)) + "</g>")
    # a glint of light that crosses the gilding now and then
    doc.define("name-clip", f'<clipPath id="name-clip"><path d="{run.d(CX, ny, "middle")}"/></clipPath>')
    shine = "#fffdf5"
    peak = .9 if t.dark else .85
    doc.define("glint", f'<linearGradient id="glint" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{shine}" stop-opacity="0"/>'
               f'<stop offset=".4" stop-color="{shine}" stop-opacity="{peak}"/><stop offset=".6" stop-color="{shine}" stop-opacity="{peak}"/>'
               f'<stop offset="1" stop-color="{shine}" stop-opacity="0"/></linearGradient>')
    left = CX - run.width / 2
    doc.style(f"@keyframes glint{{0%{{transform:translateX(0)}}24%,100%{{transform:translateX({num(run.width + 260)}px)}}}}")
    doc.add(f'<g clip-path="url(#name-clip)"><g transform="skewX(-20)">'
            f'<rect style="animation:glint 9s ease-in-out 3.4s infinite" x="{num(left - 110)}" y="{ny - 100}" width="90" height="120" fill="url(#glint)"/>'
            f'</g></g>')

    # and stars of light that catch the serifs as the glint arrives and leaves
    doc.style("@keyframes flash{0%,10%,100%{opacity:0;transform:scale(0) rotate(0)}"
              "4%{opacity:1;transform:scale(1) rotate(45deg)}}")
    flare = t.speck if t.dark else "#fffdf5"
    for (fx, fy, r), delay in (((left + 12, ny - 82, 11), 3.55), ((left + run.width - 10, ny - 83, 13), 5.15),
                               ((left + run.width * .62, ny - 2, 8), 4.6)):
        doc.add(f'<g class="fb" style="opacity:0;animation:flash 9s ease-out {delay}s infinite">'
                f'<circle cx="{num(fx)}" cy="{num(fy)}" r="{num(r * 1.6)}" fill="{glow(doc)}"/>'
                + P(sparkle(fx, fy, r), fill=flare) + "</g>")

    rule(doc, 300, 214, delay=2.3)
    doc.add(f'<g {anim("rise-s", 1.4, 2.7)}>' + text(T.caps(), C.ROLE, 19, CX, 347, tracking=.48, fill=t.ink) + "</g>")
    doc.add(f'<g {anim("rise-s", 1.4, 3.1)}>' + text(T.italic(), C.TAGLINE, 28, CX, 392, fill=t.ink2) + "</g>")
    doc.add(f'<g {anim("rise-s", 1.4, 3.5)}>' + text(T.song(), C.MOTTO, 16.5, CX, 432, tracking=.42,
                                                              fill=t.gold, opacity=".95") + "</g>")

    # the leisure seal, stamped last
    sx, sy = 1084, 430
    doc.style("@keyframes stamp{0%{opacity:0;transform:scale(1.6) rotate(-7deg)}55%{opacity:1;transform:scale(.95) rotate(0)}75%{transform:scale(1.02)}}"
              "@keyframes bloom{0%{opacity:0;transform:scale(.5)}20%{opacity:.4}100%{opacity:0;transform:scale(1.9)}}")
    doc.add(f'<circle class="fb" style="opacity:0;animation:bloom 1.4s ease-out 4.25s" cx="{sx}" cy="{sy}" r="38" fill="{t.seal}"/>')
    doc.add(f'<g class="fb" style="animation:stamp .9s 4.1s backwards cubic-bezier(.3,.6,.2,1)">{seal_square(doc, C.LEISURE_SEAL, sx, sy, 64)}</g>')
    return doc.render()
