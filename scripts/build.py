"""Render the profile README plates into assets/.

    python scripts/build.py                 # every plate, both themes
    python scripts/build.py hero about      # selected plates
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from art import content  # noqa: E402
from art.contributions import load  # noqa: E402
from art.theme import THEMES  # noqa: E402

PLATES = ["hero", "about", "toolkit", "constellation", "colophon"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plates", nargs="*", metavar="plate", help=f"any of: {', '.join(PLATES)}")
    ap.add_argument("--out", type=Path, default=ROOT / "assets")
    ap.add_argument("--fetch", action="store_true", help="refresh the contribution calendar (needs GITHUB_TOKEN)")
    ap.add_argument("--data", type=Path, help="render the constellation from this calendar JSON instead")
    args = ap.parse_args()
    args.out.mkdir(exist_ok=True)
    unknown = set(args.plates) - set(PLATES)
    if unknown:
        ap.error(f"unknown plate(s): {', '.join(sorted(unknown))}")
    for name in args.plates or PLATES:
        module = importlib.import_module(f"art.plates.{name}")
        extra = []
        if getattr(module, "NEEDS_DATA", False):
            extra = [json.loads(args.data.read_text()) if args.data else load(content.LOGIN, refresh=args.fetch)]
        for t in THEMES:
            path = args.out / f"{name}-{t.name}.svg"
            path.write_text(module.build(t, *extra), encoding="utf-8")
            print(f"{path}  {path.stat().st_size / 1024:6.1f} KiB")


if __name__ == "__main__":
    main()
