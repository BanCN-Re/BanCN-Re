"""Text → SVG outlines.

GitHub serves README images as sandboxed SVG, which may not load web fonts.
Every word on the plates is therefore shaped with HarfBuzz and written out as
plain <path> outlines, so the typography looks identical on every device.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen


def num(v: float) -> str:
    """Compact number formatting for SVG output."""
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


class Face:
    """One font file at one fixed design (weight/features)."""

    def __init__(self, path: str | Path, variations: dict | None = None, features: dict | None = None):
        self.path = str(path)
        blob = hb.Blob.from_file_path(self.path)
        self.hb_face = hb.Face(blob)
        self.font = hb.Font(self.hb_face)
        if variations:
            self.font.set_variations(variations)
        self.upem = self.hb_face.upem
        self.features = {"kern": True, "liga": True, **(features or {})}
        self._outlines: dict[int, RecordingPen] = {}

    def outline(self, gid: int) -> RecordingPen:
        pen = self._outlines.get(gid)
        if pen is None:
            pen = RecordingPen()
            self.font.draw_glyph_with_pen(gid, pen)
            self._outlines[gid] = pen
        return pen

    def has_char(self, ch: str) -> bool:
        return self.font.get_nominal_glyph(ord(ch)) is not None

    def shape(self, text: str, size: float, tracking: float = 0.0, features: dict | None = None,
              advance_override=None) -> "Run":
        """Shape `text`; `tracking` is extra space in em units between glyphs."""
        missing = [c for c in text if not c.isspace() and not self.has_char(c)]
        if missing:
            raise ValueError(f"{Path(self.path).name} has no glyph for {''.join(sorted(set(missing)))!r}; "
                             "re-run scripts/make_fonts.py after editing content")
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {**self.features, **(features or {})})
        scale = size / self.upem
        glyphs = []
        x = 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            adv = pos.x_advance * scale
            if advance_override is not None:
                adv = advance_override(text[info.cluster], adv)
            glyphs.append(Glyph(info.codepoint, text[info.cluster], x + pos.x_offset * scale,
                                pos.y_offset * scale, adv))
            x += adv + tracking * size
        width = x - tracking * size if glyphs else 0.0
        return Run(self, size, glyphs, width)


@dataclass
class Glyph:
    gid: int
    char: str
    x: float       # pen position relative to run start
    dy: float
    advance: float


@dataclass
class Run:
    face: Face
    size: float
    glyphs: list[Glyph]
    width: float

    def origin(self, x: float, anchor: str) -> float:
        return {"start": x, "middle": x - self.width / 2, "end": x - self.width}[anchor]

    def _glyph_d(self, g: Glyph, x0: float, y: float) -> str:
        s = self.size / self.face.upem
        pen = SVGPathPen(None, ntos=num)
        self.face.outline(g.gid).replay(TransformPen(pen, (s, 0, 0, -s, x0 + g.x, y - g.dy)))
        return pen.getCommands()

    def d(self, x: float, y: float, anchor: str = "start") -> str:
        x0 = self.origin(x, anchor)
        return "".join(self._glyph_d(g, x0, y) for g in self.glyphs)

    def glyph_ds(self, x: float, y: float, anchor: str = "start"):
        """Per-glyph outlines, for letter-by-letter animation: [(d, left, right, char)]."""
        x0 = self.origin(x, anchor)
        out = []
        for g in self.glyphs:
            d = self._glyph_d(g, x0, y)
            if d:
                out.append((d, x0 + g.x, x0 + g.x + g.advance, g.char))
        return out


@lru_cache(maxsize=None)
def face(path: str, weight: float | None = None, **features) -> Face:
    variations = {"wght": weight} if weight is not None else None
    return Face(path, variations, features or None)
