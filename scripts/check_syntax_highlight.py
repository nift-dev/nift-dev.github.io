#!/usr/bin/env python3
"""Verify the website's Nift syntax highlighter recognizes modern Nift and
command-style shell syntax without false positives in prose/CSS.

The static highlighter lives in public/assets/js/script.js. Positive tokens
must match at least one grammar rule. False-positive checks are scoped to the
rule families where prose/CSS collisions actually matter: the @-directive meta
rule (must not match @media/@path-without-call/email) and the comment rules
(must match @// and @/* */ but not // or #).

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
    "@script",
    "@import('sqlite')",
    "@import('./local.f')",
    "@fn(public_add(a, b))",
    "@fragment(x)",
    "@if(cond)",
    "@for(item : items)",
    "@content",
    "$[x]",
    "$[row.name]",
    "run",
    "cmd",
    "x := 5",
    "...args",
    "...xs",
    "(x) => x * 2",
    "|",
    ">",
    ">>",
    "2>",
    "2>&1",
    "&&",
    "||",
    "@// single-line Nift comment",
    "@/* block\n   comment */",
    "// single-line script-land comment",
    "/* block\n   comment */",
    "fn(double(x)) {",
    "minify(\"assets/app.js\", {\"output\": \"app.min.js\"})",
]

# Tokens that must NOT be treated as Nift @-directives.
DIRECTIVE_NEGATIVE = [
    "use @path for internal links",
    "the @pathto legacy spelling",
    "@pathtofile is an alias",
    "@pathtopage requires an integer",
    "@media (max-width: 600px)",
    "a@b.com",
    "email me at someone@example.com",
]

# Prose/CSS that must NOT be treated as Nift comments. These are checked
# against the template comment rules (@// and @/* ... */); they never start
# with '@' so they must stay unmatched.
COMMENT_NEGATIVE = [
    "background: url(https://example.com/a.png)",
    "color: #ffffff",
    "href=\"#anchor\"",
    "//# sourceMappingURL=app.js.map",
]

# Script-land bare comments (// and /* */) are now real Nift comments. URLs
# carry a scheme before '//' and must not be colored as comments.
BARE_COMMENT_NEGATIVE = [
    "https://example.com/a.png",
    "http://localhost:8000",
    "ftp://host/path",
    "git@github.com:user/repo.git",
]


def begin_patterns(source: str):
    """Return the list of highlighter begin regexes (as raw JS-regex strings)."""
    out = []
    idx = 0
    while True:
        start = source.find("begin:", idx)
        if start < 0:
            break
        delim = source.find("/", start)
        if delim < 0:
            break
        i = delim + 1
        body = []
        while i < len(source):
            c = source[i]
            if c == "\\" and i + 1 < len(source):
                body.append(source[i : i + 2])
                i += 2
                continue
            if c == "/":
                break
            body.append(c)
            i += 1
        out.append("".join(body))
        idx = i + 1
    return out


def main() -> int:
    if not JS.exists():
        print(f"check-syntax-highlight FAIL: {JS} not found (run nift build first)")
        return 1
    source = JS.read_text(encoding="utf-8")
    if "registerLanguage('nift'" not in source:
        print("check-syntax-highlight FAIL: nift language not found in script.js")
        return 1
    patterns = begin_patterns(source)
    if not patterns:
        print("check-syntax-highlight FAIL: no nift grammar begin regexes found in script.js")
        return 1
    grammars = [re.compile(p) for p in patterns if p]
    # The first grammar rule is the @-directive family. The final four are the
    # Nift comment rules: bare script-land // and /* */ (positions -4,-3) then
    # the template @// and @/* */ forms (positions -2,-1).
    directive = grammars[0]
    bare_comments = grammars[-4:-2]
    template_comments = grammars[-2:]
    failed = False

    def matches_any(token):
        return any(g.search(token) for g in grammars)

    for token in POSITIVE:
        if not matches_any(token):
            print(f"check-syntax-highlight FAIL: grammar did not match {token!r}")
            failed = True
    for token in DIRECTIVE_NEGATIVE:
        if directive.search(token):
            print(f"check-syntax-highlight FAIL: directive rule matched prose {token!r}")
            failed = True
    for token in COMMENT_NEGATIVE:
        for g in template_comments:
            if g.search(token):
                print(f"check-syntax-highlight FAIL: comment rule matched prose {token!r}")
                failed = True
    for token in BARE_COMMENT_NEGATIVE:
        for g in bare_comments:
            if g.search(token):
                print(f"check-syntax-highlight FAIL: bare comment rule matched {token!r}")
                failed = True
    if failed:
        return 1
    print("check-syntax-highlight passed: modern Nift + shell grammar recognized")
    return 0


if __name__ == "__main__":
    sys.exit(main())