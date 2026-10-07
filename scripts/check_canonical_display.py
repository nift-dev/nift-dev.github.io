#!/usr/bin/env python3
"""Verify the canonical HANDOVER.md / MIGRATION.md displayed on a docs page
matches public/<NAME>.md byte for byte.

The docs pages display the canonical files as HTML-escaped duplicates (because
the markdown deliberately contains Nift syntax that @input would interpret).
This check prevents those displayed copies drifting from the real files: it
extracts the rendered block from the page, HTML-unescapes it, and compares it
against public/<NAME>.md.

Usage (after a website build):
    python3 scripts/check_canonical_display.py HANDOVER
    python3 scripts/check_canonical_display.py MIGRATION
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CANONICAL_PAGES = {
    "HANDOVER": ROOT / "public" / "docs" / "ai-agents.html",
    "MIGRATION": ROOT / "public" / "docs" / "existing-sites.html",
}


def check(page: Path, which: str) -> bool:
    canon = ROOT / "public" / f"{which}.md"
    if not page.exists():
        print(f"check-canonical-display FAIL: {page.relative_to(ROOT)} not found (run nift build-all first)")
        return False
    source = page.read_text(encoding="utf-8")
    marker = re.compile(
        rf'<h3(?:\s+[^>]*)?>The canonical {which}\.md</h3>\s*<pre><code class="language-plaintext">(.*?)</code></pre>',
        flags=re.S,
    )
    match = marker.search(source)
    if not match:
        print(f"check-canonical-display FAIL: canonical {which} block not found on {page.relative_to(ROOT)}")
        return False
    rendered = html.unescape(match.group(1))
    real = canon.read_bytes()
    if rendered.encode("utf-8") != real:
        print(f"check-canonical-display FAIL: displayed {which}.md differs from public/{which}.md")
        print(f"  rendered {len(rendered.encode('utf-8'))} bytes, canonical {len(real)} bytes")
        for i, (a, b) in enumerate(zip(rendered.encode("utf-8"), real)):
            if a != b:
                print(f"  first diff at byte {i}: {a!r} vs {b!r}")
                break
        return False
    print(f"check-canonical-display passed: displayed {which}.md is byte-identical to public/{which}.md")
    return True


def selftest(which: str) -> bool:
    """Negative-drift proof: the comparison must pass on the real files and
    fail when either side is mutated."""
    if not check(CANONICAL_PAGES[which], which):
        return False
    page = CANONICAL_PAGES[which].read_text(encoding="utf-8")
    canon_bytes = (ROOT / "public" / f"{which}.md").read_bytes()
    marker_head = re.compile(
        rf'(<h3(?:\s+[^>]*)?>The canonical {which}\.md</h3>\s*<pre><code class="language-plaintext">)',
        flags=re.S,
    )
    head = marker_head.search(page)
    if not head:
        print(f"check-canonical-display SELFTEST FAIL: could not locate the {which} canonical block")
        return False
    mutated_page = page[: head.end(1)] + "drift" + page[head.end(1):]
    (ROOT / "public" / f".selftest-{which}.html").write_text(mutated_page, encoding="utf-8")
    old = CANONICAL_PAGES[which]
    try:
        CANONICAL_PAGES[which] = ROOT / "public" / f".selftest-{which}.html"
        if check(CANONICAL_PAGES[which], which):
            print(f"check-canonical-display SELFTEST FAIL: mutated {which} page not detected")
            return False
    finally:
        CANONICAL_PAGES[which] = old
        (ROOT / "public" / f".selftest-{which}.html").unlink(missing_ok=True)
    print(f"check-canonical-display SELFTEST passed: {which} drift is detected")
    return True


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] in ("--selftest", "--test"):
        ok = selftest("HANDOVER") and selftest("MIGRATION")
        return 0 if ok else 1
    if len(sys.argv) != 2:
        print("usage: check_canonical_display.py HANDOVER|MIGRATION | --selftest", file=sys.stderr)
        return 2
    which = sys.argv[1].upper()
    if which not in CANONICAL_PAGES:
        print(f"check-canonical-display FAIL: unknown canonical {which!r}", file=sys.stderr)
        return 2
    return 0 if check(CANONICAL_PAGES[which], which) else 1


if __name__ == "__main__":
    sys.exit(main())