#!/usr/bin/env python3
"""
release_version.py — bump the version without rewriting history.

WHY THIS EXISTS
  Releases were cut with a repository-wide replacement of the old version
  string. Three times that rewrote historical prose: README said the font
  defect was "fixed in v2.2.1" when it shipped in v2.2.0, and test docstrings
  said "before v2.2.2" for defects fixed in v2.2.1. A green suite hid it every
  time, because nothing distinguished a CURRENT DECLARATION from a HISTORICAL
  REFERENCE.

THE DISTINCTION
  Current declaration - states what this release IS. It carries the
    `MKH-EBIC-<version>` signature token, or sits in one of the registered
    fields below. These are the only strings a bump may touch.

  Historical reference - states what a PAST release did: "fixed in v2.2.0",
    "before v2.2.1", "pre-v2.2.2", and every CHANGELOG entry. A bump must
    never touch these.

  The separation holds because no historical sentence in this repository uses
  the `MKH-EBIC-` token, and CHANGELOG.md is excluded from bumping entirely.

USAGE
    python3 scripts/release_version.py --check         # validate, change nothing
    python3 scripts/release_version.py --bump 2.2.5    # targeted bump

`--check` runs in CI and in scripts/test_reference_consistency.py. It fails if
a declaration disagrees, if a historical reference cites the current version or
newer, or if the previous version is still declared outside the CHANGELOG.

Author: Md Kamrul Hasan
GitHub: https://github.com/Kamrul5242
License: MIT
Signature: MKH-EBIC-2.2.7
"""

import argparse
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

VER = r"\d+\.\d+\.\d+"

# Bare-version fields. Each regex captures (prefix)(version)(suffix).
FIELD_SITES = [
    ("SKILL.md",                    r"(?m)^(\s*version:\s*)(%s)(\s*)$" % VER),
    ("SKILL.md",                    r"(CFO v)(%s)( )" % VER),
    ("README.md",                   r"(badge/version-)(%s)(-blue)" % VER),
    ("CITATION.cff",                r'(?m)^(version:\s*")(%s)(")' % VER),
    ("llms.txt",                    r"(Current version:\s*)(%s)(\.)" % VER),
    ("scripts/verify_signature.py", r'(VERSION = ")(%s)(")' % VER),
    ("scripts/build_dashboard.py",  r'(\("Version",")(%s)(")' % VER),
]

# The signature token is always a current declaration, never historical prose.
TOKEN_FORMS = ("MKH-EBIC-%s", "MKH--EBIC--%s")   # the second is the README badge

# Phrases that introduce a statement about the past.
HISTORICAL = re.compile(
    r"(?:before|pre-|prior to|fixed in|introduced in|added in|changed in|"
    r"shipped in|regressed in|in)\s+v(%s)" % VER, re.IGNORECASE)

NEVER_BUMP = {"CHANGELOG.md"}
BINARY = (".png", ".xlsx", ".pyc")


def tracked_files():
    """Tracked files plus anything staged or newly added.

    A script introduced in the same release is still untracked when the bump
    runs, so `git ls-files` alone silently skips it and it keeps the previous
    signature. That happened to this very file during the release that
    introduced it, and was caught only by the clean-clone gate.
    """
    seen = subprocess.run(["git", "-C", ROOT, "ls-files"],
                          capture_output=True, text=True).stdout.split()
    extra = subprocess.run(
        ["git", "-C", ROOT, "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True).stdout.split()
    out = []
    for f in seen + extra:
        if os.path.splitext(f)[1] in BINARY:
            continue
        if f not in out and os.path.exists(os.path.join(ROOT, *f.split("/"))):
            out.append(f)
    return out


def read(rel):
    with io.open(os.path.join(ROOT, *rel.split("/")), encoding="utf-8",
                 newline="") as fh:
        return fh.read()


def write(rel, text):
    with io.open(os.path.join(ROOT, *rel.split("/")), "w", encoding="utf-8",
                 newline="") as fh:
        fh.write(text)


def parse(v):
    return tuple(int(p) for p in v.split("."))


def current_version():
    m = re.search(r"(?m)^\s*version:\s*(%s)\s*$" % VER, read("SKILL.md"))
    if not m:
        raise SystemExit("SKILL.md declares no version")
    return m.group(1)


def changelog_versions():
    return re.findall(r"(?m)^##\s*(%s)" % VER, read("CHANGELOG.md"))


def declarations():
    """Every current-version declaration found, as {location: version}."""
    found = {}
    for rel, pattern in FIELD_SITES:
        for i, m in enumerate(re.finditer(pattern, read(rel))):
            found["%s [field %d]" % (rel, i)] = m.group(2)
    for rel in tracked_files():
        if rel in NEVER_BUMP:
            continue
        text = read(rel)
        for form in TOKEN_FORMS:
            token = form % ""
            for m in re.finditer(re.escape(token) + r"(%s)" % VER, text):
                found["%s [%s]" % (rel, token)] = m.group(1)
    return found


def check(verbose=True):
    """Return a list of problems; empty means the release is consistent."""
    problems = []
    current = current_version()
    known = changelog_versions()

    if current not in known:
        problems.append("CHANGELOG has no entry for the current version %s"
                        % current)

    for loc, v in sorted(declarations().items()):
        if v != current:
            problems.append("declaration disagrees: %s says %s, current is %s"
                            % (loc, v, current))

    # A statement about the past may not cite this release or a later one.
    for rel in tracked_files():
        if rel in NEVER_BUMP:
            continue
        for line_no, line in enumerate(read(rel).split("\n"), 1):
            for cited in HISTORICAL.findall(line):
                if parse(cited) >= parse(current):
                    problems.append(
                        "%s:%d cites v%s as history, but the current version is "
                        "%s - a sweep has rewritten a historical reference"
                        % (rel, line_no, cited, current))

    # The previous release must not still be declared anywhere.
    older = [v for v in known if parse(v) < parse(current)]
    if older:
        previous = max(older, key=parse)
        for rel in tracked_files():
            if rel in NEVER_BUMP:
                continue
            for line_no, line in enumerate(read(rel).split("\n"), 1):
                for form in TOKEN_FORMS:
                    if (form % previous) in line:
                        problems.append(
                            "%s:%d still declares the previous version %s"
                            % (rel, line_no, previous))

    if verbose:
        for p in problems:
            print("  FAIL " + p)
        if not problems:
            kept = sum(len(HISTORICAL.findall(read(r))) for r in tracked_files()
                       if r not in NEVER_BUMP)
            print("  declarations consistent at %s; %d historical references "
                  "left untouched" % (current, kept))
    return problems


def bump(new):
    old = current_version()
    if parse(new) <= parse(old):
        raise SystemExit("refusing to bump %s -> %s: not an increase" % (old, new))
    touched = set()

    for rel, pattern in FIELD_SITES:
        text = read(rel)
        updated = re.sub(pattern, lambda m: m.group(1) + new + m.group(3), text)
        if updated != text:
            write(rel, updated)
            touched.add(rel)

    for rel in tracked_files():
        if rel in NEVER_BUMP:
            continue
        text = read(rel)
        updated = text
        for form in TOKEN_FORMS:
            updated = updated.replace(form % old, form % new)
        if updated != text:
            write(rel, updated)
            touched.add(rel)

    print("bumped %s -> %s across %d files; CHANGELOG and every historical "
          "reference untouched" % (old, new, len(touched)))
    return old


def main():
    ap = argparse.ArgumentParser(
        description="Targeted version bump and release validator.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true",
                   help="validate declarations and history; change nothing")
    g.add_argument("--bump", metavar="X.Y.Z",
                   help="update only registered declaration sites")
    a = ap.parse_args()

    if a.bump:
        bump(a.bump)
        print("validating:")
    return 1 if check() else 0


if __name__ == "__main__":
    sys.exit(main())
