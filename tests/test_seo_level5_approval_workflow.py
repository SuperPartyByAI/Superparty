"""
tests/test_seo_level5_approval_workflow.py — PR #56

Valideaza approval workflow-ul:
- list_pending_actions citeste corect propunerile fara decizie
- record_decision scrie in approval log
- dublarea deciziei este blocata (ApprovalError)
- decizie invalida este blocata
- decided_by gol este blocat
- action_id inexistent este blocat
- applied ramine 0 in summary (invariant)
- approval log nu modifica fisierele sursa SEO
"""
import json
import pytest
from pathlib import Path
from datetime import datetime, timezone

import agent.tasks.seo_level5_approval_workflow as wf_module
from agent.tasks.seo_level5_approval_workflow import (
    ApprovalError,
    list_pending_actions,
    record_decision,
    get_approval_summary,
    load_approval_log,
    get_action_by_id,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _make_dry_run_report(actions: list) -> dict:
    return {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": "2026-03-07T14:00:00Z",
            "mode": "dry_run_only",
            "action_type": "meta_description_update",
            "total_candidates": len(actions),
            "applied": 0,
            "extractor_active": False,
        },
        "actions": actions,
    }


def _make_action(action_id: str, url: str = "/blog/test") -> dict:
    return {
        "action_id": action_id,
        "action_type": "meta_description_update",
        "status": "proposed_only",
        "tier": "C",
        "is_money_page": False,
        "url": url,
        "eligibility": {"tier_allowed": True, "money_page_allowed": False},
        "before": {"meta_description": "Descriere veche."},
        "proposal": {"meta_description": "Descriere propusa noua."},
        "reasoning": {"why_selected": ["tier_c_only"], "why_safe": ["dry_run_only"]},
        "feedback_tracking": {"allowed_signals": [], "forbidden_claims": []},
    }


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports" / "superparty"
    reports_dir.mkdir(parents=True)

    dry_run_path = reports_dir / "seo_level5_dry_run_actions.json"
    approval_log_path = reports_dir / "seo_level5_approval_log.json"

    monkeypatch.setattr(wf_module, "DRY_RUN_REPORT_PATH", dry_run_path)
    monkeypatch.setattr(wf_module, "APPROVAL_LOG_PATH", approval_log_path)
    monkeypatch.setattr(wf_module, "REPORTS_DIR", reports_dir)

    return {
        "reports_dir": reports_dir,
        "dry_run_path": dry_run_path,
        "approval_log_path": approval_log_path,
    }


# ─── list_pending_actions ─────────────────────────────────────────────────────

def test_list_pending_returns_all_when_no_log(sandbox):
    actions = [_make_action("id-001"), _make_action("id-002")]
    _write_json(sandbox["dry_run_path"], _make_dry_run_report(actions))

    pending = list_pending_actions()
    assert len(pending) == 2
    assert {a["action_id"] for a in pending} == {"id-001", "id-002"}


def test_list_pending_excludes_decided_actions(sandbox):
    actions = [_make_action("id-001"), _make_action("id-002")]
    _write_json(sandbox["dry_run_path"], _make_dry_run_report(actions))

    # Pre-populate approval log with one decided action
    _write_json(sandbox["approval_log_path"], [{
        "decision_id": "dec-xxx",
        "action_id": "id-001",
        "decision": "approved",
        "decided_by": "ops-test",
        "decided_at": "2026-03-07T14:00:00Z",
        "notes": None,
        "proposal_snapshot": {},
    }])

    pending = list_pending_actions()
    assert len(pending) == 1
    assert pending[0]["action_id"] == "id-002"


def test_list_pending_raises_if_no_dry_run_report(sandbox):
    # dry_run_path not created
    with pytest.raises(ApprovalError, match="not found"):
        list_pending_actions()


# ─── get_action_by_id ─────────────────────────────────────────────────────────

def test_get_action_by_id_returns_action(sandbox):
    actions = [_make_action("id-abc", url="/articol/test")]
    _write_json(sandbox["dry_run_path"], _make_dry_run_report(actions))

    action = get_action_by_id("id-abc")
    assert action is not None
    assert action["url"] == "/articol/test"


def test_get_action_by_id_returns_none_for_missing(sandbox):
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([]))
    assert get_action_by_id("nonexistent-id") is None


# ─── record_decision ─────────────────────────────────────────────────────────

def test_record_approved_decision(sandbox):
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([_make_action("id-001")]))

    record = record_decision("id-001", "approved", decided_by="ops-manual-review", notes="Arata bine.")

    assert record["decision"] == "approved"
    assert record["action_id"] == "id-001"
    assert record["decided_by"] == "ops-manual-review"
    assert record["notes"] == "Arata bine."
    assert "decision_id" in record
    assert "decided_at" in record

    # Verify written to log
    log = load_approval_log()
    assert len(log) == 1
    assert log[0]["decision"] == "approved"


def test_record_rejected_decision(sandbox):
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([_make_action("id-002")]))
    record = record_decision("id-002", "rejected", decided_by="ops-manual-review")
    assert record["decision"] == "rejected"

    log = load_approval_log()
    assert log[0]["decision"] == "rejected"


def test_decision_record_contains_proposal_snapshot(sandbox):
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([_make_action("id-snap")]))
    record = record_decision("id-snap", "approved", decided_by="ops")

    assert "proposal_snapshot" in record
    assert record["proposal_snapshot"]["before"] == {"meta_description": "Descriere veche."}
    assert record["proposal_snapshot"]["proposal"] == {"meta_description": "Descriere propusa noua."}


def test_record_is_append_only(sandbox):
    actions = [_make_action("id-A"), _make_action("id-B")]
    _write_json(sandbox["dry_run_path"], _make_dry_run_report(actions))

    record_decision("id-A", "approved", decided_by="ops")
    record_decision("id-B", "rejected", decided_by="ops")

    log = load_approval_log()
    assert len(log) == 2
    assert log[0]["action_id"] == "id-A"
    assert log[1]["action_id"] == "id-B"


# ─── Guard: duplicate decision ────────────────────────────────────────────────

def test_duplicate_decision_is_blocked(sandbox):
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([_make_action("id-dup")]))
    record_decision("id-dup", "approved", decided_by="ops")

    with pytest.raises(ApprovalError, match="already has a recorded decision"):
        record_decision("id-dup", "rejected", decided_by="ops")

    # Log still has only 1 entry
    log = load_approval_log()
    assert len(log) == 1
    assert log[0]["decision"] == "approved"


# ─── Guard: invalid inputs ────────────────────────────────────────────────────

def test_invalid_decision_value_is_blocked(sandbox):
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([_make_action("id-x")]))
    with pytest.raises(ApprovalError, match="Invalid decision"):
        record_decision("id-x", "maybe", decided_by="ops")  # type: ignore


def test_empty_decided_by_is_blocked(sandbox):
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([_make_action("id-y")]))
    with pytest.raises(ApprovalError, match="decided_by"):
        record_decision("id-y", "approved", decided_by="")


def test_nonexistent_action_id_is_blocked(sandbox):
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([_make_action("id-z")]))
    with pytest.raises(ApprovalError, match="not found"):
        record_decision("nonexistent-id", "approved", decided_by="ops")


# ─── get_approval_summary — applied=0 invariant ───────────────────────────────

def test_summary_applied_is_always_zero(sandbox):
    actions = [_make_action("id-1"), _make_action("id-2")]
    _write_json(sandbox["dry_run_path"], _make_dry_run_report(actions))

    record_decision("id-1", "approved", decided_by="ops")
    record_decision("id-2", "rejected", decided_by="ops")

    summary = get_approval_summary()
    assert summary["applied"] == 0, "applied trebuie sa ramana 0 — approval workflow nu executa nimic"


def test_summary_counts_correctly(sandbox):
    actions = [_make_action("id-A"), _make_action("id-B"), _make_action("id-C")]
    _write_json(sandbox["dry_run_path"], _make_dry_run_report(actions))

    record_decision("id-A", "approved", decided_by="ops")
    record_decision("id-B", "rejected", decided_by="ops")
    # id-C is pending

    summary = get_approval_summary()
    assert summary["total_proposed"] == 3
    assert summary["total_decided"] == 2
    assert summary["approved"] == 1
    assert summary["rejected"] == 1
    assert summary["pending"] == 1
    assert summary["applied"] == 0


# ─── Source files not modified ────────────────────────────────────────────────

def test_source_seo_files_not_modified_after_approval(sandbox, tmp_path):
    """Approval workflow writes only to approval_log.json, never to SEO source files."""
    actions = [_make_action("id-safe")]
    _write_json(sandbox["dry_run_path"], _make_dry_run_report(actions))

    dry_run_before = sandbox["dry_run_path"].read_text(encoding="utf-8")

    record_decision("id-safe", "approved", decided_by="ops")

    dry_run_after = sandbox["dry_run_path"].read_text(encoding="utf-8")

    assert dry_run_before == dry_run_after, (
        "record_decision nu trebuie sa modifice seo_level5_dry_run_actions.json"
    )
    assert sandbox["approval_log_path"].exists(), (
        "seo_level5_approval_log.json trebuie creat"
    )
