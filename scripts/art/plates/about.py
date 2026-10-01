"""壹 · About: a Java class typed out line by line, flanked by a hanging couplet."""

from __future__ import annotations

from .. import content as C
from .. import theme as T
from ..svg import W, Doc, P, anim, background, frame, gold_fill, section_header, sky
from ..text import num
from ..theme import Theme

FS = 18.0                 # code size
LH = 29.0                 # line height
WIN_X, WIN_W = 196, 808
WIN_Y = 176
BAR = 42
START = 1.6               # typing begins
PER_COL = .016            # seconds per column
PAUSE = .09               # between lines


def colours(t: Theme) -> dict[str, str]:
    if t.dark:
        return dict(kw="#d9b56c", type="#f3ead3", str="#97c8aa", comment="#857c69", anno="#e0765c",
                    fn="#ecd2a0", punct="#9d947f", plain="#d2c8b1", num="#5d574b")
    return dict(kw="#9a6a1c", type="#1f1c18", str="#3d7656", comment="#968b78", anno="#b8321f",
                fn="#7d5216", punct="#6e665a", plain="#3c362e", num="#b9ae98")


def is_wide(ch: str) -> bool:
    return ord(ch) >= 0x2E80


def code_line(tokens, x0: float, y: float, col_w: float, pal: dict) -> tuple[str, int]:
    """Lay tokens on a monospace grid; CJK takes two columns. Returns (markup, columns)."""
    mono, mono_i, song = T.mono(), T.mono_italic(), T.song()
    col = 0
    out = []
    for kind, s in tokens:
        ds = []
        for ch in s:
            if ch == " ":
                col += 1
                continue
            if is_wide(ch):
                run = song.shape(ch, FS * 1.02)
                ds.append(run.d(x0 + (col + 1) * col_w, y + 1, "middle"))
                col += 2
            else:
                face = mono_i if kind == "comment" else mono
                ds.append(face.shape(ch, FS).d(x0 + col * col_w, y))
                col += 1
        if ds:
            out.append(P("".join(ds), fill=pal[kind]))
    return "".join(out), col


def couplet(doc: Doc, chars: str, cx: float, top: float, delay: float) -> None:
    """A hanging scroll: the top roller stays put while the lower one drops and unrolls it."""
    t = doc.t
    face = T.brush()
    step, size = 58, 44
    height = step * len(chars) + 34

    def roller(y: float) -> str:
        return (f'<path d="M{num(cx - 40)} {num(y)}H{num(cx + 40)}" stroke="{t.gold}" stroke-width="2.4" stroke-linecap="round"/>'
                + "".join(f'<circle cx="{num(cx + s * 44)}" cy="{num(y)}" r="3" fill="{t.gold}"/>' for s in (-1, 1)))

    gold = gold_fill(doc, top, top + height, f"scroll{int(cx)}")
    paper = (f'<rect x="{num(cx - 32)}" y="{num(top)}" width="64" height="{num(height)}" fill="{t.gold}" fill-opacity="{.05 if t.dark else .06}" '
             f'stroke="{t.gold}" stroke-width=".8" stroke-opacity=".55"/>'
             f'<rect x="{num(cx - 27)}" y="{num(top + 5)}" width="54" height="{num(height - 10)}" fill="none" '
             f'stroke="{t.gold}" stroke-width=".5" stroke-opacity=".35"/>')
    glyphs = "".join(f'<path {anim("rise-s", 1, delay + 1 + i * .22)} d="{face.shape(ch, size).d(cx, top + 26 + step * i + size * .78, "middle")}"/>'
                     for i, ch in enumerate(chars))
    drop = f"drop{int(height)}"
    doc.style(".unroll{transform-box:fill-box;transform-origin:center top}@keyframes unroll{from{transform:scaleY(0)}}"
              f"@keyframes {drop}{{from{{transform:translateY(-{num(height)}px)}}}}")
    doc.add(f'<g class="unroll" {anim("unroll", 1.3, delay)}>{paper}</g>' + roller(top)
            + f'<g style="animation:{drop} 1.3s cubic-bezier(.2,.7,.2,1) {delay:.2f}s backwards">{roller(top + height)}</g>'
            + f'<g fill="{gold}">{glyphs}</g>')


def build(t: Theme) -> str:
    pal = colours(t)
    lines = C.CODE
    win_h = BAR + 22 + LH * len(lines) + 14
    H = int(WIN_Y + win_h + 52)
    doc = Doc(t, H, "About — 自述",
              f"A Java class describing {C.NAME}: role Java Backend Developer, craft clean code and reliable systems, "
              f"stack Java, Python and MySQL; every day builds practical tools and learns in public; toString returns "
              f"\"Fake Null\". Flanked by the couplet {C.COUPLET[0]} / {C.COUPLET[1]}.")
    background(doc, W / 2, H * .45)
    sky(doc, 46, seed=21, avoid=[(150, 150, 1050, H)], clear=[(300, 20, 900, 150)], y_max=H - 40, twinkle_every=4, delay=.2)
    frame(doc)
    section_header(doc, "about", 66)

    # hanging couplet: 上联 on the right, 下联 on the left
    mid = WIN_Y + win_h / 2
    top = mid - (58 * 4 + 34) / 2
    couplet(doc, C.COUPLET[0], 1100, top, .7)
    couplet(doc, C.COUPLET[1], 100, top, .9)

    # the editor window
    shadow = doc.define("win-shadow", '<filter id="win-shadow" x="-10%" y="-10%" width="120%" height="125%">'
                        f'<feDropShadow dx="0" dy="{8 if t.dark else 6}" stdDeviation="{14 if t.dark else 12}" '
                        f'flood-color="{"#000" if t.dark else "#5a4320"}" flood-opacity="{.5 if t.dark else .14}"/></filter>')
    x0, y0 = WIN_X, WIN_Y
    dots = "".join(f'<circle cx="{x0 + 24 + i * 19}" cy="{y0 + BAR / 2}" r="5.2" fill="{c}" opacity="{.9 if t.dark else .85}"/>'
                   for i, c in enumerate((t.seal, t.gold, t.jade)))
    fname = T.mono().shape(C.CODE_FILE, 13.5)
    window = (f'<rect x="{x0}" y="{y0}" width="{WIN_W}" height="{num(win_h)}" rx="12" fill="{t.panel}" filter="{shadow}"/>'
              f'<rect x="{x0}" y="{y0}" width="{WIN_W}" height="{num(win_h)}" rx="12" fill="{t.panel}"/>'
              f'<rect x="{x0 + .5}" y="{y0 + .5}" width="{WIN_W - 1}" height="{num(win_h - 1)}" rx="11.5" fill="none" stroke="{t.gold}" stroke-opacity="{.32 if t.dark else .45}"/>'
              f'<path d="M{x0} {y0 + BAR}H{x0 + WIN_W}" stroke="{t.gold}" stroke-opacity="{.22 if t.dark else .3}"/>'
              + dots + P(fname.d(x0 + WIN_W / 2, y0 + BAR / 2 + 4.6, "middle"), fill=t.ink3))

    col_w = T.mono().shape("M", FS).width
    gutter_x = x0 + 46
    code_x = x0 + 68
    first = y0 + BAR + 22 + FS * .78
    nums, body, covers = [], [], []
    clock = START
    last_caret = None
    for i, tokens in enumerate(lines):
        y = first + i * LH
        nums.append(P(T.mono().shape(str(i + 1), 14).d(gutter_x, y - 1, "end"), fill=pal["num"]))
        markup, cols = code_line(tokens, code_x, y, col_w, pal)
        body.append(markup)
        if not cols:
            clock += PAUSE * 2
            continue
        dur = cols * PER_COL
        w = cols * col_w
        top = y - FS * .95
        # a panel-coloured cover slides right one column at a time, revealing the text
        covers.append(f'<rect x="{num(code_x - 1)}" y="{num(top)}" width="{num(w + col_w + 2)}" height="{num(LH)}" fill="{t.panel}" '
                      f'style="transform:translateX({num(w + col_w + 4)}px);animation:type{i} {dur:.2f}s steps({cols}) {clock:.2f}s backwards"/>')
        doc.style(f"@keyframes type{i}{{from{{transform:translateX(0)}}to{{transform:translateX({num(w)}px)}}}}")
        caret = (f'<rect x="{num(code_x)}" y="{num(top + 3)}" width="{num(col_w * .9)}" height="{num(FS * 1.18)}" fill="{t.gold}" opacity=".0" '
                 f'style="animation:type{i} {dur:.2f}s steps({cols}) {clock:.2f}s forwards,on {dur:.2f}s {clock:.2f}s"/>')
        covers.append(caret)
        last_caret = (i, dur, clock, top, w)
        clock += dur + PAUSE
    if last_caret:
        i, dur, start, top, w = last_caret
        covers[-1] = (f'<rect x="{num(code_x + w)}" y="{num(top + 3)}" width="{num(col_w * .9)}" height="{num(FS * 1.18)}" fill="{t.gold}" '
                      f'style="opacity:.85;animation:blink 1.1s step-end {start + dur:.2f}s infinite,fade .2s {start + dur:.2f}s backwards"/>')
    doc.style("@keyframes on{from,to{opacity:.85}}@keyframes blink{50%{opacity:0}}")
    clip = doc.define("code-clip", f'<clipPath id="code-clip"><rect x="{x0 + 2}" y="{y0 + BAR + 2}" width="{WIN_W - 4}" height="{num(win_h - BAR - 4)}"/></clipPath>')
    # one group, so the typing covers fade in together with the panel they match
    doc.add(f'<g {anim("rise", 1.2, .5)}>{window}'
            f'<g {anim("fade", 1, 1.1)}>{"".join(nums)}</g>'
            f'{"".join(body)}<g clip-path="{clip}">{"".join(covers)}</g></g>')
    return doc.render()
