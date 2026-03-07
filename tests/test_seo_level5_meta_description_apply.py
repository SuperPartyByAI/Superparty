"""
tests/test_seo_level5_meta_description_apply.py — PR #58

Test matrix ceruta de auditor (15 cazuri + extensii):
- refuza cand policy mode nu e single_apply
- refuza cand write_files != true
- refuza cand exista mai mult de o actiune ready
- refuza Tier A/B chiar daca e in plan
- refuza money page chiar daca e ready
- refuza pillar page chiar daca e ready
- refuza cand fișierul țintă lipsește
- refuza cand structura fișierului nu e sigura (unsupported)
- refuza cand before-state nu mai corespunde planului
- aplica un update frontmatter description corect
- aplica un update meta tag description corect
- scrie rollback payload
- scrie execution report cu applied=1
- nu creeaza commit sau PR artifacts
- sandbox complet izolat de sursele reale
"""
import json
import uuid
import pytest
from pathlib import Path
from datetime import datetime, timezone

import agent.tasks.seo_level5_meta_description_apply as apply_module
from agent.tasks.seo_level5_meta_description_apply import (
    ACTION_TYPE,
    ApplyError,
    PolicyApplyError,
    validate_policy_for_single_apply,
    select_single_ready_action,
    resolve_target_file,
    extract_current_meta_description,
    validate_target_still_matches_plan,
    apply_meta_description_to_file,
    build_rollback_payload,
    reconcile_with_live_approval_log,
    run_single_apply,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _base_policy() -> dict:
    return {
        "schema_version": "1.2",
        "mode": "controlled_single_apply",
        "allowed_actions": ["meta_description_update"],
        "dry_run_required": True,
        "approval_gate": "manual",
        "rollback_required": True,
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
                "report_only": False,
                "write_files": True,
                "create_pull_request": False,
                "commit_changes": False,
                "rollback_mode": "single_file_revert",
            }
        },
    }


def _make_ready_action(action_id: str = "id-test", url: str = "/blog/test",
                       tier: str = "C", is_money: bool = False,
                       is_pillar: bool = False,
                       before_desc: str = "Descriere veche.",
                       proposal_desc: str = "Descriere noua propusa.") -> dict:
    return {
        "plan_id": str(uuid.uuid4()),
        "action_id": action_id,
        "action_type": ACTION_TYPE,
        "url": url,
        "tier": tier,
        "is_money_page": is_money,
        "is_pillar_page": is_pillar,
        "preflight": {},
        "ready_to_apply": True,
        "before": {"meta_description": before_desc},
        "proposal": {"meta_description": proposal_desc},
        "approval_record": {
            "decision": "approved",
            "decided_by": "ops-manual-review",
            "decided_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def _make_apply_plan(ready_actions: list, blocked: list = None) -> dict:
    return {
        "metadata": {
            "schema_version": "1.0",
            "mode": "apply_plan_only",
            "total_eligible": len(ready_actions),
            "applied": 0,
        },
        "preflight_summary": {"policy_valid": True, "all_checks_passed": True, "blocking_issues": []},
        "plan": ready_actions,
        "blocked": blocked or [],
    }


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports" / "superparty"
    config_dir = tmp_path / "config" / "seo"
    pages_dir = tmp_path / "src" / "pages"

    policy_path = config_dir / "level5_action_policy.json"
    apply_plan_path = reports_dir / "seo_level5_apply_plan.json"
    approval_log_path = reports_dir / "seo_level5_approval_log.json"
    execution_report_path = reports_dir / "seo_level5_apply_execution.json"
    rollback_payload_path = reports_dir / "seo_level5_rollback_payload.json"

    monkeypatch.setattr(apply_module, "POLICY_PATH", policy_path)
    monkeypatch.setattr(apply_module, "APPLY_PLAN_PATH", apply_plan_path)
    monkeypatch.setattr(apply_module, "APPROVAL_LOG_PATH", approval_log_path)
    monkeypatch.setattr(apply_module, "EXECUTION_REPORT_PATH", execution_report_path)
    monkeypatch.setattr(apply_module, "ROLLBACK_PAYLOAD_PATH", rollback_payload_path)
    monkeypatch.setattr(apply_module, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(apply_module, "PAGES_DIR", pages_dir)
    monkeypatch.setattr(apply_module, "ROOT_DIR", tmp_path)

    _write_json(policy_path, _base_policy())
    _write_json(apply_plan_path, _make_apply_plan([]))

    return {
        "policy_path": policy_path,
        "apply_plan_path": apply_plan_path,
        "execution_report_path": execution_report_path,
        "rollback_payload_path": rollback_payload_path,
        "pages_dir": pages_dir,
        "tmp_path": tmp_path,
    }


# ─── 1. Policy mode guards ────────────────────────────────────────────────────

def test_refuses_when_policy_not_single_apply_mode():
    bad_policy = dict(_base_policy())
    bad_policy["mode"] = "controlled_dry_run_only"
    with pytest.raises(PolicyApplyError, match="controlled_single_apply"):
        validate_policy_for_single_apply(bad_policy)


def test_refuses_when_write_files_not_true():
    bad_policy = dict(_base_policy())
    bad_policy["action_activation"]["meta_description_update"]["write_files"] = False
    with pytest.raises(PolicyApplyError, match="write_files"):
        validate_policy_for_single_apply(bad_policy)


def test_refuses_when_create_pull_request_not_false():
    bad_policy = dict(_base_policy())
    bad_policy["action_activation"]["meta_description_update"]["create_pull_request"] = True
    with pytest.raises(PolicyApplyError, match="create_pull_request"):
        validate_policy_for_single_apply(bad_policy)


def test_refuses_when_commit_changes_not_false():
    bad_policy = dict(_base_policy())
    bad_policy["action_activation"]["meta_description_update"]["commit_changes"] = True
    with pytest.raises(PolicyApplyError, match="commit_changes"):
        validate_policy_for_single_apply(bad_policy)


# ─── 2. Action selection guards ───────────────────────────────────────────────

def test_refuses_when_more_than_one_ready_action_exists():
    plan = _make_apply_plan([
        _make_ready_action("id-1"),
        _make_ready_action("id-2"),
    ])
    with pytest.raises(ApplyError, match="batch apply"):
        select_single_ready_action(plan)


def test_refuses_tier_a_action_even_if_present_in_plan():
    plan = _make_apply_plan([_make_ready_action("id-a", tier="A")])
    with pytest.raises(ApplyError, match="Tier A"):
        select_single_ready_action(plan)


def test_refuses_tier_b_action_even_if_present_in_plan():
    plan = _make_apply_plan([_make_ready_action("id-b", tier="B")])
    with pytest.raises(ApplyError, match="Tier B"):
        select_single_ready_action(plan)


def test_refuses_money_page_even_if_ready():
    plan = _make_apply_plan([_make_ready_action("id-m", is_money=True)])
    with pytest.raises(ApplyError, match=r"[Mm]oney"):
        select_single_ready_action(plan)


def test_refuses_pillar_page_even_if_ready():
    plan = _make_apply_plan([_make_ready_action("id-p", is_pillar=True)])
    with pytest.raises(ApplyError, match="[Pp]illar"):
        select_single_ready_action(plan)


# ─── 3. File resolution guards ────────────────────────────────────────────────

def test_refuses_when_target_file_missing(sandbox):
    action = _make_ready_action(url="/blog/inexistent")
    with pytest.raises(ApplyError, match="target_file_not_found"):
        resolve_target_file(action, sandbox["pages_dir"])


# ─── 4. Structure guard ───────────────────────────────────────────────────────

def test_refuses_when_target_file_structure_unsupported(tmp_path):
    page = tmp_path / "ambiguous.astro"
    _write(page, """---\nimport Layout from '../layouts/Layout.astro';\n---\n<p>No meta desc here.</p>\n""")
    with pytest.raises(ApplyError, match="unsupported_file_structure"):
        apply_meta_description_to_file(page, "Noua descriere.")


# ─── 5. Before-drift guard ────────────────────────────────────────────────────

def test_refuses_when_current_description_differs_from_expected_before(tmp_path):
    page = tmp_path / "drift.astro"
    _write(page, '---\ndescription = "Descriere actuala diferita."\n---\n')
    current = extract_current_meta_description(page)
    action = _make_ready_action(before_desc="Descriere veche originala.")
    issues = validate_target_still_matches_plan(action, current)
    assert len(issues) > 0
    assert "differs_from_plan" in issues[0]


# ─── 6. Successful apply — frontmatter ───────────────────────────────────────

def test_applies_single_frontmatter_description_update(tmp_path):
    page = tmp_path / "test.astro"
    _write(page, '---\nimport Layout from "../layouts/Layout.astro";\ndescription = "Descriere veche."\n---\n<Layout></Layout>\n')
    result = apply_meta_description_to_file(page, "Descriere noua corecta.")
    assert result["strategy"] == "frontmatter_prop"
    content = page.read_text(encoding="utf-8")
    assert "Descriere noua corecta." in content
    assert "Descriere veche." not in content


def test_applies_single_meta_tag_description_update(tmp_path):
    page = tmp_path / "test_meta.astro"
    _write(page, '---\nimport Layout from "../layouts/Layout.astro";\n---\n<meta name="description" content="Descriere veche." />\n')
    result = apply_meta_description_to_file(page, "Descriere noua meta tag.")
    assert result["strategy"] == "meta_tag"
    content = page.read_text(encoding="utf-8")
    assert "Descriere noua meta tag." in content
    assert "Descriere veche." not in content


# ─── 7. Rollback payload ─────────────────────────────────────────────────────

def test_writes_rollback_payload(tmp_path):
    page = tmp_path / "rollback.astro"
    _write(page, "")  # file content irrelevant for build_rollback_payload
    payload = build_rollback_payload(page, "Veche.", "Noua.")
    payload["action_id"] = "id-rb"
    assert payload["rollback_mode"] == "single_file_revert"
    assert payload["before"]["meta_description"] == "Veche."
    assert payload["after"]["meta_description"] == "Noua."
    assert payload["action_id"] == "id-rb"
    assert "file_path" in payload  # present as string, relative path may vary
    assert isinstance(payload["file_path"], str)



# ─── 8. Full flow — execution report ─────────────────────────────────────────

def test_writes_execution_report_with_applied_one(sandbox):
    # Create a real target file
    page = sandbox["pages_dir"] / "blog" / "articol.astro"
    _write(page, '---\ndescription = "Descriere veche de test."\n---\n<Layout></Layout>\n')

    action = _make_ready_action(
        action_id="id-exec", url="/blog/articol",
        before_desc="Descriere veche de test.",
        proposal_desc="Descriere noua de test."
    )
    _write_json(sandbox["apply_plan_path"], _make_apply_plan([action]))
    # PR #59: write live approval log matching the action
    _write_json(apply_module.APPROVAL_LOG_PATH, [_make_live_log_entry(
        "id-exec", url="/blog/articol",
        before_desc="Descriere veche de test.",
        proposal_desc="Descriere noua de test.",
    )])

    result = run_single_apply(pages_dir=sandbox["pages_dir"])

    assert result is True
    assert sandbox["execution_report_path"].exists()
    with open(sandbox["execution_report_path"], encoding="utf-8") as f:
        report = json.load(f)
    assert report["metadata"]["applied"] == 1
    assert report["metadata"]["create_pull_request"] is False
    assert report["metadata"]["commit_changes"] is False
    assert len(report["applied_actions"]) == 1
    assert report["applied_actions"][0]["action_id"] == "id-exec"


# ─── 9. No commit / no PR artifacts ─────────────────────────────────────────

def test_never_creates_commit_or_pull_request_artifacts(sandbox):
    page = sandbox["pages_dir"] / "blog" / "nocommit.astro"
    _write(page, '---\ndescription = "Fara commit."\n---\n')
    action = _make_ready_action(
        action_id="id-nc", url="/blog/nocommit",
        before_desc="Fara commit.",
        proposal_desc="Noua fara commit."
    )
    _write_json(sandbox["apply_plan_path"], _make_apply_plan([action]))
    # PR #59: live approval log required
    _write_json(apply_module.APPROVAL_LOG_PATH, [_make_live_log_entry(
        "id-nc", url="/blog/nocommit",
        before_desc="Fara commit.",
        proposal_desc="Noua fara commit.",
    )])

    run_single_apply(pages_dir=sandbox["pages_dir"])

    pr_file = sandbox["tmp_path"] / "pull_request.json"
    commit_log = sandbox["tmp_path"] / "commit.log"
    assert not pr_file.exists()
    assert not commit_log.exists()
    with open(sandbox["execution_report_path"], encoding="utf-8") as f:
        report = json.load(f)
    assert report["metadata"]["commit_changes"] is False
    assert report["metadata"]["create_pull_request"] is False


# ─── 10. Rollback payload content in full flow ───────────────────────────────

def test_full_flow_produces_rollback_payload(sandbox):
    page = sandbox["pages_dir"] / "articol-complet.astro"
    _write(page, '---\ndescription = "Descriere initiala."\n---\n')
    action = _make_ready_action(
        action_id="id-rb-flow", url="/articol-complet",
        before_desc="Descriere initiala.",
        proposal_desc="Descriere dupa apply."
    )
    _write_json(sandbox["apply_plan_path"], _make_apply_plan([action]))
    # PR #59: live approval log required
    _write_json(apply_module.APPROVAL_LOG_PATH, [_make_live_log_entry(
        "id-rb-flow", url="/articol-complet",
        before_desc="Descriere initiala.",
        proposal_desc="Descriere dupa apply.",
    )])

    result = run_single_apply(pages_dir=sandbox["pages_dir"])

    assert result is True
    assert sandbox["rollback_payload_path"].exists()
    with open(sandbox["rollback_payload_path"], encoding="utf-8") as f:
        rollback = json.load(f)
    assert rollback["before"]["meta_description"] == "Descriere initiala."
    assert rollback["after"]["meta_description"] == "Descriere dupa apply."
    assert rollback["rollback_mode"] == "single_file_revert"
    assert rollback["action_id"] == "id-rb-flow"


# ─── 11. Approval gate re-check guards (PR #58 hardening) ────────────────────

def test_refuses_when_approval_record_decision_not_approved():
    """select_single_ready_action must reject actions where approval_record.decision != approved."""
    action = _make_ready_action("id-not-approved")
    action["approval_record"]["decision"] = "rejected"  # tamper downstream
    plan = _make_apply_plan([action])
    with pytest.raises(ApplyError, match="approval_record.decision"):
        select_single_ready_action(plan)


def test_refuses_when_decided_by_empty():
    """select_single_ready_action must reject actions with empty decided_by."""
    action = _make_ready_action("id-no-operator")
    action["approval_record"]["decided_by"] = ""  # operator missing
    plan = _make_apply_plan([action])
    with pytest.raises(ApplyError, match="decided_by"):
        select_single_ready_action(plan)


# ─── 12. Quote-safe write guard (PR #58 hardening) ───────────────────────────

def test_refuses_when_proposal_contains_delimiter_quote_frontmatter(tmp_path):
    """
    If the file uses double-quote as frontmatter delimiter and the proposal contains
    a double-quote, apply must block to avoid file corruption.
    """
    page = tmp_path / "quote_test.astro"
    _write(page, '---\ndescription = "Descriere veche."\n---\n')
    # Proposal contains the same double-quote used as delimiter
    with pytest.raises(ApplyError, match="unsafe_proposal_contains_quote"):
        apply_meta_description_to_file(page, 'Descriere cu "ghilimele" duble.')


def test_refuses_when_proposal_contains_delimiter_quote_meta_tag(tmp_path):
    """
    If the meta_tag uses double-quote as content= delimiter and the proposal contains
    a double-quote, apply must block.
    """
    page = tmp_path / "quote_meta.astro"
    _write(page, '---\nimport L from "../layouts/Layout.astro";\n---\n<meta name="description" content="Descriere veche." />\n')
    with pytest.raises(ApplyError, match="unsafe_proposal_contains_quote"):
        apply_meta_description_to_file(page, 'Propunere cu "ghilimele".')


# ─── 13. Live approval reconciliation (PR #59) ────────────────────────────────

def _make_live_log_entry(action_id: str, url: str = "/blog/test",
                         decision: str = "approved", decided_by: str = "ops-review",
                         before_desc: str = "Descriere veche.",
                         proposal_desc: str = "Descriere noua propusa.",
                         decision_id: str = "dec-001") -> dict:
    return {
        "action_id": action_id,
        "decision_id": decision_id,
        "action_type": ACTION_TYPE,
        "url": url,
        "decision": decision,
        "decided_by": decided_by,
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "proposal_snapshot": {
            "before": {"meta_description": before_desc},
            "proposal": {"meta_description": proposal_desc},
        },
    }


def test_reconcile_blocks_when_live_record_missing(tmp_path, monkeypatch):
    """reconcile_with_live_approval_log must block if no matching entry in live log."""
    monkeypatch.setattr(apply_module, "APPROVAL_LOG_PATH",
                        tmp_path / "empty_log.json")
    _write_json(tmp_path / "empty_log.json", [])
    action = _make_ready_action("id-missing")
    with pytest.raises(ApplyError, match="live_approval_record_not_found"):
        reconcile_with_live_approval_log(action, action.get("approval_record"))


def test_reconcile_blocks_when_decision_not_approved(tmp_path, monkeypatch):
    """Block if live record exists but decision != approved."""
    log_path = tmp_path / "log.json"
    _write_json(log_path, [_make_live_log_entry("id-rej", decision="rejected")])
    monkeypatch.setattr(apply_module, "APPROVAL_LOG_PATH", log_path)
    action = _make_ready_action("id-rej")
    with pytest.raises(ApplyError, match="live_approval_decision_not_approved"):
        reconcile_with_live_approval_log(action, action.get("approval_record"))


def test_reconcile_blocks_on_duplicate_approved_records(tmp_path, monkeypatch):
    """Block if two approved records for same action_id exist."""
    log_path = tmp_path / "log.json"
    _write_json(log_path, [
        _make_live_log_entry("id-dup", decision_id="dec-A"),
        _make_live_log_entry("id-dup", decision_id="dec-B"),
    ])
    monkeypatch.setattr(apply_module, "APPROVAL_LOG_PATH", log_path)
    action = _make_ready_action("id-dup")
    with pytest.raises(ApplyError, match="live_approval_duplicate"):
        reconcile_with_live_approval_log(action, action.get("approval_record"))


def test_reconcile_blocks_when_decided_by_empty(tmp_path, monkeypatch):
    """Block if decided_by is empty in live record."""
    log_path = tmp_path / "log.json"
    _write_json(log_path, [_make_live_log_entry("id-noby", decided_by="")])
    monkeypatch.setattr(apply_module, "APPROVAL_LOG_PATH", log_path)
    action = _make_ready_action("id-noby")
    with pytest.raises(ApplyError, match="decided_by"):
        reconcile_with_live_approval_log(action, action.get("approval_record"))


def test_reconcile_blocks_on_url_mismatch(tmp_path, monkeypatch):
    """Block if live record url != plan action url."""
    log_path = tmp_path / "log.json"
    _write_json(log_path, [_make_live_log_entry("id-urlx", url="/alt/url")])
    monkeypatch.setattr(apply_module, "APPROVAL_LOG_PATH", log_path)
    action = _make_ready_action("id-urlx", url="/blog/test")
    with pytest.raises(ApplyError, match="live_approval_url_mismatch"):
        reconcile_with_live_approval_log(action, action.get("approval_record"))


def test_reconcile_succeeds_on_valid_live_record(tmp_path, monkeypatch):
    """reconcile_with_live_approval_log succeeds and returns live record when all checks pass."""
    log_path = tmp_path / "log.json"
    _write_json(log_path, [_make_live_log_entry("id-ok", url="/blog/test")])
    monkeypatch.setattr(apply_module, "APPROVAL_LOG_PATH", log_path)
    action = _make_ready_action("id-ok", url="/blog/test")
    live = reconcile_with_live_approval_log(action, action.get("approval_record"))
    assert live["action_id"] == "id-ok"
    assert live["decision"] == "approved"


# ─── 14. Observability + lineage in execution report (PR #59) ─────────────────

def test_execution_report_contains_full_lineage(sandbox):
    """Execution report must contain execution_id, plan_id, decision_id, rollback_ready, after_value_verified."""
    page = sandbox["pages_dir"] / "blog" / "lineage.astro"
    _write(page, '---\ndescription = "Descriere veche lineage."\n---\n<Layout></Layout>\n')

    action = _make_ready_action(
        action_id="id-lin", url="/blog/lineage",
        before_desc="Descriere veche lineage.",
        proposal_desc="Descriere noua lineage.",
    )
    plan_id = action["plan_id"]
    _write_json(sandbox["apply_plan_path"], _make_apply_plan([action]))

    # Write live approval log matching the action
    log_entry = _make_live_log_entry(
        "id-lin", url="/blog/lineage",
        before_desc="Descriere veche lineage.",
        proposal_desc="Descriere noua lineage.",
    )
    _write_json(sandbox["apply_plan_path"].parent / "seo_level5_approval_log.json", [log_entry])
    import agent.tasks.seo_level5_meta_description_apply as am
    sandbox_approval_log = sandbox["apply_plan_path"].parent / "seo_level5_approval_log.json"
    # monkeypatch already points APPROVAL_LOG_PATH to reports_dir via sandbox fixture
    # sandbox fixture patches ROOT_DIR to tmp_path, APPROVAL_LOG_PATH remains in REPORTS_DIR
    # We need to also write the live log to the sandbox APPROVAL_LOG_PATH
    _write_json(apply_module.APPROVAL_LOG_PATH, [log_entry])

    result = run_single_apply(pages_dir=sandbox["pages_dir"])
    assert result is True

    with open(sandbox["execution_report_path"], encoding="utf-8") as f:
        report = json.load(f)

    aa = report["applied_actions"][0]
    assert "execution_id" in aa and aa["execution_id"]
    assert "plan_id" in aa
    assert "decision_id" in aa
    assert "policy_version" in aa
    assert aa.get("rollback_ready") is True
    assert aa.get("after_value_verified") is True
