"""Every word that appears on the plates.

Edit here, then run `python scripts/make_fonts.py` (only needed when new
characters appear) and `python scripts/build.py`.
"""

LOGIN = "BanCN-Re"
NAME = "BanCN"
GREETING = "HELLO, WORLD"
ROLE = "JAVA BACKEND DEVELOPER"
TAGLINE = "Building practical tools, learning in public."
MOTTO = "写干净的代码 · 造可靠的系统"
LEISURE_SEAL = "大道至简"          # 闲章 — "the great way is simple"
NAME_SEAL = ("BAN", "CN")          # 名章
SINCE = "MMXXIV"                   # on GitHub since 2024

# Earthly branches around the astrolabe, starting from the top (south / 午).
BRANCHES = "午未申酉戌亥子丑寅卯辰巳"

SECTIONS = {
    "about": ("壹", "ABOUT", "自述"),
    "toolkit": ("贰", "TOOLKIT", "利器"),
    "constellation": ("叁", "CONSTELLATION", "星图"),
}

# A couplet hangs either side of the code: 上联 on the right, 下联 on the left.
COUPLET = ("行稳致远", "执简驭繁")   # steady steps go far · hold the simple, master the complex

# The About plate: a Java class written in the author's own words.
CODE_FILE = "BanCN.java"
CODE = [
    [("comment", "/** 写干净的代码，造可靠的系统。 */")],
    [("kw", "public final class "), ("type", "BanCN"), ("kw", " implements "), ("type", "Developer"), ("punct", " {")],
    [],
    [("plain", "    "), ("type", "String"), ("plain", "   role  "), ("punct", "= "), ("str", '"Java Backend Developer"'), ("punct", ";")],
    [("plain", "    "), ("type", "String"), ("plain", "   craft "), ("punct", "= "), ("str", '"Clean code, reliable systems"'), ("punct", ";")],
    [("plain", "    "), ("type", "String"), ("punct", "[] "), ("plain", "stack "), ("punct", "= { "), ("str", '"Java"'), ("punct", ", "),
     ("str", '"Python"'), ("punct", ", "), ("str", '"MySQL"'), ("punct", " };")],
    [],
    [("plain", "    "), ("anno", "@Override"), ("kw", " public void "), ("fn", "everyday"), ("punct", "() {")],
    [("plain", "        "), ("fn", "build"), ("punct", "("), ("fn", "practicalTools"), ("punct", "());")],
    [("plain", "        "), ("fn", "learnInPublic"), ("punct", "();")],
    [("plain", "    "), ("punct", "}")],
    [],
    [("plain", "    "), ("anno", "@Override"), ("kw", " public "), ("type", "String"), ("plain", " "), ("fn", "toString"),
     ("punct", "() { "), ("kw", "return "), ("str", '"Fake Null"'), ("punct", "; }")],
    [("punct", "}")],
]

TOOLKIT_QUOTE = "工欲善其事，必先利其器。"
TOOLKIT_SOURCE = "——《论语 · 卫灵公》"
TOOLKIT_QUOTE_EN = "The mechanic, who wishes to do his work well, must first sharpen his tools."
TOOLS = [
    ("java", "JAVA", "Language"),
    ("python", "PYTHON", "Scripting"),
    ("mysql", "MYSQL", "Database"),
    ("git", "GIT", "Versioning"),
    ("vscode", "VS CODE", "Editor"),
]

CONSTELLATION_LINE = "Every commit, a star."
CONSTELLATION_LINE_ZH = "每一次提交，都是一颗星。"
STATS = [
    ("total", "CONTRIBUTIONS", "年度贡献"),
    ("active", "ACTIVE DAYS", "活跃天数"),
    ("longest", "LONGEST STREAK", "最长连续"),
    ("current", "CURRENT STREAK", "当前连续"),
]
CHARTING = "CHARTING THE SKY"
CHARTING_ZH = "星图绘制中"

FAREWELL = "山高水长，后会有期"
FAREWELL_EN = "Thank you for stopping by — until we meet again."
COLOPHON = f"SET IN CINZEL, CORMORANT GARAMOND, NOTO SERIF SC & JETBRAINS MONO  ·  ON GITHUB SINCE {SINCE}"


def cjk_text() -> str:
    """Every string that is set in a Chinese typeface."""
    parts = [MOTTO, LEISURE_SEAL, BRANCHES, TOOLKIT_QUOTE, TOOLKIT_SOURCE, CONSTELLATION_LINE_ZH, FAREWELL, *COUPLET]
    parts += [zh for _, _, zh in SECTIONS.values()] + [num for num, _, _ in SECTIONS.values()]
    parts += [zh for _, _, zh in STATS] + [CHARTING_ZH]
    parts += [text for line in CODE for _, text in line]
    return "".join(parts)
