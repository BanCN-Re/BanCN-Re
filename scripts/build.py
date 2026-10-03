"""Render the README images into assets/, one per GitHub theme.

    python scripts/build.py               # everything
    python scripts/build.py header        # just one
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from art.theme import THEMES  # noqa: E402

PARTS = ["header", "stack"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("parts", nargs="*", metavar="part", help=f"any of: {', '.join(PARTS)}")
    ap.add_argument("--out", type=Path, default=ROOT / "assets")
    args = ap.parse_args()
    unknown = set(args.parts) - set(PARTS)
    if unknown:
        ap.error(f"unknown part(s): {', '.join(sorted(unknown))}")
    args.out.mkdir(exist_ok=True)
    for name in args.parts or PARTS:
        module = importlib.import_module(f"art.plates.{name}")
        for t in THEMES:
            path = args.out / f"{name}-{t.name}.svg"
            path.write_text(module.build(t), encoding="utf-8")
            print(f"{path}  {path.stat().st_size / 1024:5.1f} KiB")


if __name__ == "__main__":
    main()
