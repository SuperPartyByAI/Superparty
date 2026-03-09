"""
Tests for agent/tasks/seo_level5_llm_proposal.py

All tests run WITHOUT a real Ollama server (fully mocked).
Tests for build_meta_description_proposal() integration are in
tests/test_seo_level5_meta_description_dry_run.py.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import agent.tasks.seo_level5_llm_proposal as llm_mod
from agent.tasks.seo_level5_meta_description_dry_run import Candidate


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _candidate(url="/petreceri/test", meta="", flags=None):
    return Candidate(
        url=url,
        tier="C",
        is_money_page=False,
        is_pillar_page=False,
        current_meta_description=meta,
        reason_flags=flags or ["description_missing_or_weak", "tier_c_only"],
        score=30.0,
        health_classified=True,
    )


def _mock_ollama_response(text: str):
    """Returns a mock requests.Response with Ollama JSON structure."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": text}
    mock_resp.raise_for_status.return_value = None
    return mock_resp


# ─── validate_proposal tests ──────────────────────────────────────────────────

class TestValidateProposal:

    def test_valid_text_returns_true(self):
        # Exactly 141 chars, no forbidden chars
        text = "A" * 141
        assert llm_mod.validate_proposal(text) is True

    def test_valid_boundary_140(self):
        assert llm_mod.validate_proposal("B" * 140) is True

    def test_valid_boundary_160(self):
        assert llm_mod.validate_proposal("C" * 160) is True

    def test_too_short_returns_false(self):
        assert llm_mod.validate_proposal("A" * 60) is False

    def test_too_long_returns_false(self):
        assert llm_mod.validate_proposal("A" * 165) is False

    def test_empty_returns_false(self):
        assert llm_mod.validate_proposal("") is False

    def test_none_returns_false(self):
        assert llm_mod.validate_proposal(None) is False  # type: ignore

    def test_double_quote_returns_false(self):
        text = '"' + "A" * 139
        assert llm_mod.validate_proposal(text) is False

    def test_single_quote_returns_false(self):
        text = "it" + "'" + "s" + "A" * 137
        assert llm_mod.validate_proposal(text) is False

    def test_html_angle_open_returns_false(self):
        text = "<" + "A" * 140
        assert llm_mod.validate_proposal(text[:160]) is False

    def test_html_angle_close_returns_false(self):
        text = ">" + "A" * 140
        assert llm_mod.validate_proposal(text[:160]) is False

    def test_newline_returns_false(self):
        text = "A" * 70 + "\n" + "A" * 70
        assert llm_mod.validate_proposal(text) is False

    def test_carriage_return_returns_false(self):
        text = "A" * 70 + "\r" + "A" * 70
        assert llm_mod.validate_proposal(text) is False

    def test_identical_to_current_returns_false(self):
        meta = "A" * 145
        assert llm_mod.validate_proposal(meta, current_meta=meta) is False

    def test_different_from_current_returns_true(self):
        current = "A" * 145
        proposed = "B" * 145
        assert llm_mod.validate_proposal(proposed, current_meta=current) is True

    def test_ignores_current_when_empty(self):
        # If current is empty, identical check is skipped
        text = "A" * 145
        assert llm_mod.validate_proposal(text, current_meta="") is True


# ─── _clean_response tests ────────────────────────────────────────────────────

class TestCleanResponse:

    def test_strips_whitespace(self):
        assert llm_mod._clean_response("  hello  ") == "hello"

    def test_strips_meta_prefix(self):
        assert llm_mod._clean_response("Meta description: some text") == "some text"

    def test_strips_backtick_fence(self):
        assert llm_mod._clean_response("`some text`") == "some text"

    def test_takes_first_line_only(self):
        result = llm_mod._clean_response("first line\nsecond line")
        assert result == "first line"

    def test_strips_descriere_prefix(self):
        assert llm_mod._clean_response("Descriere: some text") == "some text"


# ─── build_llm_meta_description tests ────────────────────────────────────────

class TestBuildLlmMetaDescription:

    def test_llm_unavailable_connection_error_returns_none(self):
        import requests
        with patch("requests.post", side_effect=requests.exceptions.ConnectionError("refused")):
            result = llm_mod.build_llm_meta_description(_candidate())
        assert result is None

    def test_llm_timeout_returns_none(self):
        import requests
        with patch("requests.post", side_effect=requests.exceptions.Timeout("timeout")):
            result = llm_mod.build_llm_meta_description(_candidate())
        assert result is None

    def test_llm_http_error_returns_none(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("500 Server Error")
        with patch("requests.post", return_value=mock_resp):
            result = llm_mod.build_llm_meta_description(_candidate())
        assert result is None

    def test_llm_empty_response_returns_none(self):
        mock_resp = _mock_ollama_response("")
        with patch("requests.post", return_value=mock_resp):
            result = llm_mod.build_llm_meta_description(_candidate())
        assert result is None

    def test_llm_too_short_fails_validation_returns_none(self):
        mock_resp = _mock_ollama_response("Prea scurt.")
        with patch("requests.post", return_value=mock_resp):
            result = llm_mod.build_llm_meta_description(_candidate())
        assert result is None

    def test_llm_too_long_fails_validation_returns_none(self):
        mock_resp = _mock_ollama_response("A" * 170)
        with patch("requests.post", return_value=mock_resp):
            result = llm_mod.build_llm_meta_description(_candidate())
        assert result is None

    def test_llm_with_quotes_fails_validation_returns_none(self):
        text = '"' + "A" * 140
        mock_resp = _mock_ollama_response(text)
        with patch("requests.post", return_value=mock_resp):
            result = llm_mod.build_llm_meta_description(_candidate())
        assert result is None

    def test_llm_valid_response_returns_text(self):
        # Build a clean 150-char text with no forbidden chars
        valid_text = "Animatori profesionisti pentru petreceri copii in zona Sector 1 Bucuresti cu costume premium si amintiri speciale."
        # Pad to exactly 150 chars using spaces before checking
        while len(valid_text) < 150:
            valid_text += "a"
        valid_text = valid_text[:150]
        assert 140 <= len(valid_text) <= 160, f"Test setup error: len={len(valid_text)}"
        mock_resp = _mock_ollama_response(valid_text)
        with patch("requests.post", return_value=mock_resp):
            result = llm_mod.build_llm_meta_description(_candidate())
        # LLM path: result must be a non-empty valid string
        assert result is not None
        assert 140 <= len(result) <= 160
        assert '"' not in result
        assert "'" not in result

    def test_llm_identical_to_current_returns_none(self):
        current = "A" * 145
        mock_resp = _mock_ollama_response(current)
        with patch("requests.post", return_value=mock_resp):
            result = llm_mod.build_llm_meta_description(_candidate(meta=current))
        assert result is None

    def test_prompt_contains_url(self):
        """Verify the prompt sent to Ollama contains the candidate URL."""
        mock_resp = _mock_ollama_response("valid " + "a" * 144)
        with patch("requests.post", return_value=mock_resp) as mock_post:
            llm_mod.build_llm_meta_description(_candidate(url="/petreceri/sector-5"))
        call_args = mock_post.call_args
        prompt_sent = call_args[1]["json"]["prompt"]
        assert "/petreceri/sector-5" in prompt_sent

    def test_prompt_contains_current_meta(self):
        """Verify the prompt includes current meta description for context."""
        mock_resp = _mock_ollama_response("valid " + "a" * 144)
        with patch("requests.post", return_value=mock_resp) as mock_post:
            llm_mod.build_llm_meta_description(_candidate(meta="Meta veche existenta."))
        prompt_sent = mock_post.call_args[1]["json"]["prompt"]
        assert "Meta veche existenta." in prompt_sent


# ─── Integration: build_meta_description_proposal with LLM ──────────────────

class TestBuildMetaDescriptionProposalWithLLM:
    """
    Integration tests for build_meta_description_proposal() in dry-run
    that test the LLM path through the new module.
    """

    def test_proposal_uses_llm_when_available(self):
        from agent.tasks.seo_level5_meta_description_dry_run import build_meta_description_proposal
        valid_text = "Animatori copii Sector 1 Bucuresti - programe creative si costume premium pentru petreceri de vis copii."
        valid_text = (valid_text + " x" * 20)[:150]
        assert 140 <= len(valid_text) <= 160

        with patch("agent.tasks.seo_level5_llm_proposal.build_llm_meta_description", return_value=valid_text):
            result = build_meta_description_proposal(_candidate())

        assert result["meta_description"] == valid_text
        assert result["proposal_source"] == "llm"

    def test_proposal_falls_back_when_llm_returns_none(self):
        from agent.tasks.seo_level5_meta_description_dry_run import build_meta_description_proposal

        with patch("agent.tasks.seo_level5_llm_proposal.build_llm_meta_description", return_value=None):
            result = build_meta_description_proposal(_candidate(url="/petreceri/sector-3"))

        assert result["proposal_source"] == "deterministic_fallback"
        assert "superparty" in result["meta_description"].lower()
        assert len(result["meta_description"]) <= 160

    def test_proposal_falls_back_when_llm_import_fails(self):
        """Simulate import error (module not installed) → should not crash."""
        from agent.tasks.seo_level5_meta_description_dry_run import build_meta_description_proposal

        with patch("agent.tasks.seo_level5_llm_proposal.build_llm_meta_description",
                   side_effect=ImportError("requests not installed")):
            result = build_meta_description_proposal(_candidate())

        assert result["proposal_source"] == "deterministic_fallback"
        assert result["meta_description"]
