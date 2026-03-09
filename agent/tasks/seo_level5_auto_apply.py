"""
SEO Level 5 — Controlled Single Auto-Apply Engine (PR #86)

Executa auto-apply pentru exact 1 actiune meta_description_update pe Tier C,
NUMAI daca feature flag auto_apply_config.enabled=true in policy.

Cand feature flag este OFF (default), aceasta functie returneaza None si
comportamentul este identic cu schema_version 1.2 (manual approval required).

CONSTRAINTS — acest modul NICIODATA:
  - Nu aplica actiuni pe Tier A sau Tier B
  - Nu aplica actiuni pe money pages sau pillar pages
  - Nu aplica alt action_type decat meta_description_update
  - Nu creeaza commits sau pull requests
  - Nu aplica mai mult de 1 candidat per run
  - Nu introduce auto-learning sau feedback loop autonom
  - Nu ocoleste rollback_required

OUTPUTS:
  reports/superparty/seo_level5_auto_apply_log.json  (append-only audit trail)
  reports/superparty/seo_level5_apply_execution.json (standard execution report)
  reports/superparty/seo_level5_rollback_payload.json

Schema audit trail per intrare:
{
  "auto_apply_id": str,         # uuid unic
  "action_id": str,
  "url": str,
  "approved_by": "system_auto_apply",
  "approval_mode": "auto_applied",
  "proposal_source": "llm" | "deterministic_fallback" | "unknown",
  "auto_apply_reason": [str],   # conditii care au trecut
  "before": {"meta_description": str},
  "after": {"meta_description": str},
  "rollback_reference": str,    # path relativ la rollback payload
  "applied_at": str,            # ISO8601 UTC
  "policy_version": str
}
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

ROOT_DIR    = Path(__file__).parent.parent.parent
CONFIG_DIR  = ROOT_DIR / "config" / "seo"
REPORTS_DIR = ROOT_DIR / "reports" / "superparty"
PAGES_DIR   = ROOT_DIR / "src" / "pages"

POLICY_PATH              = CONFIG_DIR  / "level5_action_policy.json"
DRY_RUN_REPORT_PATH      = REPORTS_DIR / "seo_level5_dry_run_actions.json"
APPLY_PLAN_PATH          = REPORTS_DIR / "seo_level5_apply_plan.json"
AUTO_APPLY_LOG_PATH      = REPORTS_DIR / "seo_level5_auto_apply_log.json"
EXECUTION_REPORT_PATH    = REPORTS_DIR / "seo_level5_apply_execution.json"
ROLLBACK_PAYLOAD_PATH    = REPORTS_DIR / "seo_level5_rollback_payload.json"

ACTION_TYPE = "meta_description_update"
APPROVED_BY = "system_auto_apply"

# Reuse safe edit patterns from apply module (same logic, no duplication of logic)
_RE_FRONTMATTER_DESC = re.compile(
    r"""^( *description\s*=\s*)(['"])(.*?)\2(\s*;?\s*)$""",
    re.MULTILINE,
)
_RE_META_TAG_DESC = re.compile(
    r"""(<meta\s+name=["']description["']\s+content=["'])([^"']{0,500})(["'])""",
    re.IGNORECASE,
)
_RE_LAYOUT_PROP_DESC = re.compile(
    r"""([ \t]*description=)(['"])([^'"]{0,500})\2""",
    re.MULTILINE,
)


class AutoApplyError(RuntimeError):
    """Raised when auto-apply fails a precondition."""


class AutoApplyDisabled(RuntimeError):
    """Raised when feature flag is OFF."""


# ─── Loaders ──────────────────────────────────────────────────────────────────

def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_policy() -> dict:
    data = _load_json(POLICY_PATH)
    if not data:
        raise AutoApplyError(f"Policy missing: {POLICY_PATH}")
    return data


# ─── Feature flag ────────────────────────────────────────────────────────────

def check_auto_apply_enabled(policy: dict) -> bool:
    """
    Returns True ONLY if auto_apply_config.enabled is explicitly true.
    Any other value (including missing) returns False.
    """
    cfg = policy.get("auto_apply_config", {})
    return cfg.get("enabled", False) is True


# ─── Eligibility ──────────────────────────────────────────────────────────────

def validate_auto_apply_eligibility(action: dict, policy: dict) -> list:
    """
    Returns list of blockers. Empty list = eligible.
    Checks: flag, action_type, tier, money_page, pillar_page.
    """
    blockers = []
    cfg = policy.get("auto_apply_config", {})

    if not check_auto_apply_enabled(policy):
        blockers.append("auto_apply_disabled")
        return blockers  # short-circuit

    allowlist_actions = cfg.get("auto_apply_actions_allowlist", [])
    tier_allowlist    = cfg.get("auto_apply_tier_allowlist", [])
    tier_denylist     = cfg.get("auto_apply_tier_denylist", [])

    if action.get("action_type") not in allowlist_actions:
        blockers.append("action_type_not_in_allowlist")

    tier = action.get("tier", "")
    if tier in tier_denylist:
        blockers.append(f"tier_{tier.lower()}_in_denylist")
    if tier not in tier_allowlist:
        blockers.append("tier_not_in_allowlist")

    if action.get("is_money_page"):
        blockers.append("money_page_forbidden")

    if action.get("is_pillar_page"):
        blockers.append("pillar_page_forbidden")

    return blockers


def validate_candidate_count(plan: dict, policy: dict) -> list:
    """Returns blockers if candidate count != 1."""
    blockers = []
    cfg = policy.get("auto_apply_config", {})
    max_c = cfg.get("auto_apply_max_candidates", 1)
    candidates = [a for a in plan.get("plan", []) if a.get("ready_to_apply") is True]
    if len(candidates) == 0:
        blockers.append("no_ready_candidates")
    elif len(candidates) > max_c:
        blockers.append(f"too_many_candidates_{len(candidates)}_max_{max_c}")
    return blockers


# ─── Proposal validation ──────────────────────────────────────────────────────

def validate_proposal(proposal: str) -> list:
    """Returns blockers for bad proposal text."""
    blockers = []
    if not proposal or len(proposal) < 50:
        blockers.append("proposal_too_short")
    if len(proposal) > 200:
        blockers.append("proposal_too_long")
    if '"' in proposal:
        blockers.append("proposal_contains_unsafe_double_quote")
    if "'" in proposal:
        blockers.append("proposal_contains_unsafe_single_quote")
    if re.search(r"[<>]", proposal):
        blockers.append("proposal_contains_html")
    if "\n" in proposal or "\r" in proposal:
        blockers.append("proposal_contains_newline")
    return blockers


# ─── File state validation ────────────────────────────────────────────────────

def resolve_target_file(action: dict, pages_dir: Path) -> Path:
    """Find the .astro file for the action URL."""
    url = action.get("url", "").lstrip("/")
    candidates = [
        pages_dir / f"{url}.astro",
        pages_dir / url / "index.astro",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise AutoApplyError(f"target_file_not_found: {url}")


def extract_current_meta_description(file_path: Path) -> Optional[str]:
    """Extract current meta description from file."""
    content = file_path.read_text(encoding="utf-8")
    for pattern in [_RE_FRONTMATTER_DESC, _RE_META_TAG_DESC, _RE_LAYOUT_PROP_DESC]:
        m = pattern.search(content)
        if m:
            return m.group(3).strip() if len(m.groups()) >= 3 else m.group(2).strip()
    return None


def validate_file_state(action: dict, pages_dir: Path) -> list:
    """
    Checks that the current file content matches the plan's before-state.
    Returns list of blockers.
    """
    blockers = []
    try:
        target = resolve_target_file(action, pages_dir)
    except AutoApplyError as e:
        blockers.append(str(e))
        return blockers

    current = extract_current_meta_description(target)
    expected_before = (action.get("before") or {}).get("meta_description", "")

    if current is None:
        blockers.append("cannot_extract_current_description")
    elif current.strip() != expected_before.strip():
        blockers.append(f"file_drift_detected:current={current[:60]!r}")

    return blockers


# ─── Apply ────────────────────────────────────────────────────────────────────

def apply_description_to_file(file_path: Path, new_desc: str) -> dict:
    """
    Write new meta description to file using safe edit patterns.
    Returns strategy info dict.
    """
    content = file_path.read_text(encoding="utf-8")

    # Guard: no unsafe quotes against the delimiter
    # (reuse same logic as seo_level5_meta_description_apply.py)
    def _safe_write(pattern, new_text, group_idx_text, content):
        m = pattern.search(content)
        if m:
            delimiter = m.group(group_idx_text - 1) if group_idx_text > 1 else None
            if delimiter and delimiter in new_text:
                raise AutoApplyError("unsafe_proposal_contains_quote")
            new_content = pattern.sub(
                lambda _m: _m.group(1) + _m.group(2) + new_text + _m.group(len(_m.groups())),
                content,
                count=1
            )
            return new_content
        return None

    # Try frontmatter prop
    m = _RE_FRONTMATTER_DESC.search(content)
    if m:
        delim = m.group(2)
        if delim in new_desc:
            raise AutoApplyError("unsafe_proposal_contains_quote")
        new_content = _RE_FRONTMATTER_DESC.sub(
            lambda _m: _m.group(1) + _m.group(2) + new_desc + _m.group(2) + _m.group(4),
            content, count=1,
        )
        file_path.write_text(new_content, encoding="utf-8")
        return {"strategy": "frontmatter_prop"}

    # Try Layout prop
    m = _RE_LAYOUT_PROP_DESC.search(content)
    if m:
        delim = m.group(2)
        if delim in new_desc:
            raise AutoApplyError("unsafe_proposal_contains_quote")
        new_content = _RE_LAYOUT_PROP_DESC.sub(
            lambda _m: _m.group(1) + _m.group(2) + new_desc + _m.group(2),
            content, count=1,
        )
        file_path.write_text(new_content, encoding="utf-8")
        return {"strategy": "layout_prop"}

    # Try meta tag
    m = _RE_META_TAG_DESC.search(content)
    if m:
        delim = m.group(3)
        if delim in new_desc:
            raise AutoApplyError("unsafe_proposal_contains_quote")
        new_content = _RE_META_TAG_DESC.sub(
            lambda _m: _m.group(1) + new_desc + _m.group(3),
            content, count=1,
        )
        file_path.write_text(new_content, encoding="utf-8")
        return {"strategy": "meta_tag"}

    raise AutoApplyError("unsupported_file_structure")


# ─── Audit trail ──────────────────────────────────────────────────────────────

def build_auto_apply_record(
    action: dict,
    policy: dict,
    before_desc: str,
    after_desc: str,
    strategy: str,
    auto_apply_reason: list,
) -> dict:
    """Build the audit trail record for one auto-apply."""
    return {
        "auto_apply_id": str(uuid.uuid4()),
        "action_id": action.get("action_id", ""),
        "url": action.get("url", ""),
        "approved_by": APPROVED_BY,
        "approval_mode": "auto_applied",
        "proposal_source": action.get("proposal_source", "unknown"),
        "auto_apply_reason": auto_apply_reason,
        "strategy": strategy,
        "before": {"meta_description": before_desc},
        "after": {"meta_description": after_desc},
        "rollback_reference": str(ROLLBACK_PAYLOAD_PATH.name),
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "policy_version": policy.get("schema_version", "unknown"),
    }


def append_auto_apply_log(record: dict, log_path: Path = AUTO_APPLY_LOG_PATH) -> None:
    """Append auto-apply record to append-only log."""
    existing = _load_json(log_path) or []
    if not isinstance(existing, list):
        existing = []
    existing.append(record)
    _write_json(log_path, existing)


def build_rollback_payload(
    file_path: Path, before_desc: str, after_desc: str, action_id: str
) -> dict:
    return {
        "action_id": action_id,
        "rollback_mode": "single_file_revert",
        "file_path": str(file_path),
        "before": {"meta_description": before_desc},
        "after": {"meta_description": after_desc},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


# ─── Main entry point ─────────────────────────────────────────────────────────

def run_controlled_auto_apply(
    pages_dir: Path = PAGES_DIR,
    policy_path: Path = POLICY_PATH,
    apply_plan_path: Path = APPLY_PLAN_PATH,
) -> Optional[bool]:
    """
    Entry point for controlled single auto-apply.

    Returns:
      None   — feature flag is OFF; no action taken
      True   — apply successful
      False  — blocked by a guardrail; no file modified
    """
    policy = _load_json(policy_path)
    if not policy:
        log.error("Policy not found: %s", policy_path)
        return False

    # ── Feature flag check ────────────────────────────────────────────────────
    if not check_auto_apply_enabled(policy):
        log.info("auto_apply_config.enabled=false — skipping auto-apply (flag OFF)")
        return None  # Sentinel: flag OFF, no action

    log.info("auto_apply_config.enabled=true — checking eligibility")

    # ── Load plan ─────────────────────────────────────────────────────────────
    plan = _load_json(apply_plan_path)
    if not plan:
        log.warning("Apply plan not found: %s", apply_plan_path)
        return False

    # ── Candidate count ───────────────────────────────────────────────────────
    count_blockers = validate_candidate_count(plan, policy)
    if count_blockers:
        log.warning("Auto-apply blocked (candidate count): %s", count_blockers)
        return False

    candidates = [a for a in plan.get("plan", []) if a.get("ready_to_apply") is True]
    action = candidates[0]  # exactly 1 at this point

    # ── Eligibility ───────────────────────────────────────────────────────────
    eligibility_blockers = validate_auto_apply_eligibility(action, policy)
    if eligibility_blockers:
        log.warning("Auto-apply blocked (eligibility): %s", eligibility_blockers)
        return False

    # ── Proposal validity ─────────────────────────────────────────────────────
    proposal_desc = (action.get("proposal") or {}).get("meta_description", "")
    proposal_blockers = validate_proposal(proposal_desc)
    if proposal_blockers:
        log.warning("Auto-apply blocked (proposal): %s", proposal_blockers)
        return False

    # ── File state (drift check) ──────────────────────────────────────────────
    file_blockers = validate_file_state(action, pages_dir)
    if file_blockers:
        log.warning("Auto-apply blocked (file drift): %s", file_blockers)
        return False

    # ── All guards passed — execute ───────────────────────────────────────────
    before_desc = (action.get("before") or {}).get("meta_description", "")
    auto_apply_reason = [
        "tier_c_eligible",
        "valid_proposal",
        "file_match_ok",
        "single_candidate_only",
        "not_money_page",
        "not_pillar_page",
    ]

    try:
        target_file = resolve_target_file(action, pages_dir)
        strategy_info = apply_description_to_file(target_file, proposal_desc)
        strategy = strategy_info.get("strategy", "unknown")
    except AutoApplyError as e:
        log.error("Auto-apply execution failed: %s", e)
        return False

    # ── Rollback payload ──────────────────────────────────────────────────────
    rollback = build_rollback_payload(target_file, before_desc, proposal_desc, action.get("action_id", ""))
    import agent.tasks.seo_level5_auto_apply as _self_mod
    _write_json(_self_mod.ROLLBACK_PAYLOAD_PATH, rollback)

    # ── Audit trail ───────────────────────────────────────────────────────────
    record = build_auto_apply_record(
        action=action,
        policy=policy,
        before_desc=before_desc,
        after_desc=proposal_desc,
        strategy=strategy,
        auto_apply_reason=auto_apply_reason,
    )
    append_auto_apply_log(record, log_path=_self_mod.AUTO_APPLY_LOG_PATH)

    # ── Execution report ──────────────────────────────────────────────────────
    execution_report = {
        "metadata": {
            "schema_version": policy.get("schema_version", "1.3"),
            "approval_mode": "auto_applied",
            "approved_by": APPROVED_BY,
            "applied": 1,
            "create_pull_request": False,
            "commit_changes": False,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "applied_actions": [
            {
                "action_id": action.get("action_id"),
                "url": action.get("url"),
                "tier": action.get("tier"),
                "approval_mode": "auto_applied",
                "approved_by": APPROVED_BY,
                "proposal_source": action.get("proposal_source", "unknown"),
                "strategy": strategy,
                "after_value": proposal_desc,
                "rollback_ready": True,
                "auto_apply_log_id": record["auto_apply_id"],
            }
        ],
    }
    _write_json(_self_mod.EXECUTION_REPORT_PATH, execution_report)

    log.info(
        "Auto-apply SUCCESS: url=%s strategy=%s auto_apply_id=%s",
        action.get("url"), strategy, record["auto_apply_id"],
    )
    return True


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    result = run_controlled_auto_apply()
    if result is None:
        print("AUTO_APPLY: skipped (feature flag OFF)")
        sys.exit(0)
    elif result is True:
        print("AUTO_APPLY: success")
        sys.exit(0)
    else:
        print("AUTO_APPLY: blocked by guardrail")
        sys.exit(1)
