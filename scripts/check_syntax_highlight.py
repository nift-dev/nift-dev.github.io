#!/usr/bin/env python3
"""Verify the website's Nift syntax highlighter recognizes every path-family
directive in its call form.

The static highlighter lives in public/assets/js/script.js. The console
highlighter in the Nift source already covers content/pathtopage/input/path/
pathto/pathtofile/getenv/... via tests/console_smoke.cpp; this check mirrors
that coverage for the website grammar so a future edit cannot silently drop a
supported directive.

Run after editing the highlighter:
    python3 scripts/check_syntax_highlight.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "public" / "assets" / "js" / "script.js"

POSITIVE = [
    "@path('about')",
    "@pathto('about')",
    "@pathtofile('public/assets/app.js')",
    "@pathtopage(1)",
    "\\@path('about')",
    "\\@pathto('about')",
    "\\@pathtofile('public/assets/app.js')",
    "\\@pathtopage(+1)",
]
NEGATIVE = [
    "use @path for internal links",
    "the @pathto legacy spelling",
    "@pathtofile is an alias",
    "@pathtopage requires an integer",
]


def main() -> int:
    if not JS.exists():
        print(f"check-syntax-highlight FAIL: {JS} not found (run nift build first)")
        return 1
    source = JS.read_text(encoding="utf-8")
    marker = re.compile(r"begin:\s*/(.*?)/\s*},", re.S)
    match = marker.search(source)
    if not match:
        print("check-syntax-highlight FAIL: Nift grammar begin regex not found in script.js")
        return 1
    grammar = re.compile(match.group(1))
    failed = False
    for token in POSITIVE:
        if not grammar.search(token):
            print(f"check-syntax-highlight FAIL: grammar did not match {token!r}")
            failed = True
    for token in NEGATIVE:
        if grammar.search(token):
            print(f"check-syntax-highlight FAIL: grammar matched prose {token!r} (expected no call match)")
            failed = True
    if failed:
        return 1
    print("check-syntax-highlight passed: path family (@path, @pathto, @pathtofile, @pathtopage) recognized")
    return 0


if __name__ == "__main__":
    sys.exit(main())