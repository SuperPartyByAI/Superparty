"""
SEO Level 5 — Page Metadata Extractor (PR #55)

Read-only extractor that reads meta description from local Astro source files.
NO file writes. NO mutations. NO network requests.

Supports:
1. Astro frontmatter props (description = "..." or description: "...")
2. Inline <meta name="description" content="..."> in Astro template body
3. Layout prop pass-through (description={description} in JSX)

Output: dict { url -> { "meta_description": str|None, "source": str, "file_path": str|None } }
"""

from __future__ import annotations

import re
import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# Repo root — resolver assumes this module lives at agent/tasks/
ROOT_DIR = Path(__file__).parent.parent.parent
PAGES_DIR = ROOT_DIR / "src" / "pages"

# ─── URL → File Resolution ─────────────────────────────────────────────────────

def url_to_astro_file(url: str, pages_dir: Path = PAGES_DIR) -> Optional[Path]:
    """
    Maps a URL path to the most likely Astro source file.

    Examples:
        /blog/test-article  → src/pages/blog/test-article.astro
                            → src/pages/blog/test-article/index.astro
        /                   → src/pages/index.astro

    Returns None if no file is found (dynamic route, external, etc.)
    No file is written or mutated.
    """
    slug = url.strip("/")

    # Root path
    if not slug:
        candidate = pages_dir / "index.astro"
        return candidate if candidate.exists() else None

    # Try direct file: slug.astro
    direct = pages_dir / f"{slug}.astro"
    if direct.exists():
        return direct

    # Try index file: slug/index.astro
    index = pages_dir / slug / "index.astro"
    if index.exists():
        return index

    # Try nested segments
    parts = slug.split("/")
    if len(parts) > 1:
        nested_direct = pages_dir.joinpath(*parts[:-1]) / f"{parts[-1]}.astro"
        if nested_direct.exists():
            return nested_direct
        nested_index = pages_dir.joinpath(*parts) / "index.astro"
        if nested_index.exists():
            return nested_index

    return None


# ─── Meta Description Parsers ─────────────────────────────────────────────────

# Astro frontmatter prop patterns:
#   description = "..."   or   description: "..."  or  description = '...'
_RE_FRONTMATTER_PROP = re.compile(
    r"""^\s*description\s*[=:]\s*['"]([^'"]{0,500})['"]""",
    re.MULTILINE,
)

# Inline <meta name="description" content="..."> in Astro template
_RE_META_TAG = re.compile(
    r"""<meta\s+name=["']description["']\s+content=["']([^"']{0,500})["']""",
    re.IGNORECASE,
)

# Astro Layout prop: description={description} or description={"literal value"}
_RE_LAYOUT_PROP_VAR = re.compile(
    r"""<Layout[^>]+description=\{([^}]+)\}""",
    re.IGNORECASE | re.DOTALL,
)


def _extract_frontmatter_block(content: str) -> Optional[str]:
    """Return the content between the first pair of --- fences, or None."""
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    return m.group(1) if m else None


def extract_meta_description_from_file(file_path: Path) -> dict:
    """
    Read-only extraction of meta description from a single Astro file.
    Returns:
        { "meta_description": str|None, "source": str, "file_path": str }
    source is one of: "frontmatter_prop", "meta_tag", "not_found"
    """
    result = {
        "meta_description": None,
        "source": "not_found",
        "file_path": str(file_path),
    }

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        log.warning("Cannot read %s: %s", file_path, e)
        result["source"] = "read_error"
        return result

    # 1. Check frontmatter for `description = "..."` or `description: "..."`
    fm_block = _extract_frontmatter_block(content)
    if fm_block:
        m = _RE_FRONTMATTER_PROP.search(fm_block)
        if m:
            result["meta_description"] = m.group(1).strip()
            result["source"] = "frontmatter_prop"
            return result

    # 2. Check for inline <meta name="description" content="..."> in the template body
    m = _RE_META_TAG.search(content)
    if m:
        result["meta_description"] = m.group(1).strip()
        result["source"] = "meta_tag"
        return result

    # 3. Layout prop used with a string literal: description={"actual text here"}
    m = _RE_LAYOUT_PROP_VAR.search(content)
    if m:
        inner = m.group(1).strip()
        # Only accept if it looks like a string literal (starts with ' or ")
        lit = re.match(r"""['"](.*?)['"]""", inner, re.DOTALL)
        if lit:
            result["meta_description"] = lit.group(1).strip()
            result["source"] = "layout_prop_literal"
            return result

    return result


# ─── Batch Extractor ──────────────────────────────────────────────────────────

def extract_metadata_for_urls(
    urls: list[str],
    pages_dir: Path = PAGES_DIR,
) -> dict[str, dict]:
    """
    Given a list of URL paths, extract meta description from their Astro source files.
    Returns a dict: { url -> extraction_result }

    Extraction result:
        { "meta_description": str|None, "source": str, "file_path": str|None }

    This function is STRICTLY read-only. It does not write, commit, or modify anything.
    """
    results: dict[str, dict] = {}

    for url in urls:
        file_path = url_to_astro_file(url, pages_dir)

        if file_path is None:
            results[url] = {
                "meta_description": None,
                "source": "file_not_found",
                "file_path": None,
            }
            log.debug("No Astro file found for URL: %s", url)
            continue

        results[url] = extract_meta_description_from_file(file_path)
        log.debug(
            "Extracted for %s [%s]: %s",
            url,
            results[url]["source"],
            (results[url]["meta_description"] or "")[:60],
        )

    return results


# ─── Public API ───────────────────────────────────────────────────────────────

def enrich_candidates_with_real_metadata(
    candidates: list[dict],
    pages_dir: Path = PAGES_DIR,
) -> list[dict]:
    """
    Takes a list of candidate dicts (from seo_level5_meta_description_dry_run.py)
    and enriches them with the real current_meta_description from source files.

    Returns the enriched list. Does NOT mutate source files.
    Input candidates are expected to have a `url` field.
    """
    urls = [c["url"] for c in candidates if "url" in c]
    extracted = extract_metadata_for_urls(urls, pages_dir)

    enriched = []
    for candidate in candidates:
        url = candidate.get("url", "")
        meta_info = extracted.get(url, {
            "meta_description": None,
            "source": "not_extracted",
            "file_path": None,
        })
        enriched_candidate = dict(candidate)
        enriched_candidate["current_meta_description"] = meta_info["meta_description"] or ""
        enriched_candidate["meta_extraction_source"] = meta_info["source"]
        enriched_candidate["meta_file_path"] = meta_info["file_path"]
        enriched.append(enriched_candidate)

    return enriched


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Quick smoke test against real pages dir
    test_urls = [
        "/animatori-petreceri-copii",
        "/arie-acoperire",
        "/petreceri/bucuresti",
        "/blog/test-nonexistent",
    ]
    results = extract_metadata_for_urls(test_urls)
    import json
    print(json.dumps(results, indent=2, ensure_ascii=False))
