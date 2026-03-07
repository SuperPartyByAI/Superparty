"""
tests/test_seo_level5_page_metadata_extractor.py — PR #55

Valideaza extractorul read-only de meta description din fisiere Astro:
- maparea URL -> fisier .astro
- extragerea din frontmatter
- extragerea din meta tag HTML
- fallback graceful (file_not_found, nu crash)
- zero side effects pe fisierele sursa
"""
import json
import pytest
from pathlib import Path
import agent.tasks.seo_level5_page_metadata_extractor as extractor_module
from agent.tasks.seo_level5_page_metadata_extractor import (
    url_to_astro_file,
    extract_meta_description_from_file,
    extract_metadata_for_urls,
    enrich_candidates_with_real_metadata,
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def fake_pages(tmp_path, monkeypatch):
    """Creates a fake src/pages directory with 3 test pages."""
    pages = tmp_path / "src" / "pages"
    pages.mkdir(parents=True)

    # Page 1: frontmatter prop style — plain `description = "..."` (no const/let/var)
    _write(pages / "articol-test.astro", """---
import Layout from '../layouts/Layout.astro';
description = "Descriere valida din frontmatter pentru test.";
---
<Layout title="Test" description={description}>
  <p>Continut pagina.</p>
</Layout>
""")


    # Page 2: frontmatter with description = "..."
    _write(pages / "despre-noi.astro", """---
import Layout from '../layouts/Layout.astro';
const title = "Despre Noi";
description = "Descriere explicita despre noi, valida pentru extractor."
---
<Layout title={title} description={description}>
</Layout>
""")

    # Page 3: has meta tag inline
    _write(pages / "contact.astro", """---
import Layout from '../layouts/Layout.astro';
---
<Layout title="Contact">
  <meta name="description" content="Pagina de contact SuperParty - trimite-ne un mesaj." />
</Layout>
""")

    # Page 4: index in subfolder (blog/articol/index.astro)
    _write(pages / "blog" / "articol-nou" / "index.astro", """---
description = "Articol nou din blog - descriere reala pentru test."
---
<p>Content</p>
""")

    monkeypatch.setattr(extractor_module, "PAGES_DIR", pages)
    return pages


# ─── URL to file resolution ───────────────────────────────────────────────────

def test_resolves_direct_astro_file(fake_pages):
    result = url_to_astro_file("/articol-test", fake_pages)
    assert result is not None
    assert result.name == "articol-test.astro"


def test_resolves_index_in_subfolder(fake_pages):
    result = url_to_astro_file("/blog/articol-nou", fake_pages)
    assert result is not None
    assert "index.astro" in str(result)


def test_returns_none_for_nonexistent_url(fake_pages):
    result = url_to_astro_file("/pagina-care-nu-exista", fake_pages)
    assert result is None


def test_returns_none_for_dynamic_route(fake_pages):
    # Dynamic routes like /petreceri/[slug] should not resolve to a static file
    result = url_to_astro_file("/petreceri/bratislava-nonexistent", fake_pages)
    assert result is None


# ─── Description extraction ───────────────────────────────────────────────────

def test_extracts_from_frontmatter_prop(tmp_path):
    page = tmp_path / "test.astro"
    _write(page, """---
description = "Descriere frontmatter directa."
---
<Layout title="Test" description={description}></Layout>
""")
    result = extract_meta_description_from_file(page)
    assert result["meta_description"] == "Descriere frontmatter directa."
    assert result["source"] == "frontmatter_prop"


def test_extracts_from_meta_tag(tmp_path):
    page = tmp_path / "test_meta.astro"
    _write(page, """---
import Layout from '../layouts/Layout.astro';
---
<meta name="description" content="Meta tag extras corect din pagina." />
""")
    result = extract_meta_description_from_file(page)
    assert result["meta_description"] == "Meta tag extras corect din pagina."
    assert result["source"] == "meta_tag"


def test_returns_not_found_when_no_description(tmp_path):
    page = tmp_path / "nodesc.astro"
    _write(page, """---
import Layout from '../layouts/Layout.astro';
const title = "Fara descriere";
---
<Layout title={title}><p>Text</p></Layout>
""")
    result = extract_meta_description_from_file(page)
    assert result["meta_description"] is None
    assert result["source"] == "not_found"


def test_description_length_boundary(tmp_path):
    """Extractor nu trebuie sa returneze descrieri mai lungi de 500 chars (capturate de regex)."""
    long_desc = "X" * 499
    page = tmp_path / "long.astro"
    _write(page, f"""---\ndescription = "{long_desc}"\n---\n""")
    result = extract_meta_description_from_file(page)
    assert result["meta_description"] is not None
    assert len(result["meta_description"]) <= 500


# ─── Batch extraction ────────────────────────────────────────────────────────

def test_batch_extraction_returns_all_urls(fake_pages):
    urls = ["/articol-test", "/contact", "/pagina-inexistenta"]
    results = extract_metadata_for_urls(urls, fake_pages)

    assert set(results.keys()) == set(urls)
    assert results["/articol-test"]["meta_description"] is not None
    assert results["/contact"]["meta_description"] is not None
    assert results["/pagina-inexistenta"]["source"] == "file_not_found"
    assert results["/pagina-inexistenta"]["file_path"] is None


def test_batch_extraction_does_not_modify_source_files(fake_pages, monkeypatch):
    monkeypatch.setattr(extractor_module, "PAGES_DIR", fake_pages)
    page = fake_pages / "articol-test.astro"
    content_before = page.read_text(encoding="utf-8")

    extract_metadata_for_urls(["/articol-test"], fake_pages)

    content_after = page.read_text(encoding="utf-8")
    assert content_before == content_after, "Extractorul nu trebuie sa modifice fisierele sursa"


# ─── Enrich candidates ────────────────────────────────────────────────────────

def test_enrich_candidates_fills_real_description(fake_pages, monkeypatch):
    monkeypatch.setattr(extractor_module, "PAGES_DIR", fake_pages)
    candidates = [
        {"url": "/contact", "tier": "C", "is_money_page": False, "is_pillar_page": False,
         "current_meta_description": "", "reason_flags": ["tier_c_only"], "score": 40.0},
    ]
    enriched = enrich_candidates_with_real_metadata(candidates, fake_pages)
    assert len(enriched) == 1
    assert "SuperParty" in enriched[0]["current_meta_description"]
    assert enriched[0]["meta_extraction_source"] == "meta_tag"


def test_enrich_candidates_preserves_fields(fake_pages, monkeypatch):
    monkeypatch.setattr(extractor_module, "PAGES_DIR", fake_pages)
    candidates = [
        {"url": "/pagina-inexistenta", "tier": "C", "is_money_page": False,
         "is_pillar_page": False, "current_meta_description": "", "reason_flags": [], "score": 0.0},
    ]
    enriched = enrich_candidates_with_real_metadata(candidates, fake_pages)
    assert enriched[0]["tier"] == "C"
    assert enriched[0]["meta_extraction_source"] == "file_not_found"
    assert enriched[0]["current_meta_description"] == ""
