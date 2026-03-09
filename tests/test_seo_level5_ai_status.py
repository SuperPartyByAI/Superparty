"""
Tests for agent/tasks/seo_level5_ai_status.py

All tests are mocked — no real Ollama or filesystem access.
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import agent.tasks.seo_level5_ai_status as ai_status_mod


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _dry_run_artifact(actions=None):
    """Build a minimal dry-run artifact structure for mocking."""
    return {
        "metadata": {"generated_at": "2026-03-09T12:00:00+00:00"},
        "actions": actions or [],
    }


def _action(source):
    return {"url": "/petreceri/test", "proposal": {"meta_description": "x", "proposal_source": source}}


# ─── _check_ollama_reachable ──────────────────────────────────────────────────

class TestCheckOllamaReachable:

    def test_ollama_reachable_with_models(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"models": [{"name": "llama3.2:3b"}, {"name": "other:1b"}]}
        mock_resp.raise_for_status.return_value = None
        with patch("requests.get", return_value=mock_resp):
            reachable, models = ai_status_mod._check_ollama_reachable()
        assert reachable is True
        assert "llama3.2:3b" in models

    def test_ollama_not_reachable_connection_error(self):
        import requests
        with patch("requests.get", side_effect=requests.exceptions.ConnectionError("refused")):
            reachable, models = ai_status_mod._check_ollama_reachable()
        assert reachable is False
        assert models == []

    def test_ollama_not_reachable_timeout(self):
        import requests
        with patch("requests.get", side_effect=requests.exceptions.Timeout("timeout")):
            reachable, models = ai_status_mod._check_ollama_reachable()
        assert reachable is False
        assert models == []

    def test_ollama_reachable_no_models(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"models": []}
        mock_resp.raise_for_status.return_value = None
        with patch("requests.get", return_value=mock_resp):
            reachable, models = ai_status_mod._check_ollama_reachable()
        assert reachable is True
        assert models == []


# ─── _count_proposal_sources ─────────────────────────────────────────────────

class TestCountProposalSources:

    def test_counts_llm_and_fallback(self):
        actions = [
            _action("llm"),
            _action("llm"),
            _action("deterministic_fallback"),
        ]
        counts = ai_status_mod._count_proposal_sources(actions)
        assert counts["llm"] == 2
        assert counts["deterministic_fallback"] == 1

    def test_empty_actions_returns_zeros(self):
        counts = ai_status_mod._count_proposal_sources([])
        assert counts["llm"] == 0
        assert counts["deterministic_fallback"] == 0

    def test_unknown_source_counted(self):
        actions = [{"url": "/x", "proposal": {"proposal_source": "some_new_source"}}]
        counts = ai_status_mod._count_proposal_sources(actions)
        assert counts.get("some_new_source", 0) == 1

    def test_missing_proposal_source_counted_as_unknown(self):
        actions = [{"url": "/x", "proposal": {}}]
        counts = ai_status_mod._count_proposal_sources(actions)
        assert counts.get("unknown", 0) == 1


# ─── collect_ai_status ────────────────────────────────────────────────────────

class TestCollectAiStatus:

    def _patched_collect(self, ollama_reachable, models, dry_run_content=None):
        """Helper: mock both Ollama check and dry-run path."""
        with patch.object(ai_status_mod, "_check_ollama_reachable", return_value=(ollama_reachable, models)):
            with patch.object(ai_status_mod, "_read_dry_run_artifact", return_value=dry_run_content):
                return ai_status_mod.collect_ai_status()

    def test_full_status_ollama_healthy_with_model(self):
        dry_run = _dry_run_artifact([_action("llm")])
        status = self._patched_collect(True, ["llama3.2:3b"], dry_run)
        assert status["ollama_reachable"] is True
        assert status["model_available"] is True
        assert status["candidate_count"] == 1
        assert status["proposal_source_counts"]["llm"] == 1
        assert status["llm_enabled"] is True
        assert "active" in status["notes"]

    def test_status_ollama_reachable_but_model_missing(self):
        dry_run = _dry_run_artifact()
        status = self._patched_collect(True, ["other_model:7b"], dry_run)
        assert status["ollama_reachable"] is True
        assert status["model_available"] is False
        assert "not found" in status["notes"]

    def test_status_ollama_unreachable(self):
        status = self._patched_collect(False, [])
        assert status["ollama_reachable"] is False
        assert status["model_available"] is False
        assert "deterministic fallback" in status["notes"]

    def test_status_no_dry_run_artifact(self):
        status = self._patched_collect(False, [], dry_run_content=None)
        assert status["candidate_count"] == 0
        assert status["last_dry_run_at"] is None
        assert status["proposal_source_counts"]["llm"] == 0

    def test_status_schema_fields_present(self):
        status = self._patched_collect(False, [])
        required = [
            "generated_at", "schema_version", "llm_enabled",
            "ollama_reachable", "model", "model_available",
            "last_dry_run_at", "candidate_count",
            "proposal_source_counts", "notes",
        ]
        for field in required:
            assert field in status, f"Missing field: {field}"

    def test_generated_at_is_iso_format(self):
        status = self._patched_collect(False, [])
        from datetime import datetime
        # Should parse without error
        datetime.fromisoformat(status["generated_at"].replace("Z", "+00:00"))


# ─── write_ai_status ──────────────────────────────────────────────────────────

class TestWriteAiStatus:

    def test_write_creates_file_with_correct_content(self, tmp_path):
        status = {
            "generated_at": "2026-03-09T12:00:00+00:00",
            "llm_enabled": True,
            "ollama_reachable": False,
        }
        with patch.object(ai_status_mod, "_AI_STATUS_PATH", tmp_path / "seo_level5_ai_status.json"):
            path = ai_status_mod.write_ai_status(status)
        assert path.exists()
        written = json.loads(path.read_text(encoding="utf-8"))
        assert written["llm_enabled"] is True
        assert written["ollama_reachable"] is False

    def test_write_creates_parent_directories(self, tmp_path):
        nested = tmp_path / "reports" / "superparty" / "ai_status.json"
        status = {"test": True}
        with patch.object(ai_status_mod, "_AI_STATUS_PATH", nested):
            path = ai_status_mod.write_ai_status(status)
        assert path.exists()
