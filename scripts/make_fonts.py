"""Cut the typefaces down to the few glyphs the plates use.

Downloads the variable OFL fonts from github.com/google/fonts, pins each to a
single weight and subsets it, writing small static TTFs to scripts/fonts/.
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

LATIN = "".join(map(chr, range(0x20, 0x7F))) + "".join(map(chr, range(0xA0, 0x100))) + "–—‘’“”•…·→"

# output file: (family dir, source file, weight or None, charset)
BUILD = {
    "Cinzel-Medium.ttf": ("cinzel", "Cinzel[wght].ttf", 500, "latin"),
    "Cinzel-SemiBold.ttf": ("cinzel", "Cinzel[wght].ttf", 600, "latin"),
    "CormorantGaramond-MediumItalic.ttf": ("cormorantgaramond", "CormorantGaramond-Italic[wght].ttf", 500, "latin"),
    "CormorantGaramond-SemiBold.ttf": ("cormorantgaramond", "CormorantGaramond[wght].ttf", 600, "latin"),
    "JetBrainsMono-Regular.ttf": ("jetbrainsmono", "JetBrainsMono[wght].ttf", 400, "latin"),
    "JetBrainsMono-Italic.ttf": ("jetbrainsmono", "JetBrainsMono-Italic[wght].ttf", 400, "latin"),
    "NotoSerifSC-Regular.ttf": ("notoserifsc", "NotoSerifSC[wght].ttf", 400, "cjk"),
    "NotoSerifSC-SemiBold.ttf": ("notoserifsc", "NotoSerifSC[wght].ttf", 600, "cjk"),
    "NotoSerifSC-Black.ttf": ("notoserifsc", "NotoSerifSC[wght].ttf", 900, "cjk"),
    "MaShanZheng-Regular.ttf": ("mashanzheng", "MaShanZheng-Regular.ttf", None, "cjk"),
    "ZhiMangXing-Regular.ttf": ("zhimangxing", "ZhiMangXing-Regular.ttf", None, "cjk"),
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


def cut(data: bytes, weight: int | None, text: str) -> TTFont:
    font = TTFont(io.BytesIO(data))
    opts = subset.Options()
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "lnum", "onum", "pnum", "tnum"]
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6]
    opts.hinting = False
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    if weight is not None and "fvar" in font:
        font = instancer.instantiateVariableFont(font, {"wght": weight})
    return font


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, help="directory holding <family>_<file> downloads")
    args = ap.parse_args()

    charsets = {"latin": LATIN, "cjk": " ·—" + content.cjk_text() + "，。《》、：；！？"}
    FONT_DIR.mkdir(exist_ok=True)
    cache: dict[tuple[str, str], bytes] = {}
    for out, (family, filename, weight, charset) in BUILD.items():
        key = (family, filename)
        if key not in cache:
            cache[key] = fetch(family, filename, args.source)
        font = cut(cache[key], weight, charsets[charset])
        font.save(FONT_DIR / out)
        print(f"{out:40s} {(FONT_DIR / out).stat().st_size / 1024:6.1f} KiB")
        licence = FONT_DIR / f"OFL-{family}.txt"
        if not licence.exists():
            licence.write_bytes(fetch(family, "OFL.txt", args.source))


if __name__ == "__main__":
    main()
