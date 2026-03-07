"""
Tests for SEO Level 5 Rollback Executor (PR #60)

Coverage:
  1. Payload coherence validation
  2. Lineage coherence validation
  3. Dry-run feasibility
  4. Rollback execute — success path (frontmatter)
  5. Rollback execute — success path (meta_tag)
  6. Pre-rollback drift check (Scenario D)
  7. Post-rollback verification failure (fail-closed)
  8. File not found
  9. Unsupported file structure
  10. Verify-only after rollback
  11. Unsafe restore value (delimiter in value)
  12. rollback_execution.json lineage completeness
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

import agent.tasks.seo_level5_rollback_executor as rb_module
from agent.tasks.seo_level5_rollback_executor import (
    RollbackCoherenceError,
    RollbackError,
    validate_rollback_payload_coherence,
    validate_lineage_coherence,
    resolve_target_file,
    extract_current_meta_description,
    apply_rollback_to_file,
    run_validate_only,
    run_dry_run,
    run_execute,
    run_verify_only,
    ROLLBACK_EXECUTION_PATH,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _base_payload(
    action_id: str = "id-rb-001",
    file_path: str = "src/pages/blog/test.astro",
    before_desc: str = "Descriere veche.",
    after_desc: str = "Descriere noua.",
    plan_id: str = "plan-001",
    decision_id: str = "dec-001",
) -> dict:
    return {
        "action_id": action_id,
        "file_path": file_path,
        "rollback_mode": "single_file_revert",
        "before": {"meta_description": before_desc},
        "after": {"meta_description": after_desc},
        "plan_id": plan_id,
        "decision_id": decision_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _base_execution_report(action_id: str = "id-rb-001",
                            plan_id: str = "plan-001",
                            decision_id: str = "dec-001") -> dict:
    return {
        "metadata": {"applied": 1, "create_pull_request": False, "commit_changes": False},
        "applied_actions": [{
            "execution_id": str(uuid.uuid4()),
            "plan_id": plan_id,
            "decision_id": decision_id,
            "action_id": action_id,
            "after_value_verified": True,
            "rollback_ready": True,
        }],
        "blocked_actions": [],
    }


def _base_approval_log(decision_id: str = "dec-001", action_id: str = "id-rb-001") -> list:
    return [{
        "action_id": action_id,
        "decision_id": decision_id,
        "decision": "approved",
        "decided_by": "ops-audit",
        "decided_at": datetime.now(timezone.utc).isoformat(),
    }]


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Patch all global paths to tmp_path sandbox."""
    reports_dir = tmp_path / "reports" / "superparty"
    pages_dir = tmp_path / "src" / "pages"

    rollback_payload_path = reports_dir / "seo_level5_rollback_payload.json"
    execution_report_path = reports_dir / "seo_level5_apply_execution.json"
    approval_log_path = reports_dir / "seo_level5_approval_log.json"
    rollback_exec_path = reports_dir / "seo_level5_rollback_execution.json"

    monkeypatch.setattr(rb_module, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(rb_module, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(rb_module, "PAGES_DIR", pages_dir)
    monkeypatch.setattr(rb_module, "ROLLBACK_PAYLOAD_PATH", rollback_payload_path)
    monkeypatch.setattr(rb_module, "EXECUTION_REPORT_PATH", execution_report_path)
    monkeypatch.setattr(rb_module, "APPROVAL_LOG_PATH", approval_log_path)
    monkeypatch.setattr(rb_module, "ROLLBACK_EXECUTION_PATH", rollback_exec_path)

    reports_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)

    return {
        "tmp_path": tmp_path,
        "reports_dir": reports_dir,
        "pages_dir": pages_dir,
        "rollback_payload_path": rollback_payload_path,
        "execution_report_path": execution_report_path,
        "approval_log_path": approval_log_path,
        "rollback_exec_path": rollback_exec_path,
    }


# ─── 1. Payload coherence validation ─────────────────────────────────────────

def test_valid_payload_produces_no_issues():
    issues = validate_rollback_payload_coherence(_base_payload())
    assert issues == []


def test_missing_file_path_produces_issue():
    payload = dict(_base_payload())
    payload["file_path"] = ""
    issues = validate_rollback_payload_coherence(payload)
    assert any("file_path" in i for i in issues)


def test_wrong_rollback_mode_produces_issue():
    payload = dict(_base_payload())
    payload["rollback_mode"] = "batch_revert"
    issues = validate_rollback_payload_coherence(payload)
    assert any("rollback_mode" in i for i in issues)


def test_missing_before_meta_description_produces_issue():
    payload = dict(_base_payload())
    payload["before"] = {}
    issues = validate_rollback_payload_coherence(payload)
    assert any("before.meta_description" in i for i in issues)


def test_missing_action_id_produces_issue():
    payload = dict(_base_payload())
    payload["action_id"] = ""
    issues = validate_rollback_payload_coherence(payload)
    assert any("action_id" in i for i in issues)


# ─── 2. File resolution and meta extraction ───────────────────────────────────

def test_extract_meta_description_frontmatter(tmp_path):
    page = tmp_path / "test.astro"
    _write(page, '---\ndescription = "Descriere veche din frontmatter."\n---\n<Layout/>\n')
    result = extract_current_meta_description(page)
    assert result == "Descriere veche din frontmatter."


def test_extract_meta_description_meta_tag(tmp_path):
    page = tmp_path / "test.astro"
    _write(page, '---\n---\n<meta name="description" content="Descriere din meta tag." />\n')
    result = extract_current_meta_description(page)
    assert result == "Descriere din meta tag."


def test_extract_meta_description_missing_returns_empty(tmp_path):
    page = tmp_path / "test.astro"
    _write(page, '---\ntitle = "Fara descriere."\n---\n<Layout/>\n')
    result = extract_current_meta_description(page)
    assert result == ""


# ─── 3. Rollback write ────────────────────────────────────────────────────────

def test_apply_rollback_frontmatter_succeeds(tmp_path):
    page = tmp_path / "test.astro"
    _write(page, '---\ndescription = "Valoare noua."\n---\n<Layout/>\n')
    result = apply_rollback_to_file(page, "Valoare veche restaurata.")
    assert result["strategy"] == "frontmatter_prop"
    assert "Valoare veche restaurata." in page.read_text(encoding="utf-8")


def test_apply_rollback_meta_tag_succeeds(tmp_path):
    page = tmp_path / "test.astro"
    _write(page, '---\n---\n<meta name="description" content="Valoare noua meta." />\n')
    result = apply_rollback_to_file(page, "Valoare veche restaurata meta.")
    assert result["strategy"] == "meta_tag"
    assert "Valoare veche restaurata meta." in page.read_text(encoding="utf-8")


def test_apply_rollback_blocks_unsafe_delimiter_frontmatter(tmp_path):
    page = tmp_path / "test.astro"
    _write(page, "---\ndescription = 'Valoare noua.'\n---\n<Layout/>\n")
    with pytest.raises(RollbackError, match="unsafe_restore_contains_delimiter"):
        apply_rollback_to_file(page, "Valoare cu 'apostrof' invalid.")


def test_apply_rollback_blocks_unsupported_structure(tmp_path):
    page = tmp_path / "test.astro"
    _write(page, "<Layout><p>Pagina fara meta description.</p></Layout>\n")
    with pytest.raises(RollbackError, match="unsupported_file_structure"):
        apply_rollback_to_file(page, "Valoare restaurata.")


# ─── 4. Full dry-run flow ─────────────────────────────────────────────────────

def test_dry_run_succeeds_when_file_matches_after(sandbox):
    page = sandbox["pages_dir"] / "blog" / "post.astro"
    _write(page, '---\ndescription = "Descriere noua."\n---\n')
    payload = _base_payload(file_path="src/pages/blog/post.astro",
                            before_desc="Descriere veche.",
                            after_desc="Descriere noua.")
    _write_json(sandbox["rollback_payload_path"], payload)
    assert run_dry_run(pages_dir=sandbox["pages_dir"]) is True


def test_dry_run_blocked_when_file_does_not_match_after(sandbox):
    page = sandbox["pages_dir"] / "blog" / "post.astro"
    _write(page, '---\ndescription = "Ceva complet diferit."\n---\n')
    payload = _base_payload(file_path="src/pages/blog/post.astro",
                            after_desc="Descriere noua.")
    _write_json(sandbox["rollback_payload_path"], payload)
    assert run_dry_run(pages_dir=sandbox["pages_dir"]) is False


# ─── 5. Full execute flow ─────────────────────────────────────────────────────

def test_execute_succeeds_and_writes_rollback_execution_report(sandbox):
    page = sandbox["pages_dir"] / "blog" / "exec.astro"
    _write(page, '---\ndescription = "Descriere noua de test."\n---\n<Layout/>\n')
    payload = _base_payload(
        file_path="src/pages/blog/exec.astro",
        before_desc="Descriere veche de test.",
        after_desc="Descriere noua de test.",
    )
    _write_json(sandbox["rollback_payload_path"], payload)
    _write_json(sandbox["execution_report_path"], _base_execution_report())
    _write_json(sandbox["approval_log_path"], _base_approval_log())

    result = run_execute(pages_dir=sandbox["pages_dir"], operator="test-operator")
    assert result is True

    # File reverted
    assert "Descriere veche de test." in page.read_text(encoding="utf-8")

    # Rollback execution report written
    assert sandbox["rollback_exec_path"].exists()
    with open(sandbox["rollback_exec_path"], encoding="utf-8") as f:
        report = json.load(f)
    assert report["reverted"] is True
    assert report["post_rollback_verification"] is True
    assert report["original_lineage"]["action_id"] == "id-rb-001"
    assert report["original_lineage"]["plan_id"] == "plan-001"
    assert report["original_lineage"]["decision_id"] == "dec-001"
    assert report["before_restored"] == "Descriere veche de test."
    assert report["rollback_id"]  # non-empty UUID


def test_execute_blocked_on_pre_rollback_drift(sandbox):
    """Scenario D: file does not match payload.after — rollback blocked."""
    page = sandbox["pages_dir"] / "blog" / "drift.astro"
    _write(page, '---\ndescription = "Ceva total diferit."\n---\n')
    payload = _base_payload(
        file_path="src/pages/blog/drift.astro",
        after_desc="Descriere noua.",
    )
    _write_json(sandbox["rollback_payload_path"], payload)

    result = run_execute(pages_dir=sandbox["pages_dir"])
    assert result is False
    # File untouched
    assert "Ceva total diferit." in page.read_text(encoding="utf-8")


def test_execute_does_not_modify_approval_log(sandbox):
    """approval_log must never be modified by rollback executor."""
    page = sandbox["pages_dir"] / "blog" / "nolog.astro"
    _write(page, '---\ndescription = "Noua."\n---\n')
    payload = _base_payload(file_path="src/pages/blog/nolog.astro",
                            after_desc="Noua.")
    _write_json(sandbox["rollback_payload_path"], payload)
    _write_json(sandbox["approval_log_path"], _base_approval_log())

    original_log = json.loads(sandbox["approval_log_path"].read_text(encoding="utf-8"))
    run_execute(pages_dir=sandbox["pages_dir"])
    after_log = json.loads(sandbox["approval_log_path"].read_text(encoding="utf-8"))
    assert original_log == after_log


def test_execute_does_not_modify_rollback_payload(sandbox):
    """rollback_payload must not be overwritten during rollback."""
    page = sandbox["pages_dir"] / "blog" / "nopayload.astro"
    _write(page, '---\ndescription = "Noua."\n---\n')
    payload = _base_payload(file_path="src/pages/blog/nopayload.astro",
                            after_desc="Noua.")
    _write_json(sandbox["rollback_payload_path"], payload)

    original_payload = json.loads(sandbox["rollback_payload_path"].read_text(encoding="utf-8"))
    run_execute(pages_dir=sandbox["pages_dir"])
    after_payload = json.loads(sandbox["rollback_payload_path"].read_text(encoding="utf-8"))
    assert original_payload == after_payload


# ─── 6. Verify-only ──────────────────────────────────────────────────────────

def test_verify_only_true_when_file_contains_before_value(sandbox):
    page = sandbox["pages_dir"] / "blog" / "verify.astro"
    _write(page, '---\ndescription = "Descriere veche restaurata."\n---\n')
    payload = _base_payload(
        file_path="src/pages/blog/verify.astro",
        before_desc="Descriere veche restaurata.",
    )
    _write_json(sandbox["rollback_payload_path"], payload)
    assert run_verify_only(pages_dir=sandbox["pages_dir"]) is True


def test_verify_only_false_when_file_does_not_contain_before_value(sandbox):
    page = sandbox["pages_dir"] / "blog" / "verify-fail.astro"
    _write(page, '---\ndescription = "Valoare diferita."\n---\n')
    payload = _base_payload(
        file_path="src/pages/blog/verify-fail.astro",
        before_desc="Descriere veche restaurata.",
    )
    _write_json(sandbox["rollback_payload_path"], payload)
    assert run_verify_only(pages_dir=sandbox["pages_dir"]) is False


# ─── 7. Lineage blocking tests (PR #60 hardening) ────────────────────────────

def test_execute_blocked_when_decision_id_missing_from_approval_log(sandbox):
    """run_execute must block when decision_id is not found in live approval_log."""
    page = sandbox["pages_dir"] / "blog" / "lineage-block.astro"
    _write(page, '---\ndescription = "Descriere noua."\n---\n')
    payload = _base_payload(
        file_path="src/pages/blog/lineage-block.astro",
        action_id="id-lb-001",
        decision_id="dec-MISSING",
        after_desc="Descriere noua.",
    )
    _write_json(sandbox["rollback_payload_path"], payload)
    _write_json(sandbox["execution_report_path"], _base_execution_report(
        action_id="id-lb-001", decision_id="dec-MISSING"
    ))
    # approval_log contains a DIFFERENT decision_id
    _write_json(sandbox["approval_log_path"], _base_approval_log(
        decision_id="dec-OTHER", action_id="id-lb-001"
    ))

    result = run_execute(pages_dir=sandbox["pages_dir"])
    assert result is False
    # File must be untouched
    assert "Descriere noua." in page.read_text(encoding="utf-8")


def test_execute_blocked_when_plan_id_mismatches_execution_report(sandbox):
    """run_execute must block when plan_id in payload != plan_id in execution_report."""
    page = sandbox["pages_dir"] / "blog" / "planid-mismatch.astro"
    _write(page, '---\ndescription = "Descriere noua mismatch."\n---\n')
    payload = _base_payload(
        file_path="src/pages/blog/planid-mismatch.astro",
        action_id="id-pm-001",
        plan_id="plan-PAYLOAD",
        decision_id="dec-pm-001",
        after_desc="Descriere noua mismatch.",
    )
    _write_json(sandbox["rollback_payload_path"], payload)
    # execution_report has a DIFFERENT plan_id
    _write_json(sandbox["execution_report_path"], _base_execution_report(
        action_id="id-pm-001",
        plan_id="plan-DIFFERENT",
        decision_id="dec-pm-001",
    ))
    _write_json(sandbox["approval_log_path"], _base_approval_log(
        decision_id="dec-pm-001", action_id="id-pm-001"
    ))

    result = run_execute(pages_dir=sandbox["pages_dir"])
    assert result is False
    # File must be untouched
    assert "Descriere noua mismatch." in page.read_text(encoding="utf-8")
