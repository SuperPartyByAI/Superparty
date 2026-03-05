#!/usr/bin/env python3
"""
fix_mojibake_ro.py — repair mojibake encoding in superparty_testimonials.json
and optionally in SEO content files.

Usage:
    python scripts/fix_mojibake_ro.py [--check] [--apply]
    --check : only detect and report, do not write
    --apply : detect and fix in-place

Mojibake detection: strings that contain latin1-misinterpreted UTF-8 chars
(e.g. "BucureÈ™ti" instead of "București", "Ã®n" instead of "în")
"""
import json
import sys
import re
from pathlib import Path

# Known mojibake patterns: detect that cp1252→utf8 fix is needed
MOJIBAKE_PATTERNS = re.compile(
    r"(BucureÈ|PÄ|mulÈ|Ã.|Â.|â€.|È™|È›|Å£|ÅŸ)"
)

def fix_mojibake(s: str, max_iter: int = 3) -> str:
    """Try to fix mojibake by re-encoding cp1252→utf-8, up to max_iter times."""
    if not isinstance(s, str):
        return s
    prev = s
    for _ in range(max_iter):
        try:
            fixed = prev.encode("cp1252").decode("utf-8")
            if fixed == prev:
                break
            prev = fixed
        except (UnicodeDecodeError, UnicodeEncodeError):
            break
    return prev


def has_mojibake(s: str) -> bool:
    return bool(MOJIBAKE_PATTERNS.search(s)) if isinstance(s, str) else False


def fix_dict(d: dict | list) -> dict | list:
    """Recursively fix mojibake in all string values of a dict or list."""
    if isinstance(d, dict):
        return {k: fix_dict(v) for k, v in d.items()}
    if isinstance(d, list):
        return [fix_dict(item) for item in d]
    if isinstance(d, str):
        return fix_mojibake(d)
    return d


def check_file(path: Path) -> int:
    """Return count of entries with mojibake."""
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else [data]
    count = sum(1 for item in items if has_mojibake(json.dumps(item, ensure_ascii=False)))
    return count


def apply_file(path: Path) -> tuple[int, int]:
    """Fix mojibake in JSON file. Returns (total, fixed)."""
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    items = data if isinstance(data, list) else [data]
    total = len(items)
    fixed_count = 0

    fixed_data = []
    for item in items:
        item_str = json.dumps(item, ensure_ascii=False)
        fixed_item = fix_dict(item)
        fixed_str = json.dumps(fixed_item, ensure_ascii=False)
        if item_str != fixed_str:
            fixed_count += 1
        fixed_data.append(fixed_item)

    output = json.dumps(fixed_data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(output, encoding="utf-8")
    return total, fixed_count


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix mojibake in repo JSON/content files")
    parser.add_argument("--check", action="store_true", help="Only check, don't fix")
    parser.add_argument("--apply", action="store_true", help="Fix in-place (default if no flag)")
    args = parser.parse_args()

    do_apply = args.apply or (not args.check)

    repo = Path(__file__).parent.parent
    targets = [
        repo / "src" / "data" / "superparty_testimonials.json",
    ]

    found_any = False
    for path in targets:
        if not path.exists():
            print(f"SKIP (not found): {path}")
            continue

        count = check_file(path)
        if count == 0:
            print(f"OK (no mojibake): {path.name}")
            continue

        found_any = True
        print(f"MOJIBAKE: {count} entries in {path.name}")

        if do_apply:
            total, fixed = apply_file(path)
            print(f"  FIXED {fixed}/{total} entries → {path.name}")
        else:
            print(f"  (run with --apply to fix)")

    # Also scan SEO articles for mojibake
    seo_dir = repo / "src" / "content" / "seo-articles"
    if seo_dir.exists():
        mdx_files = list(seo_dir.rglob("*.mdx")) + list(seo_dir.rglob("*.md"))
        moji_files = []
        for f in mdx_files:
            content = f.read_text(encoding="utf-8", errors="replace")
            if MOJIBAKE_PATTERNS.search(content):
                moji_files.append(f)

        if moji_files:
            found_any = True
            print(f"\nMOJIBAKE in {len(moji_files)} SEO articles:")
            for f in moji_files:
                print(f"  {f.relative_to(repo)}")
                if do_apply:
                    raw = f.read_text(encoding="utf-8", errors="replace")
                    fixed = fix_mojibake(raw)
                    f.write_text(fixed, encoding="utf-8")
                    print(f"    → FIXED")
        else:
            print(f"\nOK: no mojibake in {len(mdx_files)} SEO article files")

    if not found_any:
        print("\nAll clean — no mojibake found.")
    elif not do_apply:
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
