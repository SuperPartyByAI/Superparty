"""
compute_embeddings.py — Populate embeddings for existing owner pages.

Usage:
  python scripts/compute_embeddings.py
"""
from __future__ import annotations

import logging
import os
import sys

log = logging.getLogger("compute_embeddings")


def compute_all():
    """Fetch owner pages from Supabase, compute & store embeddings."""
    from agent.seo_agent.similarity_local import embed_text, store_embedding

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        log.error("SUPABASE_URL/KEY not set")
        return

    import json
    import urllib.request

    # Fetch owner pages
    api_url = f"{url}/rest/v1/owner_pages?select=id,title,h1,path"
    req = urllib.request.Request(
        api_url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            pages = json.loads(resp.read().decode())
    except Exception as e:
        log.error(f"Failed to fetch owner pages: {e}")
        log.info("No owner pages yet — embeddings will be computed when pages are created.")
        return

    if not pages:
        log.info("No owner pages found — nothing to embed.")
        return

    log.info(f"Found {len(pages)} owner pages, computing embeddings...")

    for page in pages:
        text = f"{page.get('title', '')} {page.get('h1', '')} {page.get('path', '')}"
        text = text.strip()
        if not text:
            continue

        emb = embed_text(text)
        store_embedding(
            owner_page_id=page["id"],
            emb=emb,
            preview_snippet=text[:200],
            use_supabase=True,
        )
        log.info(f"  ✅ {page['id'][:8]}... — {text[:60]}")

    log.info("Done computing embeddings.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    compute_all()
