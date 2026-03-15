"""
similarity_local.py — Local embedding-based similarity check.

Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings,
cosine similarity for comparison, and stores in Supabase page_embeddings_json.

No external API calls — runs entirely on CPU/GPU.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

log = logging.getLogger("seo_agent.similarity_local")

MODEL_NAME = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
_model = None


def _load_model():
    """Lazy-load sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(MODEL_NAME)
            log.info(f"Loaded sentence-transformers model: {MODEL_NAME}")
        except ImportError:
            log.warning("sentence-transformers not installed — using stub embeddings")
            _model = "stub"
    return _model


def embed_text(text: str) -> list[float]:
    """Generate embedding vector for text. Returns list of floats."""
    model = _load_model()
    if model == "stub":
        return _stub_embed(text)
    emb = model.encode([text], show_progress_bar=False)[0]
    return emb.tolist()


def _stub_embed(text: str) -> list[float]:
    """Simple hash-based stub for testing without sentence-transformers."""
    import hashlib
    h = hashlib.sha256(text.encode()).digest()
    # Create a 384-dim pseudo-embedding from hash
    vec = []
    for i in range(384):
        byte_val = h[i % len(h)]
        vec.append((byte_val / 255.0) * 2 - 1)  # normalize to [-1, 1]
    return vec


def cosine_sim(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import math
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def store_embedding(
    owner_page_id: str,
    emb: list[float],
    model_name: str = MODEL_NAME,
    preview_snippet: str = "",
    use_supabase: bool = True,
) -> dict:
    """Store embedding in Supabase page_embeddings_json table."""
    row = {
        "owner_page_id": owner_page_id,
        "model": model_name,
        "dim": len(emb),
        "embedding": emb,
        "preview_snippet": preview_snippet[:500],
    }
    if not use_supabase:
        return row

    try:
        from .supabase_client import client
        sb = client()
        res = sb.table("page_embeddings_json").insert(row).execute()
        return res.data[0] if res.data else row
    except Exception as e:
        log.error(f"Failed to store embedding: {e}")
        return row


def fetch_all_embeddings(model_name: str = MODEL_NAME) -> list[dict]:
    """Fetch all stored embeddings from Supabase."""
    try:
        from .supabase_client import client
        sb = client()
        res = sb.table("page_embeddings_json").select("*").eq("model", model_name).execute()
        return res.data or []
    except Exception as e:
        log.error(f"Failed to fetch embeddings: {e}")
        return []


def top_k_similar(
    candidate_emb: list[float],
    top_k: int = 5,
    model_name: str = MODEL_NAME,
    stored_embeddings: Optional[list[dict]] = None,
) -> list[dict]:
    """
    Find top-k most similar stored embeddings to candidate.
    
    Args:
        candidate_emb: embedding to compare
        top_k: number of results
        stored_embeddings: pre-fetched embeddings (avoids extra DB call)
    """
    existing = stored_embeddings or fetch_all_embeddings(model_name)

    scores = []
    for row in existing:
        emb = row.get("embedding")
        if not emb:
            continue
        sim = cosine_sim(candidate_emb, emb)
        scores.append({
            "owner_page_id": row.get("owner_page_id", ""),
            "similarity": round(sim, 4),
            "preview_snippet": row.get("preview_snippet", ""),
        })

    scores.sort(key=lambda x: x["similarity"], reverse=True)
    return scores[:top_k]


# ── Thresholds ────────────────────────────────────────────────────────────────

DENY_THRESHOLD = float(os.getenv("SIM_DENY_THRESHOLD", "0.70"))
REWRITE_THRESHOLD = float(os.getenv("SIM_REWRITE_THRESHOLD", "0.50"))
ACCEPT_THRESHOLD = float(os.getenv("SIM_ACCEPT_THRESHOLD", "0.35"))


def check_similarity(
    candidate_text: str,
    stored_embeddings: Optional[list[dict]] = None,
) -> dict:
    """
    Check candidate text against stored embeddings.
    
    Returns:
        {
            "action": "accept" | "rewrite" | "deny",
            "max_similarity": float,
            "top_matches": list,
            "threshold_used": str,
        }
    """
    emb = embed_text(candidate_text)
    top = top_k_similar(emb, top_k=5, stored_embeddings=stored_embeddings)
    max_sim = top[0]["similarity"] if top else 0.0

    if max_sim >= DENY_THRESHOLD:
        return {
            "action": "deny",
            "max_similarity": max_sim,
            "top_matches": top,
            "threshold_used": f"deny>={DENY_THRESHOLD}",
            "reason": f"Content too similar to existing page (sim={max_sim:.2f})",
        }

    if max_sim >= REWRITE_THRESHOLD:
        return {
            "action": "rewrite",
            "max_similarity": max_sim,
            "top_matches": top,
            "threshold_used": f"rewrite>={REWRITE_THRESHOLD}",
            "reason": f"Content needs differentiation (sim={max_sim:.2f})",
        }

    return {
        "action": "accept",
        "max_similarity": max_sim,
        "top_matches": top,
        "threshold_used": f"accept<{REWRITE_THRESHOLD}",
    }
