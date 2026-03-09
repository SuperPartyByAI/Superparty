"""
tests/test_seo_level5_dynamic_cooldown.py

Suite de teste pentru cooldown dinamic L5 auto-apply.

Acopera:
- evaluate_url_reapply_readiness() — toate ramurile decision tree
- Scenariu complet: T0, ziua5, ziua8 (fara date), ziua8 (cu date), ziua15, rollback21
- check_url_cooldown() wrapper backwards-compat
- generate_status_report() cooldown_config si rollback_cooldown_urls
- Guardrails intacte: override, pillar pages, max 1 candidat
"""
import json
import uuid
import pytest
from pathlib import Path
from datetime import datetime, timedelta, timezone

import agent.tasks.seo_level5_auto_apply as auto_module
from agent.tasks.seo_level5_auto_apply import (
    evaluate_url_reapply_readiness,
    check_url_cooldown,
    load_cooldown_config,
    ReapplyReadiness,
    generate_status_report,
    run_controlled_auto_apply,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _log_entry(url: str, days_ago: float = 0.0, approval_mode: str = "auto_applied") -> dict:
    applied_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {
        "auto_apply_id": str(uuid.uuid4()),
        "url": url,
        "approved_by": "system_auto_apply",
        "approval_mode": approval_mode,
        "applied_at": applied_at.isoformat(),
        "proposal_source": "deterministic_fallback",
        "strategy": "layout_prop",
        "before": {"meta_description": "Vechi."},
        "after": {"meta_description": "Nou."},
        "policy_version": "1.3",
    }


def _gsc_data(url: str, impressions: int) -> dict:
    return {
        "rows": [
            {"url": f"https://www.superparty.ro{url}", "impressions": impressions, "ctr": 0.05, "position": 5.0}
        ]
    }


@pytest.fixture
def cooldown_config_file(tmp_path):
    path = tmp_path / "auto_apply_cooldown_config.json"
    _write_json(path, {
        "min_reapply_days": 7,
        "min_impressions_for_reapply": 80,
        "max_reapply_days_without_data": 14,
        "rollback_cooldown_days": 21,
    })
    return path


@pytest.fixture
def log_file(tmp_path):
    return tmp_path / "seo_level5_auto_apply_log.json"


@pytest.fixture
def gsc_file(tmp_path):
    return tmp_path / "gsc_collect.json"


# ═══════════════════════════════════════════════════════════════════════════════
# 1. EVALUATE_URL_REAPPLY_READINESS — decision tree complet
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvaluateUrlReapplyReadiness:

    def test_url_never_applied_is_allowed(self, log_file, cooldown_config_file):
        """URL care nu a fost niciodata aplicat → ALLOWED."""
        _write_json(log_file, [])
        result = evaluate_url_reapply_readiness(
            url="/pagina-noua",
            log_path=log_file,
            config_path=cooldown_config_file,
        )
        assert result["status"] == ReapplyReadiness.ALLOWED
        assert result["blocked_reason"] is None
        assert result["days_since_apply"] is None

    def test_blocked_before_7_days(self, log_file, cooldown_config_file):
        """Ziua 5 → BLOCKED: url_in_minimum_cooldown_window."""
        _write_json(log_file, [_log_entry("/test", days_ago=5)])
        result = evaluate_url_reapply_readiness(
            url="/test",
            log_path=log_file,
            config_path=cooldown_config_file,
        )
        assert result["status"] == ReapplyReadiness.BLOCKED
        assert result["blocked_reason"] == "url_in_minimum_cooldown_window"
        assert result["days_since_apply"] < 7

    def test_blocked_at_day_1(self, log_file, cooldown_config_file):
        """Ziua 1 (T+24h) → BLOCKED: minimum window."""
        _write_json(log_file, [_log_entry("/test", days_ago=1)])
        result = evaluate_url_reapply_readiness(
            url="/test",
            log_path=log_file,
            config_path=cooldown_config_file,
        )
        assert result["status"] == ReapplyReadiness.BLOCKED
        assert result["blocked_reason"] == "url_in_minimum_cooldown_window"

    def test_blocked_day8_insufficient_impressions(self, log_file, cooldown_config_file, gsc_file):
        """Ziua 8, 40 impresii (< 80) → BLOCKED: insufficient_impressions_before_reapply."""
        _write_json(log_file, [_log_entry("/test", days_ago=8)])
        _write_json(gsc_file, _gsc_data("/test", impressions=40))
        result = evaluate_url_reapply_readiness(
            url="/test",
            log_path=log_file,
            config_path=cooldown_config_file,
            gsc_data_path=gsc_file,
        )
        assert result["status"] == ReapplyReadiness.BLOCKED
        assert result["blocked_reason"] == "insufficient_impressions_before_reapply"
        assert result["impressions_found"] == 40

    def test_blocked_day8_no_gsc_data(self, log_file, cooldown_config_file):
        """Ziua 8, fara date GSC → BLOCKED: insufficient_impressions_before_reapply."""
        _write_json(log_file, [_log_entry("/test", days_ago=8)])
        result = evaluate_url_reapply_readiness(
            url="/test",
            log_path=log_file,
            config_path=cooldown_config_file,
            gsc_data_path=Path("/nonexistent/gsc.json"),
        )
        assert result["status"] == ReapplyReadiness.BLOCKED
        assert result["blocked_reason"] == "insufficient_impressions_before_reapply"
        assert result["impressions_found"] is None

    def test_allowed_day8_sufficient_impressions(self, log_file, cooldown_config_file, gsc_file):
        """Ziua 8, 120 impresii (>= 80) → ALLOWED."""
        _write_json(log_file, [_log_entry("/test", days_ago=8)])
        _write_json(gsc_file, _gsc_data("/test", impressions=120))
        result = evaluate_url_reapply_readiness(
            url="/test",
            log_path=log_file,
            config_path=cooldown_config_file,
            gsc_data_path=gsc_file,
        )
        assert result["status"] == ReapplyReadiness.ALLOWED
        assert result["blocked_reason"] is None
        assert result["impressions_found"] == 120

    def test_allowed_insufficient_data_after_day_14(self, log_file, cooldown_config_file):
        """Ziua 15 fara date GSC → ALLOWED_INSUFFICIENT_DATA (nu mai e blocat)."""
        _write_json(log_file, [_log_entry("/test", days_ago=15)])
        result = evaluate_url_reapply_readiness(
            url="/test",
            log_path=log_file,
            config_path=cooldown_config_file,
            gsc_data_path=Path("/nonexistent/gsc.json"),
        )
        assert result["status"] == ReapplyReadiness.ALLOWED_INSUFFICIENT_DATA
        assert result["blocked_reason"] is None
        assert result["days_since_apply"] >= 14

    def test_rollback_cooldown_21_days(self, log_file, cooldown_config_file):
        """Rollback recent (< 21 zile) → BLOCKED: url_in_rollback_cooldown."""
        _write_json(log_file, [
            _log_entry("/test", days_ago=5, approval_mode="auto_applied"),
            _log_entry("/test", days_ago=3, approval_mode="rolled_back"),
        ])
        result = evaluate_url_reapply_readiness(
            url="/test",
            log_path=log_file,
            config_path=cooldown_config_file,
        )
        assert result["status"] == ReapplyReadiness.BLOCKED
        assert result["blocked_reason"] == "url_in_rollback_cooldown"

    def test_rollback_older_than_21_days_does_not_block(self, log_file, cooldown_config_file):
        """Rollback vechi (> 21 zile) nu mai blocheaza, ziua 25 → ALLOWED_INSUFFICIENT_DATA."""
        _write_json(log_file, [
            _log_entry("/test", days_ago=25, approval_mode="auto_applied"),
            _log_entry("/test", days_ago=22, approval_mode="rolled_back"),
        ])
        result = evaluate_url_reapply_readiness(
            url="/test",
            log_path=log_file,
            config_path=cooldown_config_file,
            gsc_data_path=Path("/nonexistent/gsc.json"),
        )
        # 25 days since last apply >= max 14 → ALLOWED_INSUFFICIENT_DATA
        assert result["status"] == ReapplyReadiness.ALLOWED_INSUFFICIENT_DATA

    def test_most_recent_entry_used(self, log_file, cooldown_config_file):
        """Cu doua intrari pentru acelasi URL, se foloseste cea mai recenta."""
        _write_json(log_file, [
            _log_entry("/test", days_ago=20),  # veche, ar fi allowed
            _log_entry("/test", days_ago=3),   # recenta, ar fi blocked
        ])
        result = evaluate_url_reapply_readiness(
            url="/test",
            log_path=log_file,
            config_path=cooldown_config_file,
        )
        # Cea mai recenta e ziua 3 < min 7 → BLOCKED
        assert result["status"] == ReapplyReadiness.BLOCKED
        assert result["blocked_reason"] == "url_in_minimum_cooldown_window"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CHECK_URL_COOLDOWN — wrapper backwards-compat
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckUrlCooldownWrapper:

    def test_returns_empty_when_never_applied(self, log_file, cooldown_config_file):
        _write_json(log_file, [])
        result = check_url_cooldown("/test", log_path=log_file, config_path=cooldown_config_file)
        assert result == []

    def test_returns_blocker_in_min_window(self, log_file, cooldown_config_file):
        _write_json(log_file, [_log_entry("/test", days_ago=5)])
        result = check_url_cooldown("/test", log_path=log_file, config_path=cooldown_config_file)
        assert len(result) == 1
        assert result[0] == "url_in_minimum_cooldown_window"

    def test_returns_empty_after_max_window(self, log_file, cooldown_config_file):
        _write_json(log_file, [_log_entry("/test", days_ago=15)])
        result = check_url_cooldown("/test", log_path=log_file, config_path=cooldown_config_file)
        assert result == []

    def test_returns_rollback_blocker(self, log_file, cooldown_config_file):
        _write_json(log_file, [
            _log_entry("/test", days_ago=3, approval_mode="rolled_back"),
        ])
        result = check_url_cooldown("/test", log_path=log_file, config_path=cooldown_config_file)
        assert result == ["url_in_rollback_cooldown"]


# ═══════════════════════════════════════════════════════════════════════════════
# 3. LOAD_COOLDOWN_CONFIG — defaults si config custom
# ═══════════════════════════════════════════════════════════════════════════════

class TestLoadCooldownConfig:

    def test_loads_from_file(self, cooldown_config_file):
        cfg = load_cooldown_config(cooldown_config_file)
        assert cfg["min_reapply_days"] == 7
        assert cfg["min_impressions_for_reapply"] == 80
        assert cfg["max_reapply_days_without_data"] == 14
        assert cfg["rollback_cooldown_days"] == 21

    def test_falls_back_to_defaults_when_file_missing(self):
        cfg = load_cooldown_config(Path("/nonexistent/cooldown.json"))
        assert cfg["min_reapply_days"] == 7
        assert cfg["min_impressions_for_reapply"] == 80
        assert cfg["max_reapply_days_without_data"] == 14
        assert cfg["rollback_cooldown_days"] == 21

    def test_custom_config_overrides_defaults(self, tmp_path):
        path = tmp_path / "custom.json"
        _write_json(path, {"min_reapply_days": 10, "rollback_cooldown_days": 30})
        cfg = load_cooldown_config(path)
        assert cfg["min_reapply_days"] == 10
        assert cfg["rollback_cooldown_days"] == 30
        # outros au valorile default
        assert cfg["min_impressions_for_reapply"] == 80


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GENERATE_STATUS_REPORT — cooldown_config si rollback_cooldown_urls
# ═══════════════════════════════════════════════════════════════════════════════

class TestStatusReportCooldownFields:

    def _make_policy(self):
        return {
            "schema_version": "1.3",
            "auto_apply_config": {"enabled": False},
        }

    def test_status_includes_cooldown_config(self, tmp_path, log_file, cooldown_config_file):
        status = generate_status_report(
            policy=self._make_policy(),
            activation_source="disabled",
            log_path=log_file,
            status_path=tmp_path / "status.json",
            cooldown_config_path=cooldown_config_file,
        )
        assert "cooldown_config" in status
        assert status["cooldown_config"]["min_reapply_days"] == 7
        assert status["cooldown_config"]["rollback_cooldown_days"] == 21

    def test_status_includes_rollback_cooldown_urls(self, tmp_path, log_file, cooldown_config_file):
        _write_json(log_file, [
            _log_entry("/rolledback", days_ago=5, approval_mode="rolled_back"),
        ])
        status = generate_status_report(
            policy=self._make_policy(),
            activation_source="disabled",
            log_path=log_file,
            status_path=tmp_path / "status.json",
            cooldown_config_path=cooldown_config_file,
        )
        assert "rollback_cooldown_urls" in status
        assert "/rolledback" in status["rollback_cooldown_urls"]

    def test_status_cooldown_active_uses_min_days(self, tmp_path, log_file, cooldown_config_file):
        """cooldown_active_urls trebuie sa arate URL-uri aplicate in ultimele MIN_DAYS (7)."""
        _write_json(log_file, [
            _log_entry("/recent", days_ago=3),    # in cooldown
            _log_entry("/old", days_ago=10),       # nu mai e in min window
        ])
        status = generate_status_report(
            policy=self._make_policy(),
            activation_source="disabled",
            log_path=log_file,
            status_path=tmp_path / "status.json",
            cooldown_config_path=cooldown_config_file,
        )
        assert "/recent" in status["cooldown_active_urls"]
        assert "/old" not in status["cooldown_active_urls"]


# ═══════════════════════════════════════════════════════════════════════════════
# 5. INVARIANTE — guardrails neatinse
# ═══════════════════════════════════════════════════════════════════════════════

class TestInvariantsIntact:

    def _sandbox(self, tmp_path, enabled_override: bool = True):
        """Build full sandbox for run_controlled_auto_apply."""
        cfg_dir = tmp_path / "config" / "seo"
        rep_dir = tmp_path / "reports" / "superparty"
        pages_dir = tmp_path / "src" / "pages"

        policy_path = cfg_dir / "level5_action_policy.json"
        override_path = cfg_dir / "auto_apply_runtime_override.json"
        pillar_path = cfg_dir / "pillar_pages_registry.json"
        cooldown_cfg = cfg_dir / "auto_apply_cooldown_config.json"
        plan_path = rep_dir / "seo_level5_apply_plan.json"
        log_path = rep_dir / "seo_level5_auto_apply_log.json"

        for d in [cfg_dir, rep_dir]:
            d.mkdir(parents=True, exist_ok=True)

        policy = {
            "schema_version": "1.3",
            "approval_gate": "manual",
            "rollback_required": True,
            "feedback_loop_mode": "observability_only",
            "tier_restrictions": {"A": "read_only", "B": "restricted", "C": "low_risk_eligible"},
            "max_actions_per_run": 1,
            "action_activation": {
                "meta_description_update": {
                    "execution_mode": "single_apply_only",
                    "tier_allowlist": ["C"], "tier_denylist": ["A", "B"],
                    "money_pages": "forbidden", "pillar_pages": "forbidden",
                    "max_candidates_per_run": 1, "requires_manual_approval_before_apply": True,
                    "requires_ready_to_apply": True, "requires_approval_decision": "approved",
                    "write_files": True, "create_pull_request": False, "commit_changes": False,
                    "rollback_mode": "single_file_revert",
                }
            },
            "auto_apply_config": {
                "enabled": True,
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
        _write_json(policy_path, policy)
        _write_json(override_path, {"enabled": enabled_override})
        _write_json(pillar_path, {"schema_version": "1.0", "pillar_pages": ["/animatori-petreceri-copii"]})
        _write_json(cooldown_cfg, {
            "min_reapply_days": 7,
            "min_impressions_for_reapply": 80,
            "max_reapply_days_without_data": 14,
            "rollback_cooldown_days": 21,
        })

        return {
            "policy_path": policy_path,
            "override_path": override_path,
            "pillar_path": pillar_path,
            "cooldown_cfg": cooldown_cfg,
            "plan_path": plan_path,
            "log_path": log_path,
            "pages_dir": pages_dir,
            "rep_dir": rep_dir,
        }

    def _write_plan_and_page(self, tmp_path, pages_dir, plan_path, url="/tier-c-pagina"):
        slug = url.strip("/")
        page_dir = pages_dir / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.astro").write_text(
            '<Layout description="Descriere veche.">\n</Layout>\n', encoding="utf-8"
        )
        action = {
            "action_id": str(uuid.uuid4()),
            "plan_id": "test-plan",
            "action_type": "meta_description_update",
            "url": url,
            "tier": "C",
            "is_money_page": False,
            "is_pillar_page": False,
            "ready_to_apply": True,
            "proposal_source": "deterministic_fallback",
            "before": {"meta_description": "Descriere veche."},
            "proposal": {"meta_description": "Text nou optimizat. 120 caractere suficiente pentru snippet bun."},
        }
        _write_json(plan_path, {"plan": [action], "blocked": []})

    def test_cooldown_blocks_reapply_within_7_days(self, tmp_path, monkeypatch):
        """Engine nu aplica pe URL aplicat in ultimele 7 zile."""
        sb = self._sandbox(tmp_path)
        self._write_plan_and_page(tmp_path, sb["pages_dir"], sb["plan_path"])
        # Simulate URL already applied 3 days ago
        _write_json(sb["log_path"], [_log_entry("/tier-c-pagina", days_ago=3)])

        # Patch module paths
        monkeypatch.setattr(auto_module, "POLICY_PATH", sb["policy_path"])
        monkeypatch.setattr(auto_module, "OVERRIDE_PATH", sb["override_path"])
        monkeypatch.setattr(auto_module, "PILLAR_REGISTRY_PATH", sb["pillar_path"])
        monkeypatch.setattr(auto_module, "APPLY_PLAN_PATH", sb["plan_path"])
        monkeypatch.setattr(auto_module, "AUTO_APPLY_LOG_PATH", sb["log_path"])
        monkeypatch.setattr(auto_module, "COOLDOWN_CONFIG_PATH", sb["cooldown_cfg"])
        monkeypatch.setattr(auto_module, "PAGES_DIR", sb["pages_dir"])
        monkeypatch.setattr(auto_module, "ROOT_DIR", tmp_path)
        monkeypatch.setattr(auto_module, "ROLLBACK_PAYLOAD_PATH", sb["rep_dir"] / "rollback.json")
        monkeypatch.setattr(auto_module, "EXECUTION_REPORT_PATH", sb["rep_dir"] / "exec.json")
        monkeypatch.setattr(auto_module, "STATUS_REPORT_PATH", sb["rep_dir"] / "status.json")

        result = run_controlled_auto_apply(
            pages_dir=sb["pages_dir"],
            policy_path=sb["policy_path"],
            apply_plan_path=sb["plan_path"],
            override_path=sb["override_path"],
            pillar_registry_path=sb["pillar_path"],
            log_path=sb["log_path"],
        )
        # Should be blocked, not True
        assert result is not True

    def test_pillar_page_still_blocked(self, tmp_path, monkeypatch):
        """Pillar page ramane blocata indiferent de cooldown."""
        sb = self._sandbox(tmp_path)
        # Use pillar URL in plan
        self._write_plan_and_page(tmp_path, sb["pages_dir"], sb["plan_path"],
                                  url="/animatori-petreceri-copii")
        page_dir = sb["pages_dir"] / "animatori-petreceri-copii"
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.astro").write_text('<Layout description="Vechi.">\n</Layout>\n')
        _write_json(sb["log_path"], [])

        monkeypatch.setattr(auto_module, "POLICY_PATH", sb["policy_path"])
        monkeypatch.setattr(auto_module, "OVERRIDE_PATH", sb["override_path"])
        monkeypatch.setattr(auto_module, "PILLAR_REGISTRY_PATH", sb["pillar_path"])
        monkeypatch.setattr(auto_module, "APPLY_PLAN_PATH", sb["plan_path"])
        monkeypatch.setattr(auto_module, "AUTO_APPLY_LOG_PATH", sb["log_path"])
        monkeypatch.setattr(auto_module, "COOLDOWN_CONFIG_PATH", sb["cooldown_cfg"])
        monkeypatch.setattr(auto_module, "PAGES_DIR", sb["pages_dir"])
        monkeypatch.setattr(auto_module, "ROOT_DIR", tmp_path)
        monkeypatch.setattr(auto_module, "ROLLBACK_PAYLOAD_PATH", sb["rep_dir"] / "rollback.json")
        monkeypatch.setattr(auto_module, "EXECUTION_REPORT_PATH", sb["rep_dir"] / "exec.json")
        monkeypatch.setattr(auto_module, "STATUS_REPORT_PATH", sb["rep_dir"] / "status.json")

        result = run_controlled_auto_apply(
            pages_dir=sb["pages_dir"],
            policy_path=sb["policy_path"],
            apply_plan_path=sb["plan_path"],
            override_path=sb["override_path"],
            pillar_registry_path=sb["pillar_path"],
            log_path=sb["log_path"],
        )
        assert result is not True

    def test_override_disabled_blocks_all(self, tmp_path, monkeypatch):
        """Override disabled → nimic nu se aplica."""
        sb = self._sandbox(tmp_path, enabled_override=False)
        self._write_plan_and_page(tmp_path, sb["pages_dir"], sb["plan_path"])
        _write_json(sb["log_path"], [])

        monkeypatch.setattr(auto_module, "POLICY_PATH", sb["policy_path"])
        monkeypatch.setattr(auto_module, "OVERRIDE_PATH", sb["override_path"])
        monkeypatch.setattr(auto_module, "PILLAR_REGISTRY_PATH", sb["pillar_path"])
        monkeypatch.setattr(auto_module, "APPLY_PLAN_PATH", sb["plan_path"])
        monkeypatch.setattr(auto_module, "AUTO_APPLY_LOG_PATH", sb["log_path"])
        monkeypatch.setattr(auto_module, "COOLDOWN_CONFIG_PATH", sb["cooldown_cfg"])
        monkeypatch.setattr(auto_module, "PAGES_DIR", sb["pages_dir"])
        monkeypatch.setattr(auto_module, "ROOT_DIR", tmp_path)
        monkeypatch.setattr(auto_module, "ROLLBACK_PAYLOAD_PATH", sb["rep_dir"] / "rollback.json")
        monkeypatch.setattr(auto_module, "EXECUTION_REPORT_PATH", sb["rep_dir"] / "exec.json")
        monkeypatch.setattr(auto_module, "STATUS_REPORT_PATH", sb["rep_dir"] / "status.json")

        result = run_controlled_auto_apply(
            pages_dir=sb["pages_dir"],
            policy_path=sb["policy_path"],
            apply_plan_path=sb["plan_path"],
            override_path=sb["override_path"],
            pillar_registry_path=sb["pillar_path"],
            log_path=sb["log_path"],
        )
        assert result is None  # disabled → None

    def test_max_1_candidate_per_run(self, tmp_path, monkeypatch):
        """Chiar cu 3 candidati Tier C, se aplica max 1."""
        sb = self._sandbox(tmp_path)
        actions = []
        for i in range(3):
            slug = f"pagina-tier-c-{i}"
            page_dir = sb["pages_dir"] / slug
            page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "index.astro").write_text(
                f'<Layout description="Descriere veche {i}.">\n</Layout>\n', encoding="utf-8"
            )
            actions.append({
                "action_id": str(uuid.uuid4()),
                "plan_id": "test",
                "action_type": "meta_description_update",
                "url": f"/{slug}",
                "tier": "C",
                "is_money_page": False,
                "is_pillar_page": False,
                "ready_to_apply": True,
                "proposal_source": "deterministic_fallback",
                "before": {"meta_description": f"Descriere veche {i}."},
                "proposal": {"meta_description": f"Text nou optimizat {i}. Suficient de lung pentru snippet."},
            })
        _write_json(sb["plan_path"], {"plan": actions, "blocked": []})
        _write_json(sb["log_path"], [])

        monkeypatch.setattr(auto_module, "POLICY_PATH", sb["policy_path"])
        monkeypatch.setattr(auto_module, "OVERRIDE_PATH", sb["override_path"])
        monkeypatch.setattr(auto_module, "PILLAR_REGISTRY_PATH", sb["pillar_path"])
        monkeypatch.setattr(auto_module, "APPLY_PLAN_PATH", sb["plan_path"])
        monkeypatch.setattr(auto_module, "AUTO_APPLY_LOG_PATH", sb["log_path"])
        monkeypatch.setattr(auto_module, "COOLDOWN_CONFIG_PATH", sb["cooldown_cfg"])
        monkeypatch.setattr(auto_module, "PAGES_DIR", sb["pages_dir"])
        monkeypatch.setattr(auto_module, "ROOT_DIR", tmp_path)
        monkeypatch.setattr(auto_module, "ROLLBACK_PAYLOAD_PATH", sb["rep_dir"] / "rollback.json")
        monkeypatch.setattr(auto_module, "EXECUTION_REPORT_PATH", sb["rep_dir"] / "exec.json")
        monkeypatch.setattr(auto_module, "STATUS_REPORT_PATH", sb["rep_dir"] / "status.json")

        result = run_controlled_auto_apply(
            pages_dir=sb["pages_dir"],
            policy_path=sb["policy_path"],
            apply_plan_path=sb["plan_path"],
            override_path=sb["override_path"],
            pillar_registry_path=sb["pillar_path"],
            log_path=sb["log_path"],
        )
        # max 1 applied
        log_data = json.loads(sb["log_path"].read_text(encoding="utf-8"))
        assert len(log_data) <= 1
