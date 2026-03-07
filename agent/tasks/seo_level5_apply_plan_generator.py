"""
SEO Level 5 — Apply Plan Generator (PR #57)

Consumes ONLY approved actions from seo_level5_approval_log.json and produces
a structured apply_plan.json with preflight safety checks.

This module is a PLANNING step — it does NOT:
  - Edit any page source file
  - Create commits
  - Create pull requests
  - Call any apply engine
  - Modify operator decisions

applied = 0 is an invariant throughout this entire module.

OUTPUT: reports/superparty/seo_level5_apply_plan.json

Schema:
{
  "metadata": {
    "schema_version": "1.0",
    "generated_at": str,
    "mode": "apply_plan_only",
    "policy_version": str,
    "total_approved": int,
    "total_eligible": int,
    "total_blocked": int,
    "applied": 0          <- invariant: this module never applies
  },
  "preflight_summary": {
    "policy_valid": bool,
    "all_checks_passed": bool,
    "blocking_issues": list[str]
  },
  "plan": [               <- actions that passed ALL preflight checks
    {
      "plan_id":          str,
      "action_id":        str,
      "action_type":      str,
      "url":              str,
      "tier":             str,
      "is_money_page":    bool,
      "preflight":        { check_name: bool, ... },
      "ready_to_apply":   bool,
      "before":           dict,
      "proposal":         dict,
      "approval_record":  dict   <- snapshot of approval log entry
    }
  ],
  "blocked": [            <- approved actions that FAILED a preflight check
    { ...same structure..., "blocking_reason": str }
  ]
}
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT_DIR / "config" / "seo"
REPORTS_DIR = ROOT_DIR / "reports" / "superparty"

POLICY_PATH = CONFIG_DIR / "level5_action_policy.json"
DRY_RUN_REPORT_PATH = REPORTS_DIR / "seo_level5_dry_run_actions.json"
APPROVAL_LOG_PATH = REPORTS_DIR / "seo_level5_approval_log.json"
APPLY_PLAN_PATH = REPORTS_DIR / "seo_level5_apply_plan.json"


class PlanGenerationError(RuntimeError):
    """Raised when apply plan generation fails a pre-condition."""


# ─── Readers ──────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> Optional[dict | list]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_policy() -> dict:
    policy = _load_json(POLICY_PATH)
    if not policy or not isinstance(policy, dict):
        raise PlanGenerationError(f"Policy file missing or invalid: {POLICY_PATH}")
    return policy


def load_approval_log() -> list[dict]:
    data = _load_json(APPROVAL_LOG_PATH)
    if data is None:
        return []
    if not isinstance(data, list):
        raise PlanGenerationError(f"Approval log is not a list: {APPROVAL_LOG_PATH}")
    return data


def load_dry_run_report() -> dict:
    data = _load_json(DRY_RUN_REPORT_PATH)
    if not data or not isinstance(data, dict):
        raise PlanGenerationError(
            f"Dry-run report missing or invalid: {DRY_RUN_REPORT_PATH}"
        )
    return data


def get_approved_entries(approval_log: list[dict]) -> list[dict]:
    """Return only the approved entries from the approval log."""
    return [e for e in approval_log if e.get("decision") == "approved"]


def get_action_from_report(report: dict, action_id: str) -> Optional[dict]:
    for action in report.get("actions", []):
        if action.get("action_id") == action_id:
            return action
    return None


# ─── Policy validation ────────────────────────────────────────────────────────

def validate_policy_for_apply_plan(policy: dict) -> list[str]:
    """
    Re-validate policy invariants before generating the apply plan.
    Returns a list of blocking issues (empty = policy is valid).
    """
    issues: list[str] = []

    mode = policy.get("mode")
    if mode not in ("controlled_dry_run_only", "apply_plan_only"):
        issues.append(
            f"policy.mode='{mode}' — expected 'controlled_dry_run_only' or 'apply_plan_only'"
        )

    if policy.get("dry_run_required") is not True:
        issues.append("policy.dry_run_required must be True")

    if policy.get("approval_gate") != "manual":
        issues.append("policy.approval_gate must be 'manual'")

    tier_restrictions = policy.get("tier_restrictions", {})
    if tier_restrictions.get("A") != "read_only":
        issues.append("policy: Tier A must remain 'read_only'")

    allowed = policy.get("allowed_actions", [])
    if not allowed:
        issues.append("policy.allowed_actions is empty — no actions are permitted")

    activation = policy.get("action_activation", {})
    for action_type in allowed:
        act = activation.get(action_type, {})
        if act.get("write_files") is not False:
            issues.append(f"action_activation.{action_type}.write_files must be False")
        if act.get("create_pull_request") is not False:
            issues.append(f"action_activation.{action_type}.create_pull_request must be False")
        if act.get("commit_changes") is not False:
            issues.append(f"action_activation.{action_type}.commit_changes must be False")

    return issues


# ─── Preflight checks per action ─────────────────────────────────────────────

def _preflight_checks(action: dict, approval_entry: dict, policy: dict) -> dict[str, bool]:
    """
    Run per-action preflight safety checks.
    Returns a dict of check_name → passed (True/False).
    All checks must pass for the action to appear in plan[].
    """
    allowed_actions: list = policy.get("allowed_actions", [])
    activation: dict = (policy.get("action_activation") or {}).get(
        action.get("action_type", ""), {}
    )
    tier_allowlist: list = activation.get("tier_allowlist", [])
    tier_denylist: list = activation.get("tier_denylist", [])

    tier = action.get("tier", "")
    is_money = action.get("is_money_page", True)  # default True = safer

    return {
        # Decision integrity
        "decision_is_approved": approval_entry.get("decision") == "approved",
        "decided_by_present": bool(approval_entry.get("decided_by", "").strip()),
        # Action type permitted by policy
        "action_type_allowed": action.get("action_type") in allowed_actions,
        # Tier safety
        "tier_not_in_denylist": tier not in tier_denylist,
        "tier_in_allowlist": tier in tier_allowlist if tier_allowlist else True,
        "tier_a_not_permitted": tier != "A",
        # Money / pillar guard
        "not_money_page": not is_money,
        # Action-level write guards
        "write_files_false": activation.get("write_files") is False,
        "create_pr_false": activation.get("create_pull_request") is False,
        "commit_changes_false": activation.get("commit_changes") is False,
        # Proposal present
        "proposal_not_empty": bool(
            (action.get("proposal") or {}).get("meta_description", "").strip()
        ),
    }


def _checks_all_passed(checks: dict[str, bool]) -> bool:
    return all(checks.values())


def _first_failed_check(checks: dict[str, bool]) -> Optional[str]:
    for check_name, passed in checks.items():
        if not passed:
            return check_name
    return None


# ─── Plan builder ─────────────────────────────────────────────────────────────

def _build_plan_entry(
    action: dict,
    approval_entry: dict,
    checks: dict[str, bool],
    ready: bool,
    blocking_reason: Optional[str] = None,
) -> dict:
    entry = {
        "plan_id": str(uuid.uuid4()),
        "action_id": action.get("action_id", ""),
        "action_type": action.get("action_type", ""),
        "url": action.get("url", ""),
        "tier": action.get("tier", ""),
        "is_money_page": action.get("is_money_page", False),
        "preflight": checks,
        "ready_to_apply": ready,
        "before": action.get("before", {}),
        "proposal": action.get("proposal", {}),
        "approval_record": {
            "decision_id": approval_entry.get("decision_id"),
            "decision": approval_entry.get("decision"),
            "decided_by": approval_entry.get("decided_by"),
            "decided_at": approval_entry.get("decided_at"),
            "notes": approval_entry.get("notes"),
        },
    }
    if blocking_reason is not None:
        entry["blocking_reason"] = blocking_reason
    return entry


# ─── Main generator ───────────────────────────────────────────────────────────

def generate_apply_plan() -> dict:
    """
    Generate the apply plan from approved entries in the approval log.
    This function reads-only from:
      - level5_action_policy.json
      - seo_level5_approval_log.json
      - seo_level5_dry_run_actions.json
    And writes ONLY to seo_level5_apply_plan.json.

    applied = 0 is an immutable invariant — this function never applies changes.
    """
    policy = load_policy()
    approval_log = load_approval_log()
    dry_run_report = load_dry_run_report()

    # Policy-level validation
    policy_issues = validate_policy_for_apply_plan(policy)
    policy_valid = len(policy_issues) == 0

    approved_entries = get_approved_entries(approval_log)
    plan_entries: list[dict] = []
    blocked_entries: list[dict] = []

    for approval_entry in approved_entries:
        action_id = approval_entry.get("action_id", "")
        action = get_action_from_report(dry_run_report, action_id)

        if action is None:
            # Action approved but no longer in dry-run report — block it
            blocked_entries.append({
                "plan_id": str(uuid.uuid4()),
                "action_id": action_id,
                "action_type": approval_entry.get("action_type", ""),
                "url": approval_entry.get("url", ""),
                "tier": None,
                "is_money_page": None,
                "preflight": {},
                "ready_to_apply": False,
                "before": {},
                "proposal": {},
                "approval_record": {
                    "decision_id": approval_entry.get("decision_id"),
                    "decision": approval_entry.get("decision"),
                    "decided_by": approval_entry.get("decided_by"),
                    "decided_at": approval_entry.get("decided_at"),
                    "notes": approval_entry.get("notes"),
                },
                "blocking_reason": "action_id_not_found_in_dry_run_report",
            })
            continue

        checks = _preflight_checks(action, approval_entry, policy)
        all_passed = _checks_all_passed(checks)

        if all_passed:
            plan_entries.append(
                _build_plan_entry(action, approval_entry, checks, ready=True)
            )
        else:
            reason = _first_failed_check(checks) or "unknown"
            blocked_entries.append(
                _build_plan_entry(
                    action, approval_entry, checks, ready=False,
                    blocking_reason=reason
                )
            )

    all_checks_passed = (
        policy_valid
        and len(blocked_entries) == 0
        and len(plan_entries) > 0
    )

    return {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": "apply_plan_only",
            "policy_version": policy.get("schema_version", ""),
            "total_approved": len(approved_entries),
            "total_eligible": len(plan_entries),
            "total_blocked": len(blocked_entries),
            "applied": 0,  # invariant: this module never applies
        },
        "preflight_summary": {
            "policy_valid": policy_valid,
            "all_checks_passed": all_checks_passed,
            "blocking_issues": policy_issues,
        },
        "plan": plan_entries,
        "blocked": blocked_entries,
    }


def save_apply_plan(plan: dict) -> None:
    APPLY_PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(APPLY_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    log.info("Apply plan written to %s", APPLY_PLAN_PATH)


def run_apply_plan_generator() -> bool:
    try:
        plan = generate_apply_plan()
        save_apply_plan(plan)
        meta = plan["metadata"]
        summary = plan["preflight_summary"]
        print(
            f"Apply plan generated: {meta['total_eligible']} eligible, "
            f"{meta['total_blocked']} blocked, {meta['applied']} applied. "
            f"All checks passed: {summary['all_checks_passed']}"
        )
        return True
    except PlanGenerationError as e:
        log.error("Plan generation failed: %s", e)
        print(f"Apply plan blocked: {e}")
        return False
    except Exception as e:
        log.exception("Unexpected apply plan failure")
        print(f"Apply plan failed: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_apply_plan_generator()
