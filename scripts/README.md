# Profile plates

The profile README is five SVG "plates", each drawn twice: **day** (xuan paper,
ink and gold leaf) for GitHub's light theme and **night** (midnight sky, ivory
and gold) for the dark theme. The README picks one with `<picture>` and
`prefers-color-scheme`.

| Plate | File | What it shows |
| --- | --- | --- |
| Frontispiece | `assets/hero-*.svg` | Greeting, name, astrolabe, mountains, the 大道至简 seal |
| 壹 About | `assets/about-*.svg` | A Java class typed out line by line, between a hanging couplet |
| 贰 Toolkit | `assets/toolkit-*.svg` | The Analects on tools, struck-gold medallions |
| 叁 Constellation | `assets/constellation-*.svg` | A year of contributions as a star chart, redrawn daily |
| 跋 Colophon | `assets/colophon-*.svg` | Farewell in running script, name seal, sea-and-cliff hem |

All lettering is converted to outlines, because GitHub serves README images as
sandboxed SVG that may not load web fonts. The animations are plain CSS/SMIL
and settle on the finished plate; a `prefers-reduced-motion` rule skips
straight to that final frame.

## Rebuilding

```sh
pip install -r scripts/requirements.txt
python scripts/build.py                  # every plate
python scripts/build.py hero about       # just some
python scripts/build.py constellation --fetch   # refresh the star chart (needs GITHUB_TOKEN)
```

Copy lives in `scripts/art/content.py`. If an edit introduces characters the
bundled font subsets lack, the build says so; run `python scripts/make_fonts.py`
to re-cut them from Google Fonts.

`.github/workflows/constellation.yml` redraws the star chart every day and
commits it when it changes. The workflow has to be on the default branch for
the schedule to run.

## Credits

- Typefaces (SIL Open Font License 1.1, see `scripts/fonts/OFL-*.txt`):
  Cinzel, Cormorant Garamond, JetBrains Mono, Noto Serif SC, Ma Shan Zheng,
  Zhi Mang Xing.
- Brand marks: [Simple Icons](https://simpleicons.org) (CC0) and
  [devicon](https://github.com/devicons/devicon) (MIT). The marks remain
  trademarks of their owners.
