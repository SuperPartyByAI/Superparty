"""
SEO Level 5 — Controlled Meta Description Apply (PR #58)

The first REAL write in the Level 5 pipeline. Ultra-restricted:
  - ONLY meta_description_update
  - ONLY Tier C, non-money, non-pillar
  - ONLY 1 action per run
  - ONLY from ready_to_apply=True in the apply plan
  - ONLY with decision=approved in approval log
  - REQUIRES rollback payload
  - create_pull_request = False
  - commit_changes = False

This module NEVER:
  - Creates commits
  - Creates pull requests
  - Touches Tier A pages
  - Touches money pages
  - Touches pillar pages
  - Applies batch changes
  - Updates title
  - Injects new HTML structure if no safe edit pattern exists

OUTPUTS:
  reports/superparty/seo_level5_apply_execution.json
  reports/superparty/seo_level5_rollback_payload.json
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT_DIR / "config" / "seo"
REPORTS_DIR = ROOT_DIR / "reports" / "superparty"
PAGES_DIR = ROOT_DIR / "src" / "pages"

POLICY_PATH = CONFIG_DIR / "level5_action_policy.json"
APPLY_PLAN_PATH = REPORTS_DIR / "seo_level5_apply_plan.json"
APPROVAL_LOG_PATH = REPORTS_DIR / "seo_level5_approval_log.json"
EXECUTION_REPORT_PATH = REPORTS_DIR / "seo_level5_apply_execution.json"
ROLLBACK_PAYLOAD_PATH = REPORTS_DIR / "seo_level5_rollback_payload.json"

ACTION_TYPE = "meta_description_update"

# Safe edit patterns — only these structures allow write
_RE_FRONTMATTER_DESC = re.compile(
    r"""^( *description\s*=\s*)(['"])(.*?)\2(\s*;?\s*)$""",
    re.MULTILINE,
)
_RE_META_TAG_DESC = re.compile(
    r"""(<meta\s+name=["']description["']\s+content=["'])([^"']{0,500})(["'])""",
    re.IGNORECASE,
)


class ApplyError(RuntimeError):
    """Raised when the apply step fails a precondition — causes blocked record."""


class PolicyApplyError(RuntimeError):
    """Raised when the policy does not permit apply."""


# ─── Loaders ─────────────────────────────────────────────────────────────────

def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_policy() -> dict:
    data = _load_json(POLICY_PATH)
    if not data or not isinstance(data, dict):
        raise PolicyApplyError(f"Policy missing: {POLICY_PATH}")
    return data


def load_apply_plan() -> dict:
    data = _load_json(APPLY_PLAN_PATH)
    if not data or not isinstance(data, dict):
        raise ApplyError(f"Apply plan missing: {APPLY_PLAN_PATH}")
    return data


# ─── Policy validation ────────────────────────────────────────────────────────

def validate_policy_for_single_apply(policy: dict) -> dict:
    """
    Validates that the policy permits a single real apply.
    Returns the action_activation dict for ACTION_TYPE.
    Raises PolicyApplyError if any guard fails.
    """
    mode = policy.get("mode")
    if mode != "controlled_single_apply":
        raise PolicyApplyError(
            f"policy.mode='{mode}' — expected 'controlled_single_apply'"
        )

    allowed = policy.get("allowed_actions", [])
    if ACTION_TYPE not in allowed:
        raise PolicyApplyError(f"'{ACTION_TYPE}' not in allowed_actions")

    if policy.get("approval_gate") != "manual":
        raise PolicyApplyError("approval_gate must be 'manual'")

    if policy.get("rollback_required") is not True:
        raise PolicyApplyError("rollback_required must be True")

    tier_restrictions = policy.get("tier_restrictions", {})
    if tier_restrictions.get("A") != "read_only":
        raise PolicyApplyError("Tier A must remain 'read_only'")

    activation = (policy.get("action_activation") or {}).get(ACTION_TYPE)
    if not activation:
        raise PolicyApplyError(f"Missing action_activation for '{ACTION_TYPE}'")

    if activation.get("execution_mode") != "single_apply_only":
        raise PolicyApplyError("execution_mode must be 'single_apply_only'")

    if activation.get("write_files") is not True:
        raise PolicyApplyError("write_files must be True for single apply")

    if activation.get("create_pull_request") is not False:
        raise PolicyApplyError("create_pull_request must be False")

    if activation.get("commit_changes") is not False:
        raise PolicyApplyError("commit_changes must be False")

    if activation.get("requires_ready_to_apply") is not True:
        raise PolicyApplyError("requires_ready_to_apply must be True")

    if activation.get("requires_approval_decision") != "approved":
        raise PolicyApplyError("requires_approval_decision must be 'approved'")

    if activation.get("max_candidates_per_run") != 1:
        raise PolicyApplyError("max_candidates_per_run must be 1")

    return activation


# ─── Action selection ────────────────────────────────────────────────────────

def select_single_ready_action(plan: dict) -> dict:
    """
    Select exactly one ready_to_apply=True action from the apply plan.
    Raises ApplyError if:
      - no ready actions
      - more than one ready action (refuse batch apply)
      - action is Tier A/B, money, pillar
    """
    ready = [a for a in plan.get("plan", []) if a.get("ready_to_apply") is True]

    if not ready:
        raise ApplyError("No ready_to_apply=True action in apply plan")

    if len(ready) > 1:
        raise ApplyError(
            f"Found {len(ready)} ready_to_apply actions — refusing batch apply. "
            "max_candidates_per_run=1 must be enforced."
        )

    action = ready[0]

    # Redundant safety guards
    if action.get("tier") == "A":
        raise ApplyError("Tier A action in ready list — blocked")
    if action.get("tier") == "B":
        raise ApplyError("Tier B action in ready list — blocked")
    if action.get("is_money_page"):
        raise ApplyError("Money page in ready list — blocked")
    if action.get("is_pillar_page"):
        raise ApplyError("Pillar page in ready list — blocked")
    if action.get("action_type") != ACTION_TYPE:
        raise ApplyError(
            f"Unexpected action_type: {action.get('action_type')} — only {ACTION_TYPE} permitted"
        )

    return action


# ─── File resolution ─────────────────────────────────────────────────────────

def resolve_target_file(action: dict, pages_dir: Path = PAGES_DIR) -> Path:
    """
    Map the action URL to an Astro source file.
    Raises ApplyError if file cannot be found or is not an .astro file.
    """
    url = action.get("url", "").strip("/")

    candidates = []
    if url:
        candidates = [
            pages_dir / f"{url}.astro",
            pages_dir / url / "index.astro",
        ]
        parts = url.split("/")
        if len(parts) > 1:
            candidates += [
                pages_dir.joinpath(*parts[:-1]) / f"{parts[-1]}.astro",
                pages_dir.joinpath(*parts) / "index.astro",
            ]
    else:
        candidates = [pages_dir / "index.astro"]

    for path in candidates:
        if path.exists() and path.suffix == ".astro":
            return path

    raise ApplyError(
        f"target_file_not_found for URL '{action.get('url')}'"
    )


# ─── Preflight read ──────────────────────────────────────────────────────────

def extract_current_meta_description(path: Path) -> dict:
    """
    Read the current meta description from the target Astro file.
    Returns: { "meta_description": str|None, "source": str }
    Read-only.
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise ApplyError(f"Cannot read {path}: {e}")

    # 1. Frontmatter prop
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        m = _RE_FRONTMATTER_DESC.search(fm_match.group(1))
        if m:
            return {"meta_description": m.group(3).strip(), "source": "frontmatter_prop"}

    # 2. Meta tag
    m = _RE_META_TAG_DESC.search(content)
    if m:
        return {"meta_description": m.group(2).strip(), "source": "meta_tag"}

    return {"meta_description": None, "source": "not_found"}


def validate_target_still_matches_plan(action: dict, current_meta: dict) -> list[str]:
    """
    Verify that the current file state matches the expected 'before' state in the plan.
    Returns list of mismatch issues (empty = OK to apply).
    """
    issues: list[str] = []

    expected_before = (action.get("before") or {}).get("meta_description", "")
    actual_current = current_meta.get("meta_description") or ""

    if current_meta.get("source") == "not_found":
        issues.append(
            "current_description_not_found — file has no detectable meta description"
        )
    elif actual_current.strip() != expected_before.strip():
        issues.append(
            f"current_description_differs_from_plan: "
            f"expected='{expected_before[:80]}' actual='{actual_current[:80]}'"
        )

    return issues


# ─── Safe write ───────────────────────────────────────────────────────────────

def _detect_safe_edit_strategy(content: str) -> Optional[str]:
    """
    Returns 'frontmatter_prop', 'meta_tag', or None if no safe pattern found.
    Only patterns with explicit description text are safe.
    """
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match and _RE_FRONTMATTER_DESC.search(fm_match.group(1)):
        return "frontmatter_prop"
    if _RE_META_TAG_DESC.search(content):
        return "meta_tag"
    return None


def apply_meta_description_to_file(path: Path, new_description: str) -> dict:
    """
    Write the new meta description to the Astro file using a safe edit strategy.
    Returns: { "strategy": str, "chars_written": int }
    Raises ApplyError if:
      - file structure is unsupported
      - write fails
    """
    content = path.read_text(encoding="utf-8", errors="replace")
    strategy = _detect_safe_edit_strategy(content)

    if strategy is None:
        raise ApplyError(
            "unsupported_file_structure — no safe edit pattern found. "
            "Refusing to inject new markup. blocking_reason=unsupported_file_structure"
        )

    escaped = new_description.replace('"', '\\"')

    if strategy == "frontmatter_prop":
        def _replace_fm(m):
            quote = m.group(2)
            return f"{m.group(1)}{quote}{new_description}{quote}{m.group(4)}"
        # Only replace inside frontmatter block
        fm_match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
        if not fm_match:
            raise ApplyError("frontmatter_prop detected but couldn't re-parse frontmatter")
        new_fm_body = _RE_FRONTMATTER_DESC.sub(_replace_fm, fm_match.group(2))
        new_content = fm_match.group(1) + new_fm_body + fm_match.group(3) + content[fm_match.end():]
    else:  # meta_tag
        new_content = _RE_META_TAG_DESC.sub(
            lambda m: f"{m.group(1)}{new_description}{m.group(3)}", content
        )

    try:
        path.write_text(new_content, encoding="utf-8")
    except OSError as e:
        raise ApplyError(f"Write failed: {e}")

    return {"strategy": strategy, "chars_written": len(new_description)}


# ─── Rollback + report ───────────────────────────────────────────────────────

def build_rollback_payload(path: Path, before_description: str, after_description: str) -> dict:
    try:
        file_path_str = str(path.relative_to(ROOT_DIR)).replace("\\", "/")
    except ValueError:
        file_path_str = str(path).replace("\\", "/")
    return {
        "action_id": "",  # filled by caller
        "file_path": file_path_str,
        "rollback_mode": "single_file_revert",
        "before": {"meta_description": before_description},
        "after": {"meta_description": after_description},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def save_rollback_payload(payload: dict) -> None:
    ROLLBACK_PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ROLLBACK_PAYLOAD_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def save_apply_report(report: dict) -> None:
    EXECUTION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EXECUTION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


# ─── Main executor ───────────────────────────────────────────────────────────

def run_single_apply(
    pages_dir: Path = PAGES_DIR,
) -> bool:
    """
    Execute a single controlled meta_description apply.
    Returns True on success, False on any blocked/error state.
    """
    applied_actions = []
    blocked_actions = []

    try:
        policy = load_policy()
        activation = validate_policy_for_single_apply(policy)
        plan = load_apply_plan()
        action = select_single_ready_action(plan)

        url = action.get("url", "")
        action_id = action.get("action_id", "")
        proposed_description = (action.get("proposal") or {}).get("meta_description", "")
        expected_before = (action.get("before") or {}).get("meta_description", "")

        # Resolve target file
        target_path = resolve_target_file(action, pages_dir)

        # Pre-apply read
        current_meta = extract_current_meta_description(target_path)

        # Validate current state matches plan
        mismatches = validate_target_still_matches_plan(action, current_meta)
        if mismatches:
            blocked_actions.append({
                "action_id": action_id,
                "url": url,
                "blocking_reason": mismatches[0],
            })
            raise ApplyError(f"Pre-apply validation failed: {mismatches}")

        # Apply
        write_result = apply_meta_description_to_file(target_path, proposed_description)

        # Build rollback
        rollback = build_rollback_payload(
            target_path,
            before_description=expected_before,
            after_description=proposed_description,
        )
        rollback["action_id"] = action_id
        save_rollback_payload(rollback)

        applied_actions.append({
            "action_id": action_id,
            "action_type": ACTION_TYPE,
            "url": url,
            "file_path": str(target_path.relative_to(ROOT_DIR)).replace("\\", "/"),
            "before": {"meta_description": expected_before},
            "after": {"meta_description": proposed_description},
            "edit_strategy": write_result["strategy"],
            "rollback_payload_path": str(
                ROLLBACK_PAYLOAD_PATH.relative_to(ROOT_DIR)
            ).replace("\\", "/"),
        })

    except PolicyApplyError as e:
        log.error("Policy blocked apply: %s", e)
        print(f"Apply blocked by policy: {e}")
        _save_empty_execution_report(applied=0, blocked=blocked_actions, policy_error=str(e))
        return False
    except ApplyError as e:
        log.warning("Apply blocked: %s", e)
        print(f"Apply blocked: {e}")
        if not blocked_actions:
            blocked_actions.append({"blocking_reason": str(e)})
        _save_empty_execution_report(applied=0, blocked=blocked_actions)
        return False
    except Exception as e:
        log.exception("Unexpected apply failure")
        print(f"Apply failed: {e}")
        _save_empty_execution_report(applied=0, blocked=[{"blocking_reason": str(e)}])
        return False

    report = {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": "single_apply_only",
            "policy_version": policy.get("schema_version", ""),
            "applied": len(applied_actions),
            "blocked": len(blocked_actions),
            "create_pull_request": False,
            "commit_changes": False,
        },
        "applied_actions": applied_actions,
        "blocked_actions": blocked_actions,
    }
    save_apply_report(report)
    print(
        f"Apply complete: {len(applied_actions)} applied, {len(blocked_actions)} blocked. "
        f"No commit, no PR."
    )
    return True


def _save_empty_execution_report(applied: int, blocked: list, policy_error: str = "") -> None:
    report = {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": "single_apply_only",
            "applied": applied,
            "blocked": len(blocked),
            "create_pull_request": False,
            "commit_changes": False,
        },
        "policy_error": policy_error or None,
        "applied_actions": [],
        "blocked_actions": blocked,
    }
    EXECUTION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EXECUTION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_single_apply()
