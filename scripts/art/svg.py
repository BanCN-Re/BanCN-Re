"""A tiny SVG document builder."""

from __future__ import annotations

from html import escape


def document(width: float, height: float, title: str, body: str, css: str = "", defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}" '
        f'role="img" aria-label="{escape(title)}">\n'
        f"<title>{escape(title)}</title>\n"
        + (f"<style>{css}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>\n" if css else "")
        + (f"<defs>{defs}</defs>\n" if defs else "")
        + body + "\n</svg>\n"
    )
