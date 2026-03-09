"""
tests/test_seo_level5_auto_apply.py — PR #88 Hardening

Suite de teste runtime pentru seo_level5_auto_apply.py.
Verifica toate invariantele de executie:
- flag OFF -> returneaza None, fisier neatins
- flag ON + Tier C valid -> returneaza True, fisier modificat, audit log scris
- Tier A/B/money/pillar bloccat cand flag ON
- Propunere invalida blocata
- File drift bloccat
- Audit trail complet (approved_by, proposal_source, rollback_reference, activation_source)
- Rollback payload scris corect
- Max 1 candidat per run
- create_pull_request=False, commit_changes=False
- Pillar registry guard (blocat indiferent de is_pillar_page din plan)
- Cooldown guard (14 zile per URL)
- Override file prioritar fata de policy
- Status report scris la fiecare run
"""
import json
import uuid
import pytest
from pathlib import Path
from datetime import datetime, timedelta, timezone

import agent.tasks.seo_level5_auto_apply as auto_module
from agent.tasks.seo_level5_auto_apply import (
    check_auto_apply_enabled,
    get_activation_source,
    check_pillar_registry,
    check_url_cooldown,
    validate_auto_apply_eligibility,
    validate_proposal,
    validate_candidate_count,
    validate_file_state,
    run_controlled_auto_apply,
    APPROVED_BY,
    ACTION_TYPE,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _base_policy(flag: bool = False) -> dict:
    return {
        "schema_version": "1.3",
        "mode": "controlled_single_apply",
        "approval_gate": "manual",
        "rollback_required": True,
        "feedback_loop_mode": "observability_only",
        "tier_restrictions": {"A": "read_only", "B": "restricted", "C": "low_risk_eligible"},
        "max_actions_per_run": 1,
        "action_activation": {
            "meta_description_update": {
                "execution_mode": "single_apply_only",
                "tier_allowlist": ["C"],
                "tier_denylist": ["A", "B"],
                "money_pages": "forbidden",
                "pillar_pages": "forbidden",
                "max_candidates_per_run": 1,
                "requires_manual_approval_before_apply": True,
                "requires_ready_to_apply": True,
                "requires_approval_decision": "approved",
                "write_files": True,
                "create_pull_request": False,
                "commit_changes": False,
                "rollback_mode": "single_file_revert",
            }
        },
        "auto_apply_config": {
            "enabled": flag,
            "mode": "controlled_single_auto_apply",
            "auto_apply_actions_allowlist": ["meta_description_update"],
            "auto_apply_tier_allowlist": ["C"],
            "auto_apply_tier_denylist": ["A", "B"],
            "auto_apply_max_candidates": 1,
            "auto_apply_money_pages": "forbidden",
            "auto_apply_pillar_pages": "forbidden",
            "auto_apply_approved_by_label": "system_auto_apply",
            "rollback_required": True,
            "feedback_loop_mode": "observability_only",
            "create_pull_request": False,
            "commit_changes": False,
        },
    }


def _make_action(tier="C", is_money=False, is_pillar=False,
                 action_type=ACTION_TYPE,
                 before_desc="Descriere veche de test pentru pagina.",
                 proposal_desc="Animatori petreceri copii Bucuresti. Costume premium, 30 personaje, transport inclus. Pachete de la 490 lei. Suna: 0722 744 377.",
                 proposal_source="deterministic_fallback",
                 url="/test/page") -> dict:
    return {
        "action_id": str(uuid.uuid4()),
        "plan_id": str(uuid.uuid4()),
        "action_type": action_type,
        "url": url,
        "tier": tier,
        "is_money_page": is_money,
        "is_pillar_page": is_pillar,
        "ready_to_apply": True,
        "proposal_source": proposal_source,
        "before": {"meta_description": before_desc},
        "proposal": {"meta_description": proposal_desc},
    }


def _make_plan(actions: list) -> dict:
    return {"plan": actions, "blocked": []}


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Isolated sandbox: all paths patched to tmp_path."""
    reports_dir = tmp_path / "reports" / "superparty"
    config_dir  = tmp_path / "config" / "seo"
    pages_dir   = tmp_path / "src" / "pages"

    policy_path           = config_dir  / "level5_action_policy.json"
    override_path         = config_dir  / "auto_apply_runtime_override.json"
    pillar_registry_path  = config_dir  / "pillar_pages_registry.json"
    apply_plan_path       = reports_dir / "seo_level5_apply_plan.json"
    auto_apply_log_path   = reports_dir / "seo_level5_auto_apply_log.json"
    execution_report_path = reports_dir / "seo_level5_apply_execution.json"
    rollback_payload_path = reports_dir / "seo_level5_rollback_payload.json"
    status_report_path    = reports_dir / "seo_level5_status.json"

    monkeypatch.setattr(auto_module, "POLICY_PATH",             policy_path)
    monkeypatch.setattr(auto_module, "OVERRIDE_PATH",           override_path)
    monkeypatch.setattr(auto_module, "PILLAR_REGISTRY_PATH",    pillar_registry_path)
    monkeypatch.setattr(auto_module, "APPLY_PLAN_PATH",         apply_plan_path)
    monkeypatch.setattr(auto_module, "AUTO_APPLY_LOG_PATH",     auto_apply_log_path)
    monkeypatch.setattr(auto_module, "EXECUTION_REPORT_PATH",   execution_report_path)
    monkeypatch.setattr(auto_module, "ROLLBACK_PAYLOAD_PATH",   rollback_payload_path)
    monkeypatch.setattr(auto_module, "STATUS_REPORT_PATH",      status_report_path)
    monkeypatch.setattr(auto_module, "PAGES_DIR",               pages_dir)
    monkeypatch.setattr(auto_module, "ROOT_DIR",                tmp_path)

    # Empty pillar registry by default (tests opt-in)
    _write_json(pillar_registry_path, {"schema_version": "1.0", "pillar_pages": []})

    return {
        "policy_path": policy_path,
        "override_path": override_path,
        "pillar_registry_path": pillar_registry_path,
        "apply_plan_path": apply_plan_path,
        "auto_apply_log_path": auto_apply_log_path,
        "execution_report_path": execution_report_path,
        "rollback_payload_path": rollback_payload_path,
        "status_report_path": status_report_path,
        "pages_dir": pages_dir,
        "tmp_path": tmp_path,
    }


def _setup_page(sandbox, url="/test/page",
                before_desc="Descriere veche de test pentru pagina.") -> Path:
    url_stripped = url.lstrip("/")
    page = sandbox["pages_dir"] / url_stripped / "index.astro"
    _write(page, f'---\nimport Layout from "../../layouts/Layout.astro";\n---\n'
                 f'<Layout description="{before_desc}">\n</Layout>\n')
    return page


def _setup_run(sandbox, flag=True, tier="C", is_money=False, is_pillar=False,
               action_type=ACTION_TYPE, proposal_desc=None, before_desc=None,
               multi_candidates=False, url="/test/page"):
    """Setup a complete run scenario. Policy-based activation (no override file)."""
    bd = before_desc or "Descriere veche de test pentru pagina."
    pd = proposal_desc or "Animatori petreceri copii Bucuresti. Costume premium, 30 personaje. Pachete de la 490 lei. Suna: 0722 744 377."

    _write_json(sandbox["policy_path"], _base_policy(flag=flag))

    action = _make_action(tier=tier, is_money=is_money, is_pillar=is_pillar,
                          action_type=action_type, before_desc=bd, proposal_desc=pd, url=url)

    if multi_candidates:
        action2 = _make_action(tier=tier, before_desc=bd, proposal_desc=pd, url="/test/page2")
        _write_json(sandbox["apply_plan_path"], _make_plan([action, action2]))
    else:
        _write_json(sandbox["apply_plan_path"], _make_plan([action]))

    page = _setup_page(sandbox, url=url, before_desc=bd)
    return action, page


# ─── 1. Feature flag OFF ──────────────────────────────────────────────────────

def test_run_returns_none_when_flag_off(sandbox):
    """When flag is OFF (policy), run returns None and file is untouched."""
    action, page = _setup_run(sandbox, flag=False)
    original = page.read_text(encoding="utf-8")

    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )

    assert result is None, "Flag OFF must return None"
    assert page.read_text(encoding="utf-8") == original, "File must not be modified"
    assert not sandbox["auto_apply_log_path"].exists(), "Audit log must not be written"


# ─── 2. Flag ON via policy — happy path ──────────────────────────────────────

def test_run_applies_single_tier_c_when_flag_on(sandbox):
    """Flag ON (policy) + 1 Tier C candidate = apply succeeds, file modified."""
    action, page = _setup_run(sandbox, flag=True)

    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )

    assert result is True, "Valid Tier C auto-apply must return True"
    content = page.read_text(encoding="utf-8")
    proposal = action["proposal"]["meta_description"]
    assert proposal in content, "New description must be written to file"


def test_audit_trail_written_on_success(sandbox):
    """Auto-apply success must write audit trail with required fields."""
    action, page = _setup_run(sandbox, flag=True)

    run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )

    assert sandbox["auto_apply_log_path"].exists()
    log_entries = json.loads(sandbox["auto_apply_log_path"].read_text(encoding="utf-8"))
    assert len(log_entries) == 1
    entry = log_entries[0]
    assert entry["approved_by"] == APPROVED_BY
    assert entry["approval_mode"] == "auto_applied"
    assert "auto_apply_id" in entry and entry["auto_apply_id"]
    assert "applied_at" in entry
    assert "before" in entry and "after" in entry
    assert entry["rollback_reference"]


def test_audit_trail_has_proposal_source(sandbox):
    """audit trail must include proposal_source field."""
    _setup_run(sandbox, flag=True)
    run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    log_entries = json.loads(sandbox["auto_apply_log_path"].read_text(encoding="utf-8"))
    assert "proposal_source" in log_entries[0]
    assert log_entries[0]["proposal_source"] in ("llm", "deterministic_fallback", "unknown")


def test_audit_trail_has_rollback_reference(sandbox):
    """audit trail must include rollback_reference."""
    _setup_run(sandbox, flag=True)
    run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    log_entries = json.loads(sandbox["auto_apply_log_path"].read_text(encoding="utf-8"))
    assert log_entries[0]["rollback_reference"]


def test_audit_trail_has_activation_source(sandbox):
    """audit trail must include activation_source field."""
    _setup_run(sandbox, flag=True)
    run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    log_entries = json.loads(sandbox["auto_apply_log_path"].read_text(encoding="utf-8"))
    assert "activation_source" in log_entries[0]
    assert log_entries[0]["activation_source"] in ("policy", "override_file")


def test_rollback_payload_written_on_success(sandbox):
    """Rollback payload must be written with correct before/after."""
    action, _ = _setup_run(sandbox, flag=True)
    run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert sandbox["rollback_payload_path"].exists()
    payload = json.loads(sandbox["rollback_payload_path"].read_text(encoding="utf-8"))
    assert payload["before"]["meta_description"] == action["before"]["meta_description"]
    assert payload["after"]["meta_description"] == action["proposal"]["meta_description"]
    assert payload["rollback_mode"] == "single_file_revert"


def test_execution_report_approval_mode_auto_applied(sandbox):
    """Execution report must show approval_mode=auto_applied."""
    _setup_run(sandbox, flag=True)
    run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    report = json.loads(sandbox["execution_report_path"].read_text(encoding="utf-8"))
    assert report["metadata"]["approval_mode"] == "auto_applied"
    assert report["metadata"]["approved_by"] == APPROVED_BY
    assert report["metadata"]["create_pull_request"] is False
    assert report["metadata"]["commit_changes"] is False


def test_status_report_written_on_success(sandbox):
    """Status report must be written after successful apply."""
    _setup_run(sandbox, flag=True)
    run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert sandbox["status_report_path"].exists()
    status = json.loads(sandbox["status_report_path"].read_text(encoding="utf-8"))
    assert status["activation"]["enabled"] is True
    assert status["last_apply"] is not None
    assert status["last_apply"]["url"] == "/test/page"


def test_status_report_written_when_flag_off(sandbox):
    """Status report must be written even when flag is OFF."""
    action, page = _setup_run(sandbox, flag=False)

    run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert sandbox["status_report_path"].exists()
    status = json.loads(sandbox["status_report_path"].read_text(encoding="utf-8"))
    assert status["activation"]["enabled"] is False


# ─── 3. Tier guards ───────────────────────────────────────────────────────────

def test_run_blocked_tier_a(sandbox):
    """Tier A must be blocked even with flag ON."""
    action, page = _setup_run(sandbox, flag=True, tier="A")
    original = page.read_text(encoding="utf-8")
    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is False
    assert page.read_text(encoding="utf-8") == original


def test_run_blocked_tier_b(sandbox):
    """Tier B must be blocked even with flag ON."""
    action, page = _setup_run(sandbox, flag=True, tier="B")
    original = page.read_text(encoding="utf-8")
    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is False
    assert page.read_text(encoding="utf-8") == original


def test_run_blocked_money_page(sandbox):
    """Money page must be blocked."""
    action, page = _setup_run(sandbox, flag=True, is_money=True)
    original = page.read_text(encoding="utf-8")
    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is False
    assert page.read_text(encoding="utf-8") == original


def test_run_blocked_pillar_page(sandbox):
    """Pillar page (is_pillar_page=True in plan) must be blocked."""
    action, page = _setup_run(sandbox, flag=True, is_pillar=True)
    original = page.read_text(encoding="utf-8")
    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is False
    assert page.read_text(encoding="utf-8") == original


def test_run_blocked_multiple_candidates(sandbox):
    """More than 1 candidate must be blocked (max=1)."""
    action, page = _setup_run(sandbox, flag=True, multi_candidates=True)
    original = page.read_text(encoding="utf-8")
    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is False
    assert page.read_text(encoding="utf-8") == original


def test_run_blocked_action_type_not_in_allowlist(sandbox):
    """meta_title_update (not in allowlist) must be blocked."""
    action, page = _setup_run(sandbox, flag=True, action_type="meta_title_update")
    original = page.read_text(encoding="utf-8")
    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is False
    assert page.read_text(encoding="utf-8") == original


# ─── 4. Proposal validity guard ───────────────────────────────────────────────

def test_run_blocked_invalid_proposal_with_quotes(sandbox):
    """Proposal containing double quotes must be blocked."""
    bad_proposal = 'Animatori "premium" pentru petreceri copii in Bucuresti. Suna: 0722 744 377.'
    action, page = _setup_run(sandbox, flag=True, proposal_desc=bad_proposal)
    original = page.read_text(encoding="utf-8")
    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is False
    assert page.read_text(encoding="utf-8") == original


# ─── 5. File drift guard ──────────────────────────────────────────────────────

def test_run_blocked_file_drift(sandbox):
    """If file content differs from before-state in plan, block."""
    action, page = _setup_run(sandbox, flag=True,
                               before_desc="Descriere veche de test pentru pagina.")
    _write(page, '<Layout description="Continut complet diferit in fisier.">\n</Layout>\n')
    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is False


# ─── 6. Pillar registry guard ─────────────────────────────────────────────────

def test_run_blocked_url_in_pillar_registry_even_if_plan_says_not_pillar(sandbox):
    """URL in pillar registry must be blocked even if is_pillar_page=False in plan."""
    # Register the URL as pillar
    _write_json(sandbox["pillar_registry_path"], {
        "schema_version": "1.0",
        "pillar_pages": ["/test/page"],
    })
    # Plan explicitly says is_pillar_page=False (the vulnerability)
    action, page = _setup_run(sandbox, flag=True, is_pillar=False)
    original = page.read_text(encoding="utf-8")

    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )

    assert result is False, "URL in pillar registry must be blocked regardless of plan flag"
    assert page.read_text(encoding="utf-8") == original, "File must not be modified"


def test_pillar_registry_not_in_registry_passes(sandbox):
    """URL NOT in pillar registry should pass the registry guard."""
    _write_json(sandbox["pillar_registry_path"], {
        "schema_version": "1.0",
        "pillar_pages": ["/some-other-pillar"],
    })
    blockers = check_pillar_registry("/test/page", sandbox["pillar_registry_path"])
    assert blockers == []


def test_pillar_registry_in_registry_blocked(sandbox):
    """URL in pillar registry returns blocker."""
    _write_json(sandbox["pillar_registry_path"], {
        "schema_version": "1.0",
        "pillar_pages": ["/animatori-petreceri-copii"],
    })
    blockers = check_pillar_registry("/animatori-petreceri-copii", sandbox["pillar_registry_path"])
    assert "pillar_page_in_registry" in blockers


def test_pillar_registry_animatori_petreceri_copii_is_pillar():
    """
    /animatori-petreceri-copii must be in the real pillar registry.
    Prevents recurrence of PR #88 smoke test vulnerability.
    """
    from agent.tasks.seo_level5_auto_apply import PILLAR_REGISTRY_PATH
    blockers = check_pillar_registry("/animatori-petreceri-copii", PILLAR_REGISTRY_PATH)
    assert "pillar_page_in_registry" in blockers, (
        "/animatori-petreceri-copii must be in pillar_pages_registry.json. "
        "This was the page incorrectly marked as non-pillar in PR #88 smoke test."
    )


# ─── 7. Cooldown guard ────────────────────────────────────────────────────────

def _make_log_entry(url: str, applied_at_offset_days: int) -> dict:
    """Helper: build a log entry for a URL applied N days ago."""
    applied_at = datetime.now(timezone.utc) - timedelta(days=applied_at_offset_days)
    return {
        "auto_apply_id": str(uuid.uuid4()),
        "url": url,
        "applied_at": applied_at.isoformat(),
        "approved_by": "system_auto_apply",
        "approval_mode": "auto_applied",
    }


def test_cooldown_blocks_url_applied_1_day_ago(sandbox):
    """URL applied 1 day ago must be blocked by cooldown."""
    log_path = sandbox["auto_apply_log_path"]
    _write_json(log_path, [_make_log_entry("/test/page", applied_at_offset_days=1)])

    blockers = check_url_cooldown("/test/page", log_path=log_path, days=14)
    assert len(blockers) > 0
    assert any("cooldown" in b for b in blockers)


def test_cooldown_allows_url_applied_15_days_ago(sandbox):
    """URL applied 15 days ago must NOT be blocked by cooldown (> 14 day window)."""
    log_path = sandbox["auto_apply_log_path"]
    _write_json(log_path, [_make_log_entry("/test/page", applied_at_offset_days=15)])

    blockers = check_url_cooldown("/test/page", log_path=log_path, days=14)
    assert blockers == []


def test_cooldown_allows_url_never_applied(sandbox):
    """URL never applied must have no cooldown blockers."""
    log_path = sandbox["auto_apply_log_path"]
    _write_json(log_path, [_make_log_entry("/other/page", applied_at_offset_days=1)])

    blockers = check_url_cooldown("/test/page", log_path=log_path, days=14)
    assert blockers == []


def test_cooldown_blocks_run_if_url_in_cooldown(sandbox):
    """Integration: run blocked if URL is in cooldown window."""
    # Seed audit log with recent apply for the same URL
    _write_json(sandbox["auto_apply_log_path"], [
        _make_log_entry("/test/page", applied_at_offset_days=3)
    ])

    action, page = _setup_run(sandbox, flag=True)
    original = page.read_text(encoding="utf-8")

    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )

    assert result is False, "Run must be blocked when URL is in cooldown"
    assert page.read_text(encoding="utf-8") == original


def test_cooldown_allows_run_if_url_outside_cooldown(sandbox):
    """Integration: run allowed if last apply for URL is outside cooldown window."""
    # Seed audit log with old apply (16 days ago)
    _write_json(sandbox["auto_apply_log_path"], [
        _make_log_entry("/test/page", applied_at_offset_days=16)
    ])

    action, page = _setup_run(sandbox, flag=True)

    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )

    assert result is True, "Run must be allowed when URL is outside cooldown"


# ─── 8. Override file — priority over policy ──────────────────────────────────

def test_override_file_enables_apply_when_policy_disabled(sandbox):
    """Override file with enabled=true activates apply even if policy has enabled=false."""
    action, page = _setup_run(sandbox, flag=False)  # policy OFF
    # Override enables
    _write_json(sandbox["override_path"], {"enabled": True})

    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is True, "Override file enabled=true must activate apply"


def test_override_file_disabled_blocks_even_if_policy_enabled(sandbox):
    """Override file with enabled=false blocks apply even if policy has enabled=true."""
    action, page = _setup_run(sandbox, flag=True)  # policy ON
    original = page.read_text(encoding="utf-8")
    # Override disables
    _write_json(sandbox["override_path"], {"enabled": False})

    result = run_controlled_auto_apply(
        pages_dir=sandbox["pages_dir"],
        policy_path=sandbox["policy_path"],
        apply_plan_path=sandbox["apply_plan_path"],
        override_path=sandbox["override_path"],
        pillar_registry_path=sandbox["pillar_registry_path"],
        log_path=sandbox["auto_apply_log_path"],
    )
    assert result is None, "Override file enabled=false must block (file OFF sentinel)"
    assert page.read_text(encoding="utf-8") == original


def test_activation_source_is_policy_when_no_override(sandbox):
    """get_activation_source returns 'policy' when only policy is enabled."""
    policy = _base_policy(flag=True)
    source = get_activation_source(policy, override_path=sandbox["override_path"])
    assert source == "policy"


def test_activation_source_is_override_file(sandbox):
    """get_activation_source returns 'override_file' when override file is present."""
    policy = _base_policy(flag=False)  # policy OFF
    _write_json(sandbox["override_path"], {"enabled": True})
    source = get_activation_source(policy, override_path=sandbox["override_path"])
    assert source == "override_file"


def test_activation_source_is_disabled_when_both_off(sandbox):
    """get_activation_source returns 'disabled' when both off."""
    policy = _base_policy(flag=False)
    _write_json(sandbox["override_path"], {"enabled": False})
    source = get_activation_source(policy, override_path=sandbox["override_path"])
    assert source == "disabled"


# ─── 9. Unit-level guards ─────────────────────────────────────────────────────

def test_check_auto_apply_enabled_false_when_not_set(sandbox):
    assert check_auto_apply_enabled({}, override_path=sandbox["override_path"]) is False


def test_check_auto_apply_enabled_false_when_false(sandbox):
    assert check_auto_apply_enabled(
        {"auto_apply_config": {"enabled": False}},
        override_path=sandbox["override_path"],
    ) is False


def test_check_auto_apply_enabled_true_when_true(sandbox):
    assert check_auto_apply_enabled(
        {"auto_apply_config": {"enabled": True}},
        override_path=sandbox["override_path"],
    ) is True


def test_validate_proposal_valid():
    good = "Animatori petreceri copii Bucuresti. Costume premium, 30 personaje. Pachete de la 490 lei. Rezerva: 0722 744 377."
    assert validate_proposal(good) == []


def test_validate_proposal_too_short():
    assert "proposal_too_short" in validate_proposal("Prea scurt.")


def test_validate_proposal_html_blocked():
    assert "proposal_contains_html" in validate_proposal("Text <b>bold</b> meta.")


def test_validate_proposal_newline_blocked():
    assert "proposal_contains_newline" in validate_proposal("Text cu\nnewline inclus.")
