"""The everyday tools, as a row of quiet outlined chips."""

from __future__ import annotations

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

from .. import content as C
from .. import theme as T
from ..icons import ICONS
from ..svg import document
from ..text import num
from ..theme import Theme

H = 34
ICON, PAD, GAP, LABEL = 16, 11, 8, 13.5


def icon_d(name: str, x: float, cy: float, box: float) -> tuple[str, bool]:
    _, evenodd, ds = ICONS[name]
    bp = BoundsPen(None)
    for d in ds:
        parse_path(d, bp)
    x0, y0, x1, y1 = bp.bounds
    s = box / max(x1 - x0, y1 - y0)
    tx = x + box / 2 - (x0 + x1) / 2 * s
    ty = cy - (y0 + y1) / 2 * s
    pen = SVGPathPen(None, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    for d in ds:
        parse_path(d, TransformPen(pen, (s, 0, 0, s, tx, ty)))
    return pen.getCommands(), evenodd


def build(t: Theme) -> str:
    x, parts = .5, []
    cy = H / 2
    for key, label in C.TOOLS:
        run = T.sans().shape(label, LABEL)
        w = PAD + ICON + 7 + run.width + PAD
        d, evenodd = icon_d(key, x + PAD, cy, ICON * (1.2 if key in ("java", "mysql") else 1))
        rule = ' fill-rule="evenodd"' if evenodd else ""
        parts.append(f'<rect x="{num(x)}" y=".5" width="{num(w)}" height="{H - 1}" rx="6" fill="none" stroke="{t.border}"/>'
                     f'<path fill="{t.muted}"{rule} d="{d}"/>'
                     f'<path fill="{t.fg}" d="{run.d(x + PAD + ICON + 7, cy + LABEL * .36)}"/>')
        x += w + GAP
    width = x - GAP + .5
    return document(round(width, 1), H, "Tools: " + ", ".join(label for _, label in C.TOOLS), "\n".join(parts))
