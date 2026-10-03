"""Every word that appears in the README images.

Edit here, then run `python scripts/build.py`. If the build reports a missing
glyph, run `python scripts/make_fonts.py` first.
"""

NAME = "BanCN"
ROLE = "Java Backend Developer"

# The line under the name types these out one after another, forever.
PHRASES = [
    "写干净的代码，造可靠的系统。",
    "clean code, reliable systems",
    "building practical tools",
    "learning in public",
]

# (icon key in icons.py, label)
TOOLS = [
    ("java", "Java"),
    ("python", "Python"),
    ("mysql", "MySQL"),
    ("git", "Git"),
    ("vscode", "VS Code"),
]


def cjk_text() -> str:
    return "".join(PHRASES)
