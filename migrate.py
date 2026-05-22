#!/usr/bin/env python3
"""
Path-rewrite pass for the euclids-elements.org content site.

Run from the repo root after the publishable subset has been copied in from
djoyce/converted/.  Walks every *.html file under elements/ and geomlib/ and
applies the rewrites in REWRITES below.

Rules are intentionally precise so a future re-run (e.g., bumping geomlib to
a new version) is mechanical.  Adjust GEOMLIB_VERSION at the top, re-run.

Idempotent: running twice does nothing the second time, because each rewrite
moves a source pattern to a unique target.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

GEOMLIB_VERSION = "0.1.0"
GEOMLIB_CDN = (
    f"https://unpkg.com/@brownnrl/geomlib@{GEOMLIB_VERSION}/dist/bundle.js"
)

# Each tuple is (description, compiled-regex, replacement).
# Order matters when multiple patterns could match the same input — earlier
# rules win.
REWRITES: list[tuple[str, re.Pattern[str], str]] = [
    # --- geomlib bundle: any relative path to geometry.bundle.js -> unpkg CDN
    (
        "geomlib bundle -> CDN",
        re.compile(r'(\.\./)+js/geometry\.bundle\.js'),
        GEOMLIB_CDN,
    ),
    # --- elements pages reference ../elements.css and ../elements.js
    (
        "../elements.css -> /css/style.css",
        re.compile(r'\.\./elements\.css'),
        '/css/style.css',
    ),
    (
        "../elements.js -> /js/header-footer.js",
        re.compile(r'\.\./elements\.js'),
        '/js/header-footer.js',
    ),
    # Same css/js refs from pages at elements/ root (no `../` prefix)
    (
        "elements.css (local) -> /css/style.css",
        re.compile(r'(href="|href=)elements\.css(")?'),
        r'\1/css/style.css\2',
    ),
    (
        "elements.js (local) -> /js/header-footer.js",
        re.compile(r'(src="|src=)elements\.js(")?'),
        r'\1/js/header-footer.js\2',
    ),
    # --- absolute aleph0.clarku.edu URLs into the *Elements* tree
    # rewrite to the local /elements/<path>, dropping the java/ prefix
    (
        "clarku java/elements -> /elements",
        re.compile(
            r'https?://aleph0\.clarku\.edu/~djoyce/java/elements/([^"\'\s>]+)'
        ),
        r'/elements/\1',
    ),
    (
        "clarku elements (non-java) -> /elements",
        re.compile(
            r'https?://aleph0\.clarku\.edu/~djoyce/elements/([^"\'\s>]+)'
        ),
        r'/elements/\1',
    ),
    # --- compass + round under /geomlib/
    (
        "clarku java/compass -> /geomlib/compass",
        re.compile(
            r'https?://aleph0\.clarku\.edu/~djoyce/java/compass/([^"\'\s>]+)'
        ),
        r'/geomlib/compass/\1',
    ),
    (
        "clarku java/round -> /geomlib/round",
        re.compile(
            r'https?://aleph0\.clarku\.edu/~djoyce/java/round/([^"\'\s>]+)'
        ),
        r'/geomlib/round/\1',
    ),
    # --- compass/round pages currently link siblingwise to ../elements/...
    # That was correct in the old layout (java/compass + java/elements siblings).
    # In the new layout, compass lives at /geomlib/compass/ and elements at
    # /elements/, so the sibling reference resolves to /geomlib/elements/ which
    # is wrong.  Rewrite to root-relative /elements/.
    (
        "../elements/ (cross-section sibling ref) -> /elements/",
        re.compile(r'\.\./elements/'),
        '/elements/',
    ),
    # --- usingApplet.html -> usingGeomlib.html where it's been renamed
    # (only the /geomlib/ copy was renamed; the /elements/usingApplet.html
    # stays at its original name for inbound-link continuity)
    (
        "/geomlib/usingApplet.html -> usingGeomlib.html",
        re.compile(r'/geomlib/usingApplet\.html\b'),
        '/geomlib/usingGeomlib.html',
    ),
    # --- "Geometry Applet" link target -> our /geomlib/ landing page
    # Inline references like "this figure utilizes the [Geometry Applet]" used
    # to link to Joyce's applet doc at clarku.  Those are now broken — we point
    # them at our own /geomlib/ explanation instead.
    (
        "clarku Geometry Applet page -> /geomlib/",
        re.compile(
            r'https?://aleph0\.clarku\.edu/~djoyce/java/Geometry/Geometry\.html'
        ),
        '/geomlib/',
    ),
]


def walk_html_files(root: Path) -> list[Path]:
    """Return every *.html under elements/ and geomlib/."""
    targets: list[Path] = []
    for sub in ("elements", "geomlib"):
        targets.extend((root / sub).rglob("*.html"))
    return sorted(targets)


def apply_rewrites(text: str) -> tuple[str, list[str]]:
    """Apply every rule in REWRITES to `text`. Return (new_text, descriptions of rules that fired)."""
    fired: list[str] = []
    for desc, pat, repl in REWRITES:
        new_text, n = pat.subn(repl, text)
        if n > 0:
            fired.append(f"  - {desc} ({n}x)")
            text = new_text
    return text, fired


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change without writing.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="only print per-file summary, not each rule that fired.",
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parent
    files = walk_html_files(root)
    print(f"Found {len(files)} HTML files to scan under elements/ + geomlib/.")

    total_changed = 0
    for fp in files:
        original = fp.read_text(encoding="utf-8", errors="replace")
        rewritten, fired = apply_rewrites(original)

        if rewritten != original:
            total_changed += 1
            rel = fp.relative_to(root)
            action = "would rewrite" if args.dry_run else "rewrote"
            print(f"{action} {rel}")
            if not args.quiet:
                for line in fired:
                    print(line)
            if not args.dry_run:
                fp.write_text(rewritten, encoding="utf-8")

    print()
    verb = "would change" if args.dry_run else "changed"
    print(f"{verb} {total_changed} / {len(files)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
