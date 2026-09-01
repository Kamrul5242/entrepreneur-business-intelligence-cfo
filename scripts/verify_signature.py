#!/usr/bin/env python3
"""
verify_signature.py — provenance and integrity checker.

Entrepreneur Business Intelligence & CFO skill
Author:    Md Kamrul Hasan
GitHub:    https://github.com/Kamrul5242
Signature: MKH-EBIC-2.2.3
License:   MIT — attribution required

WHAT THIS DOES
  1. Confirms the author signature is present in every file that should carry it.
  2. Computes a SHA-256 hash of every file and compares it to SIGNATURE.json.
  3. Reports any file that was modified, removed, or stripped of attribution.

WHAT THIS DOES NOT DO
  It cannot prevent removal. These are plain-text files; anyone with an editor
  can delete a line. This tool makes removal *detectable and provable*, which is
  what matters in a licence dispute. Attribution is protected by the MIT
  License, not by software.

USAGE
  python3 scripts/verify_signature.py            # verify against SIGNATURE.json
  python3 scripts/verify_signature.py --generate # regenerate the manifest
"""

import hashlib
import json
import os
import sys

AUTHOR = "Md Kamrul Hasan"
GITHUB = "https://github.com/Kamrul5242"
SIGNATURE = "MKH-EBIC-2.2.3"
VERSION = "2.2.3"
SKILL = "entrepreneur-business-intelligence-cfo"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "SIGNATURE.json")

SKIP_DIRS = {".git", "__pycache__", ".github", "node_modules"}
SKIP_FILES = {"SIGNATURE.json", ".DS_Store"}

# Files required to carry the visible attribution string
MUST_SIGN = (".md", ".py", ".txt", ".mdc")
EXEMPT = {"CHANGELOG.md"}

GREEN, RED, YELL, DIM, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[0m"


def walk():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn in SKIP_FILES:
                continue
            full = os.path.join(dirpath, fn)
            yield os.path.relpath(full, ROOT).replace(os.sep, "/"), full


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def has_attribution(path):
    """True if the file carries the author name or signature ID."""
    if path.lower().endswith(".xlsx"):
        return True  # checked separately via document properties
    try:
        text = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return True
    return ("Md Kamrul Hasan" in text) or (SIGNATURE in text) or ("Kamrul5242" in text)


def check_xlsx(path):
    """Verify the signature survives in the workbook's document properties."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        return None
    try:
        wb = load_workbook(path, read_only=True)
        p = wb.properties
        blob = " ".join(str(x) for x in
                        (p.creator, p.subject, p.description, p.keywords, p.identifier))
        return (AUTHOR in blob) and (SIGNATURE in blob)
    except Exception:
        return None


def generate():
    files = {}
    for rel, full in walk():
        files[rel] = {
            "sha256": sha256(full),
            "bytes": os.path.getsize(full),
            "signed": has_attribution(full),
        }
    manifest = {
        "skill": SKILL,
        "version": VERSION,
        "author": AUTHOR,
        "github": GITHUB,
        "signature": SIGNATURE,
        "license": "MIT — attribution required in all copies",
        "notice": (
            "This manifest records a SHA-256 hash of every file at publication. "
            "Any modification changes the hash and is detected by "
            "verify_signature.py. Removing the attribution does not remove the "
            "author's rights under the MIT License."
        ),
        "file_count": len(files),
        "files": files,
    }
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"{GREEN}Manifest written:{RESET} {MANIFEST}")
    print(f"  {len(files)} files hashed")
    unsigned = [f for f, m in files.items()
                if not m["signed"] and f.endswith(MUST_SIGN) and os.path.basename(f) not in EXEMPT]
    if unsigned:
        print(f"{YELL}  Missing attribution in:{RESET}")
        for f in unsigned:
            print(f"    - {f}")
    return 0


def verify():
    print(f"\n{'='*66}")
    print(f"  SIGNATURE VERIFICATION  ·  {SKILL} v{VERSION}")
    print(f"  Author: {AUTHOR}  ·  {GITHUB}")
    print(f"  Signature ID: {SIGNATURE}")
    print(f"{'='*66}\n")

    if not os.path.exists(MANIFEST):
        print(f"{RED}FAIL{RESET}  SIGNATURE.json not found — cannot verify integrity.")
        print(f"      Run: python3 scripts/verify_signature.py --generate")
        return 2

    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    recorded = manifest["files"]
    current = {rel: full for rel, full in walk()}

    modified, missing, added, stripped = [], [], [], []

    for rel, meta in recorded.items():
        if rel not in current:
            missing.append(rel)
            continue
        if sha256(current[rel]) != meta["sha256"]:
            modified.append(rel)
        if meta.get("signed") and not has_attribution(current[rel]):
            stripped.append(rel)

    for rel in current:
        if rel not in recorded:
            added.append(rel)

    xlsx_ok = []
    for rel, full in current.items():
        if rel.lower().endswith(".xlsx"):
            r = check_xlsx(full)
            xlsx_ok.append((rel, r))

    print(f"  Files recorded : {len(recorded)}")
    print(f"  Files present  : {len(current)}\n")

    ok = True
    if stripped:
        ok = False
        print(f"{RED}  ATTRIBUTION REMOVED — {len(stripped)} file(s){RESET}")
        for f in stripped:
            print(f"    ✗ {f}")
        print(f"{RED}    This violates the MIT License attribution requirement.{RESET}\n")

    if modified:
        ok = False
        print(f"{YELL}  MODIFIED — {len(modified)} file(s){RESET}")
        for f in modified:
            print(f"    ~ {f}")
        print()

    if missing:
        ok = False
        print(f"{RED}  MISSING — {len(missing)} file(s){RESET}")
        for f in missing:
            print(f"    ✗ {f}")
        print()

    if added:
        print(f"{DIM}  ADDED (not in manifest) — {len(added)} file(s){RESET}")
        for f in added:
            print(f"    + {f}")
        print()

    for rel, r in xlsx_ok:
        if r is None:
            print(f"{DIM}  ? {rel} — openpyxl unavailable, workbook properties unchecked{RESET}")
        elif r:
            print(f"{GREEN}  ✓ {rel} — signature intact in document properties{RESET}")
        else:
            ok = False
            print(f"{RED}  ✗ {rel} — signature stripped from document properties{RESET}")
    if xlsx_ok:
        print()

    if ok and not modified and not missing:
        print(f"{GREEN}  RESULT: VERIFIED{RESET}")
        print(f"  Every file matches its recorded hash and carries the author signature.\n")
        return 0

    print(f"{RED}  RESULT: TAMPERED{RESET}")
    print(f"  This copy differs from the published release by {AUTHOR}.")
    print(f"  Authentic source: {GITHUB}\n")
    return 1


if __name__ == "__main__":
    if "--generate" in sys.argv or "-g" in sys.argv:
        sys.exit(generate())
    sys.exit(verify())
