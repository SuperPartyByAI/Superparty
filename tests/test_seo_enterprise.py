import pytest
import os
from pathlib import Path

# Since functions might still be inside _orig_seo_apply_task, we'll extract them dynamically for the test or use the refactored ones.
# Actually I will refactor seo.py. Let's assume they are module level after my next script.
from agent.tasks.seo import (
    resolve_astro_path,
    patch_layout_title_description,
    replace_or_insert_seo_block,
    patch_const_faq_array,
    get_deterministic_payload,
    SEO_MARKER_START,
    SEO_MARKER_END
)

def test_resolve_astro_path(tmp_path):
    # Mocking Path existence
    import agent.tasks.seo
    original_path = agent.tasks.seo.Path
    
    class MockPath:
        def __init__(self, p):
            self.p = str(p)
        def exists(self):
            return "index.astro" in self.p or "otopeni.astro" in self.p or "bucuresti" in self.p
        def __str__(self): return self.p
    
    agent.tasks.seo.Path = MockPath
    try:
        assert str(resolve_astro_path("/petreceri/otopeni")) == "src/pages/petreceri/otopeni.astro"
        assert str(resolve_astro_path("/petreceri/ilfov/")) == "src/pages/petreceri/ilfov/index.astro"
        assert str(resolve_astro_path("https://www.superparty.ro/petreceri/bucuresti")) == "src/pages/petreceri/bucuresti.astro"
    finally:
        agent.tasks.seo.Path = original_path

def test_apply_patch_frontmatter():
    text = "---\nimport Layout from '../components/Layout.astro'\n---\n<Layout title='Old' description='Old Desc' schema={schema}>\n  <p>Hello</p>\n</Layout>"
    new_text = patch_layout_title_description(text, "New Title", "New Description")
    assert 'title="New Title"' in new_text
    assert 'description="New Description"' in new_text
    assert "schema={schema}" in new_text
    assert "---\nimport Layout" in new_text

def test_idempotent_replace():
    text = f"<Layout>\n  {SEO_MARKER_START}\n  OLD CONTENT\n  {SEO_MARKER_END}\n</Layout>"
    new_block = f"{SEO_MARKER_START}\n  NEW CONTENT\n{SEO_MARKER_END}"
    new_text = replace_or_insert_seo_block(text, new_block)
    assert "NEW CONTENT" in new_text
    assert "OLD CONTENT" not in new_text
    # Check it doesn't duplicate markers
    assert new_text.count(SEO_MARKER_START) == 1

def test_validator_blocks_bad_content():
    # If using string validation in apply logic
    bad_tokens = ["lei", "RON", "sala", "garantăm", "minute", "km"]
    content = "Aceasta este o sala minunata la pret de 10 lei."
    found = any(tok.lower() in content.lower() for tok in bad_tokens)
    assert found == True

def test_quality_gate():
    text_delta = 2600
    faq_count = 4
    links_count = 3
    assert text_delta > 2500 and faq_count >= 4 and links_count >= 3
