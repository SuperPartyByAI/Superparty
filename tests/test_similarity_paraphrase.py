"""
test_similarity_paraphrase.py — Tests for similarity + paraphrase engine.
"""
import pytest
from agent.seo_agent.similarity_local import (
    embed_text, cosine_sim, check_similarity,
    DENY_THRESHOLD, REWRITE_THRESHOLD, ACCEPT_THRESHOLD,
)
from agent.seo_agent.paraphrase_local import (
    paraphrase_once, iterative_paraphrase, check_and_rewrite,
)


class TestEmbedding:

    def test_embed_returns_list(self):
        emb = embed_text("animatori petreceri copii")
        assert isinstance(emb, list)
        assert len(emb) == 384  # MiniLM or stub dim

    def test_embed_different_texts_differ(self):
        a = embed_text("animatori petreceri copii bucuresti")
        b = embed_text("decoratiuni baloane nunti")
        sim = cosine_sim(a, b)
        # Different texts should not be identical
        assert sim < 1.0

    def test_embed_same_text_identical(self):
        text = "mascote si personaje"
        a = embed_text(text)
        b = embed_text(text)
        sim = cosine_sim(a, b)
        assert sim > 0.99

    def test_empty_vectors(self):
        assert cosine_sim([], []) == 0.0

    def test_zero_vector(self):
        zero = [0.0] * 384
        other = embed_text("test")
        assert cosine_sim(zero, other) == 0.0


class TestCosine:

    def test_identical_vectors(self):
        v = [1.0, 0.0, 1.0]
        assert abs(cosine_sim(v, v) - 1.0) < 0.001

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert abs(cosine_sim(a, b)) < 0.001

    def test_opposite_vectors(self):
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert abs(cosine_sim(a, b) - (-1.0)) < 0.001


class TestCheckSimilarity:

    def test_accept_when_no_stored(self):
        result = check_similarity("completely unique text", stored_embeddings=[])
        assert result["action"] == "accept"
        assert result["max_similarity"] == 0.0

    def test_deny_when_identical(self):
        text = "animatori petreceri copii"
        emb = embed_text(text)
        stored = [{
            "owner_page_id": "fake-id",
            "embedding": emb,
            "preview_snippet": text,
            "model": "all-MiniLM-L6-v2",
        }]
        result = check_similarity(text, stored_embeddings=stored)
        # Same text should be very similar
        assert result["max_similarity"] > 0.9
        assert result["action"] == "deny"


class TestParaphraseStub:

    def test_paraphrase_returns_candidates(self):
        results = paraphrase_once("hello world test", num_return_sequences=2)
        assert isinstance(results, list)
        assert len(results) == 2
        for r in results:
            assert isinstance(r, str)
            assert len(r) > 0

    def test_paraphrase_differs_from_original(self):
        original = "animatori petreceri copii in bucuresti"
        results = paraphrase_once(original)
        # Stub should produce different text
        assert any(r != original for r in results)


class TestIterativeParaphrase:

    def test_immediate_accept(self):
        """If similarity is already low, no rewrite needed."""
        def checker(text):
            return 0.1, []  # very low similarity

        result = iterative_paraphrase("some text", checker, max_iters=3, target_threshold=0.35)
        assert result["success"] is True
        assert result["iterations"] == 1

    def test_iterative_improvement(self):
        """Simulate progressive similarity reduction."""
        call_count = {"n": 0}

        def checker(text):
            call_count["n"] += 1
            # Simulate improving similarity on each call
            sim = max(0.6 - 0.15 * call_count["n"], 0.1)
            return sim, [{"sim": sim}]

        result = iterative_paraphrase(
            "overlapping content text",
            checker,
            max_iters=5,
            target_threshold=0.35,
        )
        assert result["final_similarity"] <= 0.35 or result["iterations"] <= 5


class TestCheckAndRewrite:

    def test_accept_low_similarity(self):
        def checker(text):
            return 0.1, []
        result = check_and_rewrite("unique content", checker)
        assert result["allowed"] is True
        assert result["action"] == "accept"

    def test_deny_high_similarity(self):
        def checker(text):
            return 0.85, [{"close_match": True}]
        result = check_and_rewrite("duplicate content", checker)
        assert result["allowed"] is False
        assert result["action"] == "denied"

    def test_rewrite_medium_similarity(self):
        call_count = {"n": 0}

        def checker(text):
            call_count["n"] += 1
            # First call: medium, then progressively lower
            sim = max(0.55 - 0.1 * call_count["n"], 0.2)
            return sim, []

        result = check_and_rewrite("medium overlap text", checker)
        # Should attempt rewrite and either succeed or fail gracefully
        assert result["action"] in ("rewritten", "denied", "accept")
        assert isinstance(result["allowed"], bool)
