"""
tests/test_seo_level5_meta_description_dry_run.py — PR #54

Valideaza executorul dry-run Level 5:
- refuza daca actiunea nu este in allowed_actions
- refuza daca execution_mode != dry_run_only
- selecteaza exclusiv Tier C non-money non-pillar
- limiteaza la 1 candidat per run
- nu modifica fisierele sursa
- produce report cu status=proposed_only si applied=0
"""
import json
from pathlib import Path

import pytest

import agent.tasks.seo_level5_meta_description_dry_run as dry_run_module
from agent.tasks.seo_level5_meta_description_dry_run import (
    ACTION_TYPE,
    PolicyValidationError,
    generate_dry_run_report,
    resolve_eligible_candidates,
    run_meta_description_dry_run,
)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@pytest.fixture
def base_policy() -> dict:
    return {
        "schema_version": "1.1",
        "mode": "controlled_dry_run_only",
        "description": "PR #54 dry-run only",
        "allowed_actions": ["meta_description_update"],
        "forbidden_actions": [
            "change_canonical", "change_robots", "change_noindex", "change_registry",
            "change_cluster_schema", "change_internal_ownership",
            "modify_pillar_page", "modify_sitemap_policy",
        ],
        "low_risk_eligible_actions": ["meta_title_update", "meta_description_update"],
        "dry_run_required": True,
        "approval_gate": "manual",
        "rollback_required": True,
        "feedback_loop_mode": "observability_only",
        "feedback_loop_permitted_signals": [
            "impressions", "clicks", "ctr", "average_position",
            "owner_share_delta", "forbidden_delta", "trend_status",
        ],
        "feedback_loop_forbidden_claims": [
            "serp_rank_1_claim",
            "business_outcome_validation_without_real_serp",
            "auto_interpreted_seo_win",
        ],
        "tier_restrictions": {"A": "read_only", "B": "restricted", "C": "low_risk_eligible"},
        "max_actions_per_run": 1,
        "requires_human_review_for": ["all_tier_a", "all_money_pages", "all_registry_touches"],
        "action_activation": {
            "meta_description_update": {
                "execution_mode": "dry_run_only",
                "tier_allowlist": ["C"],
                "tier_denylist": ["A", "B"],
                "money_pages": "forbidden",
                "pillar_pages": "forbidden",
                "registry_touches": "forbidden",
                "max_candidates_per_run": 1,
                "requires_manual_approval_before_apply": True,
                "report_only": True,
                "write_files": False,
                "create_pull_request": False,
                "commit_changes": False,
            }
        },
    }


@pytest.fixture
def sandbox(tmp_path, monkeypatch, base_policy):
    config_dir = tmp_path / "config" / "seo"
    reports_dir = tmp_path / "reports" / "superparty"

    policy_path = config_dir / "level5_action_policy.json"
    health_path = reports_dir / "seo_cluster_health.json"
    priority_path = reports_dir / "seo_cluster_priority.json"
    trend_path = reports_dir / "seo_trend_delta.json"
    output_path = reports_dir / "seo_level5_dry_run_actions.json"

    _write_json(policy_path, base_policy)
    _write_json(health_path, {"metadata": {}, "clusters": {}})
    _write_json(priority_path, {"metadata": {}, "clusters": {}})
    _write_json(trend_path, {"metadata": {}, "clusters": []})

    monkeypatch.setattr(dry_run_module, "POLICY_PATH", policy_path)
    monkeypatch.setattr(dry_run_module, "HEALTH_PATH", health_path)
    monkeypatch.setattr(dry_run_module, "PRIORITY_PATH", priority_path)
    monkeypatch.setattr(dry_run_module, "TREND_PATH", trend_path)
    monkeypatch.setattr(dry_run_module, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(dry_run_module, "assert_inputs_ready", lambda: {"status": "ready"})

    return {
        "policy_path": policy_path,
        "health_path": health_path,
        "priority_path": priority_path,
        "trend_path": trend_path,
        "output_path": output_path,
    }


def _write_policy(sandbox, policy: dict) -> None:
    _write_json(sandbox["policy_path"], policy)


def _write_health(sandbox, clusters: dict) -> None:
    _write_json(
        sandbox["health_path"],
        {"metadata": {"generated_at": "2026-03-07T14:00:00Z"}, "clusters": clusters},
    )


# ─── Policy guard tests ───────────────────────────────────────────────────────

def test_refuses_when_action_not_allowed(sandbox, base_policy):
    policy = dict(base_policy)
    policy["allowed_actions"] = []
    _write_policy(sandbox, policy)

    result = run_meta_description_dry_run()

    assert result is False
    assert not sandbox["output_path"].exists()


def test_refuses_non_dry_run_mode(sandbox, base_policy):
    policy = dict(base_policy)
    activation = dict(base_policy["action_activation"]["meta_description_update"])
    activation["execution_mode"] = "apply_real"
    policy["action_activation"] = {"meta_description_update": activation}
    _write_policy(sandbox, policy)

    with pytest.raises(PolicyValidationError):
        generate_dry_run_report(ACTION_TYPE)


# ─── Candidate selection tests ────────────────────────────────────────────────

def test_selects_only_tier_c_non_money_candidate(sandbox):
    _write_health(sandbox, {
        "cluster_c_ok": {
            "is_money_cluster": False,
            "urls": {"/blog/test-tier-c": {"classification": "owner"}},
        },
        "cluster_money": {
            "is_money_cluster": True,
            "urls": {"/ghid/test-money-c": {"classification": "owner"}},
        },
        "cluster_tier_b": {
            "is_money_cluster": False,
            "urls": {"/petreceri/sector-2": {"classification": "owner"}},
        },
        "cluster_tier_a": {
            "is_money_cluster": False,
            "urls": {"/animatori-petreceri-copii": {"classification": "owner"}},
        },
    })

    policy = dry_run_module.load_level5_policy()
    inputs = dry_run_module.load_candidate_inputs()
    candidates = resolve_eligible_candidates(inputs, policy)

    assert len(candidates) == 1
    assert candidates[0].url == "/blog/test-tier-c"
    assert candidates[0].tier == "C"
    assert candidates[0].is_money_page is False
    assert candidates[0].is_pillar_page is False


def test_never_selects_tier_a(sandbox):
    _write_health(sandbox, {
        "cluster_a_only": {
            "is_money_cluster": False,
            "urls": {
                "/animatori-petreceri-copii": {"classification": "owner"},
                "/petreceri/bucuresti": {"classification": "owner"},
            },
        }
    })

    policy = dry_run_module.load_level5_policy()
    inputs = dry_run_module.load_candidate_inputs()
    candidates = resolve_eligible_candidates(inputs, policy)

    assert candidates == []


def test_never_selects_tier_b_in_pr54(sandbox):
    _write_health(sandbox, {
        "cluster_b_only": {
            "is_money_cluster": False,
            "urls": {
                "/petreceri/sector-1": {"classification": "owner"},
                "/petreceri/sector-6": {"classification": "owner"},
            },
        }
    })

    policy = dry_run_module.load_level5_policy()
    inputs = dry_run_module.load_candidate_inputs()
    candidates = resolve_eligible_candidates(inputs, policy)

    assert candidates == []


def test_never_selects_money_pages(sandbox):
    _write_health(sandbox, {
        "cluster_money_c": {
            "is_money_cluster": True,
            "urls": {"/resursa-tier-c": {"classification": "owner"}},
        }
    })

    policy = dry_run_module.load_level5_policy()
    inputs = dry_run_module.load_candidate_inputs()
    candidates = resolve_eligible_candidates(inputs, policy)

    assert candidates == []


def test_never_selects_pillar_pages(sandbox):
    _write_health(sandbox, {
        "cluster_pillar": {
            "is_money_cluster": False,
            "urls": {"/petreceri/ilfov": {"classification": "owner"}},
        }
    })

    policy = dry_run_module.load_level5_policy()
    inputs = dry_run_module.load_candidate_inputs()
    candidates = resolve_eligible_candidates(inputs, policy)

    assert candidates == []


def test_limits_to_one_candidate_per_run(sandbox):
    _write_health(sandbox, {
        "cluster_c_1": {
            "is_money_cluster": False,
            "urls": {"/articol/test-1": {"classification": "owner"}},
        },
        "cluster_c_2": {
            "is_money_cluster": False,
            "urls": {"/articol/test-2": {"classification": "owner"}},
        },
    })

    report = generate_dry_run_report(ACTION_TYPE)

    assert report["metadata"]["total_candidates"] == 1
    assert len(report["actions"]) == 1


# ─── Report integrity tests ───────────────────────────────────────────────────

def test_generates_report_without_modifying_source_files(sandbox):
    original_health = {
        "metadata": {"generated_at": "2026-03-07T14:00:00Z"},
        "clusters": {
            "cluster_c_ok": {
                "is_money_cluster": False,
                "urls": {"/blog/fara-modificari": {"classification": "owner"}},
            }
        },
    }
    original_priority = {"metadata": {}, "clusters": {}}
    original_trend = {"metadata": {}, "clusters": []}

    _write_json(sandbox["health_path"], original_health)
    _write_json(sandbox["priority_path"], original_priority)
    _write_json(sandbox["trend_path"], original_trend)

    result = run_meta_description_dry_run()

    assert result is True
    assert sandbox["output_path"].exists()

    with open(sandbox["health_path"], "r", encoding="utf-8") as f:
        assert json.load(f) == original_health
    with open(sandbox["priority_path"], "r", encoding="utf-8") as f:
        assert json.load(f) == original_priority
    with open(sandbox["trend_path"], "r", encoding="utf-8") as f:
        assert json.load(f) == original_trend


def test_report_marks_status_proposed_only(sandbox):
    _write_health(sandbox, {
        "cluster_c_ok": {
            "is_money_cluster": False,
            "urls": {"/blog/status-proposed": {"classification": "owner"}},
        }
    })

    result = run_meta_description_dry_run()
    assert result is True

    with open(sandbox["output_path"], "r", encoding="utf-8") as f:
        report = json.load(f)

    assert report["metadata"]["mode"] == "dry_run_only"
    assert report["metadata"]["applied"] == 0
    assert report["metadata"]["action_type"] == "meta_description_update"
    assert len(report["actions"]) == 1
    assert report["actions"][0]["status"] == "proposed_only"


# ─── Policy contract tests (din policy real, nu din sandbox) ─────────────────

def test_policy_allows_only_meta_description_update(sandbox):
    policy = dry_run_module.load_level5_policy()
    assert policy["allowed_actions"] == ["meta_description_update"]


def test_policy_max_actions_per_run_is_one(sandbox):
    policy = dry_run_module.load_level5_policy()
    assert policy["max_actions_per_run"] == 1
    assert (
        policy["action_activation"]["meta_description_update"]["max_candidates_per_run"]
        == 1
    )
