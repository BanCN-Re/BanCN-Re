# README images

The profile README is mostly plain Markdown. Two small images sit in it, each
drawn for GitHub's light and dark themes (picked with `<picture>`), with
transparent backgrounds and GitHub's own Primer colours:

- `assets/header-*.svg`: name, role, and a terminal line that types a few phrases in turn
- `assets/stack-*.svg`: the everyday tools as outlined chips

Text is converted to outlines because GitHub serves README images as sandboxed
SVG that cannot load web fonts.

## Rebuilding

```sh
pip install -r scripts/requirements.txt
python scripts/build.py
```

Words live in `scripts/art/content.py`. If an edit adds characters the bundled
font subsets lack, the build says so; run `python scripts/make_fonts.py` to
re-cut them from Google Fonts.

## Credits

- Typefaces (SIL Open Font License 1.1, see `scripts/fonts/OFL-*.txt`):
  Inter, JetBrains Mono, Noto Sans SC.
- Brand marks: [Simple Icons](https://simpleicons.org) (CC0) and
  [devicon](https://github.com/devicons/devicon) (MIT). The marks remain
  trademarks of their owners.
