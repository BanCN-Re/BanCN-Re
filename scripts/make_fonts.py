"""Cut the typefaces down to the few glyphs the README images use.

Downloads the variable OFL fonts from github.com/google/fonts, pins each to a
single instance and subsets it, writing small static TTFs to scripts/fonts/.
Only needs re-running when content.py gains characters the subsets lack.

    python scripts/make_fonts.py [--source DIR_WITH_DOWNLOADED_FONTS]
"""

from __future__ import annotations

import argparse
import io
import sys
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import content  # noqa: E402
from art.theme import FONT_DIR  # noqa: E402

GOOGLE_FONTS = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
LATIN = "".join(map(chr, range(0x20, 0x7F))) + "–—‘’“”•…·→"

# output file: (family dir, source file, axis values, charset)
BUILD = {
    "Inter-SemiBold.ttf": ("inter", "Inter[opsz,wght].ttf", {"wght": 600, "opsz": 32}, "latin"),
    "Inter-Regular.ttf": ("inter", "Inter[opsz,wght].ttf", {"wght": 400, "opsz": 14}, "latin"),
    "JetBrainsMono-Regular.ttf": ("jetbrainsmono", "JetBrainsMono[wght].ttf", {"wght": 400}, "latin"),
    "NotoSansSC-Regular.ttf": ("notosanssc", "NotoSansSC[wght].ttf", {"wght": 400}, "cjk"),
}


def fetch(family: str, filename: str, source: Path | None) -> bytes:
    if source:
        local = source / f"{family}_{filename}"
        if local.exists():
            return local.read_bytes()
    url = GOOGLE_FONTS + family + "/" + filename.replace("[", "%5B").replace("]", "%5D")
    print(f"  downloading {url}")
    with urllib.request.urlopen(url) as r:
        return r.read()


def cut(data: bytes, axes: dict, text: str) -> TTFont:
    font = TTFont(io.BytesIO(data))
    opts = subset.Options()
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "lnum", "tnum"]
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6]
    opts.hinting = False
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    if "fvar" in font:
        font = instancer.instantiateVariableFont(font, axes)
    return font


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, help="directory holding <family>_<file> downloads")
    args = ap.parse_args()

    charsets = {"latin": LATIN, "cjk": " " + content.cjk_text()}
    FONT_DIR.mkdir(exist_ok=True)
    cache: dict[tuple[str, str], bytes] = {}
    for out, (family, filename, axes, charset) in BUILD.items():
        key = (family, filename)
        if key not in cache:
            cache[key] = fetch(family, filename, args.source)
        cut(cache[key], axes, charsets[charset]).save(FONT_DIR / out)
        print(f"{out:30s} {(FONT_DIR / out).stat().st_size / 1024:6.1f} KiB")
        licence = FONT_DIR / f"OFL-{family}.txt"
        if not licence.exists():
            licence.write_bytes(fetch(family, "OFL.txt", args.source))


if __name__ == "__main__":
    main()
