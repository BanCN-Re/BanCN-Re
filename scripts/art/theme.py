"""GitHub's own Primer colours, so the images sit quietly on the page."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .text import face

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"


@dataclass(frozen=True)
class Theme:
    name: str
    fg: str
    muted: str
    subtle: str
    border: str
    accent: str


LIGHT = Theme("light", fg="#1f2328", muted="#59636e", subtle="#818b98", border="#d1d9e0", accent="#0969da")
DARK = Theme("dark", fg="#f0f6fc", muted="#9198a1", subtle="#656c76", border="#3d444d", accent="#4493f8")
THEMES = (LIGHT, DARK)


def _f(name: str, **features):
    return face(str(FONT_DIR / name), **features)


def sans_bold():
    return _f("Inter-SemiBold.ttf")


def sans():
    return _f("Inter-Regular.ttf")


def mono():
    return _f("JetBrainsMono-Regular.ttf", calt=False, liga=False)


def cjk():
    return _f("NotoSansSC-Regular.ttf")
