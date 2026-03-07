"""
tests/test_seo_level5_apply_plan_generator.py — PR #57

Valideaza apply plan generator-ul:
- consuma exclusiv approved entries (nu rejected)
- preflight checks blocheaza Tier A, money pages, actiuni interzise
- applied = 0 invariant
- plan[] contine actiuni gata-de-aplicat care au trecut toate check-urile
- blocked[] contine actiuni respinse cu blocking_reason
- policy invalida produce preflight_summary cu policy_valid=False
- sursele SEO nu sunt modificate
"""
import json
import uuid
import pytest
from pathlib import Path
from datetime import datetime, timezone

import agent.tasks.seo_level5_apply_plan_generator as gen_module
from agent.tasks.seo_level5_apply_plan_generator import (
    PlanGenerationError,
    generate_apply_plan,
    run_apply_plan_generator,
    validate_policy_for_apply_plan,
    get_approved_entries,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _base_policy() -> dict:
    return {
        "schema_version": "1.1",
        "mode": "controlled_dry_run_only",
        "allowed_actions": ["meta_description_update"],
        "forbidden_actions": ["change_canonical", "change_robots", "change_noindex",
                              "change_registry", "change_cluster_schema",
                              "change_internal_ownership", "modify_pillar_page",
                              "modify_sitemap_policy"],
        "dry_run_required": True,
        "approval_gate": "manual",
        "rollback_required": True,
        "feedback_loop_mode": "observability_only",
        "tier_restrictions": {"A": "read_only", "B": "restricted", "C": "low_risk_eligible"},
        "max_actions_per_run": 1,
        "action_activation": {
            "meta_description_update": {
                "execution_mode": "dry_run_only",
                "tier_allowlist": ["C"],
                "tier_denylist": ["A", "B"],
                "money_pages": "forbidden",
                "pillar_pages": "forbidden",
                "max_candidates_per_run": 1,
                "report_only": True,
                "write_files": False,
                "create_pull_request": False,
                "commit_changes": False,
            }
        },
    }


def _make_action(action_id: str, url: str = "/blog/test", tier: str = "C",
                 is_money: bool = False, proposal_text: str = "Descriere propusa.") -> dict:
    return {
        "action_id": action_id,
        "action_type": "meta_description_update",
        "status": "proposed_only",
        "tier": tier,
        "is_money_page": is_money,
        "url": url,
        "before": {"meta_description": "Descriere veche."},
        "proposal": {"meta_description": proposal_text},
        "reasoning": {"why_selected": ["tier_c_only"], "why_safe": ["dry_run_only"]},
        "feedback_tracking": {"allowed_signals": [], "forbidden_claims": []},
    }


def _make_dry_run_report(actions: list) -> dict:
    return {
        "metadata": {"schema_version": "1.0", "mode": "dry_run_only",
                     "applied": 0, "total_candidates": len(actions)},
        "actions": actions,
    }


def _make_approval_entry(action_id: str, decision: str = "approved",
                         url: str = "/blog/test") -> dict:
    return {
        "decision_id": str(uuid.uuid4()),
        "action_id": action_id,
        "action_type": "meta_description_update",
        "url": url,
        "decision": decision,
        "decided_by": "ops-manual-review",
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "notes": None,
        "proposal_snapshot": {
            "before": {"meta_description": "Descriere veche."},
            "proposal": {"meta_description": "Descriere propusa."},
        },
    }


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports" / "superparty"
    config_dir = tmp_path / "config" / "seo"

    policy_path = config_dir / "level5_action_policy.json"
    dry_run_path = reports_dir / "seo_level5_dry_run_actions.json"
    approval_log_path = reports_dir / "seo_level5_approval_log.json"
    apply_plan_path = reports_dir / "seo_level5_apply_plan.json"

    monkeypatch.setattr(gen_module, "POLICY_PATH", policy_path)
    monkeypatch.setattr(gen_module, "DRY_RUN_REPORT_PATH", dry_run_path)
    monkeypatch.setattr(gen_module, "APPROVAL_LOG_PATH", approval_log_path)
    monkeypatch.setattr(gen_module, "APPLY_PLAN_PATH", apply_plan_path)
    monkeypatch.setattr(gen_module, "REPORTS_DIR", reports_dir)

    # Write default valid files
    _write_json(policy_path, _base_policy())
    _write_json(dry_run_path, _make_dry_run_report([]))
    _write_json(approval_log_path, [])

    return {
        "policy_path": policy_path,
        "dry_run_path": dry_run_path,
        "approval_log_path": approval_log_path,
        "apply_plan_path": apply_plan_path,
    }


# ─── Policy validation ────────────────────────────────────────────────────────

def test_valid_policy_produces_no_issues():
    issues = validate_policy_for_apply_plan(_base_policy())
    assert issues == []


def test_invalid_policy_tier_a_not_read_only_produces_issue():
    policy = dict(_base_policy())
    policy["tier_restrictions"] = {"A": "enabled", "B": "restricted", "C": "low_risk_eligible"}
    issues = validate_policy_for_apply_plan(policy)
    assert any("Tier A" in i for i in issues)


def test_invalid_policy_empty_allowed_actions_produces_issue():
    policy = dict(_base_policy())
    policy["allowed_actions"] = []
    issues = validate_policy_for_apply_plan(policy)
    assert any("allowed_actions" in i for i in issues)


def test_invalid_policy_write_files_true_produces_issue():
    policy = dict(_base_policy())
    policy["action_activation"]["meta_description_update"]["write_files"] = True
    issues = validate_policy_for_apply_plan(policy)
    assert any("write_files" in i for i in issues)


# ─── Approved entries filter ──────────────────────────────────────────────────

def test_get_approved_entries_filters_rejected():
    log = [
        _make_approval_entry("id-A", "approved"),
        _make_approval_entry("id-B", "rejected"),
        _make_approval_entry("id-C", "approved"),
    ]
    approved = get_approved_entries(log)
    assert len(approved) == 2
    assert all(e["decision"] == "approved" for e in approved)


# ─── Plan generation — happy path ────────────────────────────────────────────

def test_generates_plan_for_approved_tier_c_action(sandbox):
    action = _make_action("id-ok", url="/blog/articol", tier="C")
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([action]))
    _write_json(sandbox["approval_log_path"], [_make_approval_entry("id-ok", url="/blog/articol")])

    plan = generate_apply_plan()

    assert plan["metadata"]["applied"] == 0
    assert plan["metadata"]["total_eligible"] == 1
    assert plan["metadata"]["total_blocked"] == 0
    assert len(plan["plan"]) == 1
    assert plan["plan"][0]["action_id"] == "id-ok"
    assert plan["plan"][0]["ready_to_apply"] is True


def test_plan_entry_contains_proposal_and_before(sandbox):
    action = _make_action("id-snap", url="/blog/snap", tier="C")
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([action]))
    _write_json(sandbox["approval_log_path"], [_make_approval_entry("id-snap", url="/blog/snap")])

    plan = generate_apply_plan()
    entry = plan["plan"][0]
    assert entry["before"] == {"meta_description": "Descriere veche."}
    assert entry["proposal"] == {"meta_description": "Descriere propusa."}


def test_plan_entry_contains_approval_record(sandbox):
    action = _make_action("id-ar", url="/blog/ar", tier="C")
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([action]))
    approval = _make_approval_entry("id-ar", url="/blog/ar")
    _write_json(sandbox["approval_log_path"], [approval])

    plan = generate_apply_plan()
    ar = plan["plan"][0]["approval_record"]
    assert ar["decision"] == "approved"
    assert ar["decided_by"] == "ops-manual-review"


# ─── Preflight blocks ─────────────────────────────────────────────────────────

def test_blocks_tier_a_action(sandbox):
    action = _make_action("id-tier-a", url="/animatori-petreceri-copii", tier="A")
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([action]))
    _write_json(sandbox["approval_log_path"],
                [_make_approval_entry("id-tier-a", url="/animatori-petreceri-copii")])

    plan = generate_apply_plan()
    assert plan["metadata"]["total_eligible"] == 0
    assert plan["metadata"]["total_blocked"] == 1
    assert plan["blocked"][0]["ready_to_apply"] is False
    # Tier A falls first on denylist check (tier_not_in_denylist) or explicit guard —
    # either way the blocking_reason must mention tier
    blocking = plan["blocked"][0]["blocking_reason"]
    assert "tier" in blocking, (
        f"Expected tier-related block for Tier A, got: {blocking}"
    )


def test_blocks_money_page_action(sandbox):
    action = _make_action("id-money", url="/ghid/test", tier="C", is_money=True)
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([action]))
    _write_json(sandbox["approval_log_path"], [_make_approval_entry("id-money")])

    plan = generate_apply_plan()
    assert plan["metadata"]["total_blocked"] == 1
    assert plan["blocked"][0]["blocking_reason"] == "not_money_page"


def test_blocks_action_not_in_dry_run_report(sandbox):
    # Approval exists but action_id not in dry-run report
    _write_json(sandbox["approval_log_path"], [_make_approval_entry("id-orphan")])

    plan = generate_apply_plan()
    assert plan["metadata"]["total_blocked"] == 1
    assert plan["blocked"][0]["blocking_reason"] == "action_id_not_found_in_dry_run_report"


def test_rejected_actions_not_included_in_plan(sandbox):
    action = _make_action("id-rej", url="/blog/rejected", tier="C")
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([action]))
    _write_json(sandbox["approval_log_path"],
                [_make_approval_entry("id-rej", decision="rejected")])

    plan = generate_apply_plan()
    assert plan["metadata"]["total_approved"] == 0
    assert plan["metadata"]["total_eligible"] == 0
    assert len(plan["plan"]) == 0
    assert len(plan["blocked"]) == 0


# ─── applied = 0 invariant ────────────────────────────────────────────────────

def test_applied_is_always_zero_even_with_eligible_actions(sandbox):
    action = _make_action("id-z", url="/blog/zero", tier="C")
    _write_json(sandbox["dry_run_path"], _make_dry_run_report([action]))
    _write_json(sandbox["approval_log_path"], [_make_approval_entry("id-z", url="/blog/zero")])

    plan = generate_apply_plan()
    assert plan["metadata"]["applied"] == 0, (
        "applied trebuie sa ramana 0 — apply plan generator NU executa nimic"
    )


def test_applied_is_always_zero_with_no_actions(sandbox):
    plan = generate_apply_plan()
    assert plan["metadata"]["applied"] == 0


# ─── Source integrity ─────────────────────────────────────────────────────────

def test_source_files_not_modified_after_plan_generation(sandbox):
    action = _make_action("id-safe", url="/blog/safe", tier="C")
    dry_run_content = _make_dry_run_report([action])
    _write_json(sandbox["dry_run_path"], dry_run_content)
    _write_json(sandbox["approval_log_path"], [_make_approval_entry("id-safe", url="/blog/safe")])

    dr_before = sandbox["dry_run_path"].read_text(encoding="utf-8")
    al_before = sandbox["approval_log_path"].read_text(encoding="utf-8")

    run_apply_plan_generator()

    assert sandbox["dry_run_path"].read_text(encoding="utf-8") == dr_before
    assert sandbox["approval_log_path"].read_text(encoding="utf-8") == al_before
    assert sandbox["apply_plan_path"].exists()


# ─── Policy invalid — preflight_summary ───────────────────────────────────────

def test_invalid_policy_reflected_in_preflight_summary(sandbox):
    bad_policy = dict(_base_policy())
    bad_policy["tier_restrictions"]["A"] = "enabled"
    _write_json(sandbox["policy_path"], bad_policy)

    plan = generate_apply_plan()
    assert plan["preflight_summary"]["policy_valid"] is False
    assert len(plan["preflight_summary"]["blocking_issues"]) > 0
