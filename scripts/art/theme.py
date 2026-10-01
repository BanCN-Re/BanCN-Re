"""Palettes and typefaces.

Two moods share every layout:
  day   — xuan paper, ink and gold leaf (GitHub light theme)
  night — midnight sky, ivory and gold (GitHub dark theme)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .text import face

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"


@dataclass(frozen=True)
class Theme:
    name: str
    dark: bool
    bg: tuple[str, str, str]        # radial: centre, middle, edge
    ink: str                         # primary text
    ink2: str                        # secondary text
    ink3: str                        # quiet text / hairlines
    gold: str                        # flat gold for strokes
    gold_ramp: tuple[str, ...]       # metallic gradient, top → bottom
    seal: str                        # cinnabar
    seal_text: str                   # carved-out paper colour inside seals
    jade: str
    panel: str                       # code window
    panel_edge: str
    speck: str                       # tiny stars / paper specks


NIGHT = Theme(
    name="night", dark=True,
    bg=("#141b2c", "#0c1019", "#07090f"),
    ink="#efe6cf", ink2="#bdb39b", ink3="#7c7462",
    gold="#d6b26a",
    gold_ramp=("#fff4d1", "#ecd08c", "#c99a46", "#f2d999", "#a77a35"),
    seal="#c3402b", seal_text="#f6ead0",
    jade="#93c4a6",
    panel="#0e131e", panel_edge="#2a2a2a",
    speck="#f3e7c4",
)

DAY = Theme(
    name="day", dark=False,
    bg=("#fbf7ee", "#f5efe1", "#ebe1cb"),
    ink="#1f1c18", ink2="#4d463c", ink3="#8f8574",
    gold="#a8792b",
    gold_ramp=("#d9b264", "#b3832f", "#7d5617", "#c4974a", "#6f4c14"),
    seal="#b8321f", seal_text="#fbf4e4",
    jade="#3d7656",
    panel="#fdfaf3", panel_edge="#d9ccb0",
    speck="#b48a3c",
)

THEMES = (DAY, NIGHT)


def _f(name: str, **features):
    return face(str(FONT_DIR / name), **features)


# Roman inscriptional capitals for names and labels.
def display():
    return _f("Cinzel-SemiBold.ttf")


def caps():
    return _f("Cinzel-Medium.ttf")


# Old-style Garamond for prose and numerals.
def italic():
    return _f("CormorantGaramond-MediumItalic.ttf")


def numerals():
    return _f("CormorantGaramond-SemiBold.ttf", lnum=True)


def mono():
    return _f("JetBrainsMono-Regular.ttf", calt=False, liga=False)


def mono_italic():
    return _f("JetBrainsMono-Italic.ttf", calt=False, liga=False)


# Chinese: Song for text, brush for numerals, running script for the farewell.
def song():
    return _f("NotoSerifSC-Regular.ttf")


def song_bold():
    return _f("NotoSerifSC-SemiBold.ttf")


def song_black():
    return _f("NotoSerifSC-Black.ttf")


def brush():
    return _f("MaShanZheng-Regular.ttf")


def cursive():
    return _f("ZhiMangXing-Regular.ttf")
