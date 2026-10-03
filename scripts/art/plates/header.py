"""Name, role, and a terminal line that types out a few phrases in turn."""

from __future__ import annotations

from .. import content as C
from .. import theme as T
from ..svg import document
from ..text import num
from ..theme import Theme

W, H = 840, 150
X = 2
MONO = 15.0
TYPE, ERASE, HOLD, GAP = .075, .03, 2.2, .45   # seconds


def _line(text: str, x0: float, y: float, col: float) -> tuple[str, list[float]]:
    """Outline a phrase on a monospace grid (CJK takes two columns); returns (d, right edge after each char)."""
    ds, edges, cols = [], [], 0
    for ch in text:
        wide = ord(ch) >= 0x2E80
        if ch != " ":
            if wide:
                ds.append(T.cjk().shape(ch, MONO * 1.05).d(x0 + (cols + 1) * col, y + .5, "middle"))
            else:
                ds.append(T.mono().shape(ch, MONO).d(x0 + cols * col, y))
        cols += 2 if wide else 1
        edges.append(cols * col)
    return "".join(ds), edges


def _discrete(attr: str, frames: list[tuple[float, float]], total: float) -> str:
    """SMIL step animation through (time, value) frames, looping every `total` seconds."""
    times = ";".join(f"{t / total:.4f}" for t, _ in frames)
    values = ";".join(num(v) for _, v in frames)
    return (f'<animate attributeName="{attr}" dur="{num(total)}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{times}" values="{values}"/>')


def build(t: Theme) -> str:
    name = T.sans_bold().shape(C.NAME, 44, -.01)
    role = T.sans().shape(C.ROLE, 19)
    col = T.mono().shape("M", MONO).width
    y = 128
    x0 = X + 22

    # one timeline for all phrases: type, hold, erase, pause, next
    lines, plans, clock = [], [], 0.0
    for text in C.PHRASES:
        d, edges = _line(text, x0, y, col)
        frames = [(clock, 0.0)]
        for i, e in enumerate(edges):
            frames.append((clock + (i + 1) * TYPE, e))
        clock += len(edges) * TYPE + HOLD
        for i in range(len(edges) - 1, -1, -1):
            frames.append((clock, edges[i - 1] if i else 0.0))
            clock += ERASE
        clock += GAP
        lines.append(d)
        plans.append(frames)
    total = clock

    defs, body, caret = [], [], {}
    for k, (d, frames) in enumerate(zip(lines, plans)):
        for ft, w in frames:
            caret[round(ft, 4)] = x0 + w
        if frames[0][0] > 0:
            frames = [(0.0, 0.0)] + frames
        defs.append(f'<clipPath id="p{k}"><rect x="{num(x0)}" y="{y - 20}" width="0" height="28">'
                    f'{_discrete("width", frames, total)}</rect></clipPath>')
        body.append(f'<path clip-path="url(#p{k})" fill="{t.muted}" d="{d}"/>')
    caret = sorted(caret.items())

    css = (".in{animation:in .7s cubic-bezier(.2,.7,.2,1) backwards}"
           "@keyframes in{from{opacity:0;transform:translateY(6px)}}"
           ".blink{animation:blink 1.06s step-end infinite}@keyframes blink{50%{opacity:0}}")
    out = [
        f'<path class="in" fill="{t.fg}" d="{name.d(X, 52)}"/>',
        f'<path class="in" style="animation-delay:.12s" fill="{t.muted}" d="{role.d(X + 1, 88)}"/>',
        '<g class="in" style="animation-delay:.24s">',
        f'<path fill="{t.accent}" d="{T.mono().shape(">", MONO).d(X + 1, y)}"/>',
        *body,
        f'<rect class="blink" x="{num(x0)}" y="{y - 13}" width="2" height="17" fill="{t.accent}">{_discrete("x", caret, total)}</rect>',
        "</g>",
    ]
    return document(W, H, f"{C.NAME} — {C.ROLE}. " + " / ".join(C.PHRASES), "\n".join(out), css, "".join(defs))
