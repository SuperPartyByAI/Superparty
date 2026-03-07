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
import uuid
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
# PR #61: Astro component prop pattern — description="..." inside <Layout .../> or <Layout ...>
# Matches:  description="Any text here"
# Used by all petreceri/* and other pages that pass description as a Layout prop.
_RE_LAYOUT_PROP_DESC = re.compile(
    r"""([ \t]*description=)(['"])([^'"]{0,500})\2""",
    re.MULTILINE,
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
      - approval_record.decision != 'approved' (redundant gate, do not trust upstream blindly)
      - approval_record.decided_by is empty
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

    # Redundant safety guards (do NOT trust upstream to have done these)
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

    # Approval record re-check — redundant guard, do NOT trust plan[] snapshot alone
    approval_record = action.get("approval_record") or {}
    if approval_record.get("decision") != "approved":
        raise ApplyError(
            f"approval_record.decision='{approval_record.get('decision')}' — "
            "only 'approved' actions may be applied. Blocked."
        )
    if not (approval_record.get("decided_by") or "").strip():
        raise ApplyError(
            "approval_record.decided_by is empty — operator identity required before apply. Blocked."
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

    # 2. PR #61: Layout prop
    m = _RE_LAYOUT_PROP_DESC.search(content)
    if m:
        return {"meta_description": m.group(3).strip(), "source": "layout_prop"}

    # 3. Meta tag
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
    Returns 'frontmatter_prop', 'layout_prop', 'meta_tag', or None.
    Priority: frontmatter_prop > layout_prop > meta_tag.
    PR #61: added layout_prop for Astro component prop format (description=\"...\").
    """
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match and _RE_FRONTMATTER_DESC.search(fm_match.group(1)):
        return "frontmatter_prop"
    if _RE_LAYOUT_PROP_DESC.search(content):
        return "layout_prop"
    if _RE_META_TAG_DESC.search(content):
        return "meta_tag"
    return None


def apply_meta_description_to_file(path: Path, new_description: str) -> dict:
    """
    Write the new meta description to the Astro file using a safe edit strategy.
    Returns: { "strategy": str, "chars_written": int }
    Raises ApplyError if:
      - file structure is unsupported
      - new_description contains quote characters incompatible with detected pattern
      - write fails
    """
    content = path.read_text(encoding="utf-8", errors="replace")
    strategy = _detect_safe_edit_strategy(content)

    if strategy is None:
        raise ApplyError(
            "unsupported_file_structure — no safe edit pattern found. "
            "Refusing to inject new markup. blocking_reason=unsupported_file_structure"
        )

    # Quote-safety check per strategy
    if strategy == "frontmatter_prop":
        fm_match_for_quote = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        fm_body = fm_match_for_quote.group(1) if fm_match_for_quote else ""
        q_match = _RE_FRONTMATTER_DESC.search(fm_body)
        if q_match:
            used_quote = q_match.group(2)
            if used_quote in new_description:
                raise ApplyError(
                    f"unsafe_proposal_contains_quote: proposal contains '{used_quote}' which "
                    f"is used as frontmatter string delimiter. Refusing to write to avoid "
                    f"file corruption. blocking_reason=unsafe_proposal_contains_quote"
                )
    elif strategy == "layout_prop":
        # PR #61: layout_prop uses ' or " as delimiter
        lp_match = _RE_LAYOUT_PROP_DESC.search(content)
        if lp_match:
            used_quote = lp_match.group(2)
            if used_quote in new_description:
                raise ApplyError(
                    f"unsafe_proposal_contains_quote: proposal contains '{used_quote}' which "
                    f"is used as layout prop delimiter. Refusing to write. "
                    f"blocking_reason=unsafe_proposal_contains_quote"
                )
    else:  # meta_tag
        tag_match = _RE_META_TAG_DESC.search(content)
        if tag_match:
            used_quote = tag_match.group(3)
            if used_quote in new_description:
                raise ApplyError(
                    f"unsafe_proposal_contains_quote: proposal contains '{used_quote}' which "
                    f"is used as meta tag attribute delimiter. Refusing to write. "
                    f"blocking_reason=unsafe_proposal_contains_quote"
                )

    if strategy == "frontmatter_prop":
        def _replace_fm(m):
            quote = m.group(2)
            return f"{m.group(1)}{quote}{new_description}{quote}{m.group(4)}"
        fm_match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
        if not fm_match:
            raise ApplyError("frontmatter_prop detected but couldn't re-parse frontmatter")
        new_fm_body = _RE_FRONTMATTER_DESC.sub(_replace_fm, fm_match.group(2))
        new_content = fm_match.group(1) + new_fm_body + fm_match.group(3) + content[fm_match.end():]
    elif strategy == "layout_prop":
        # PR #61: replace description=\"old\" with description=\"new\" preserving the quote char
        lp_match = _RE_LAYOUT_PROP_DESC.search(content)
        if not lp_match:
            raise ApplyError("layout_prop detected but couldn't re-parse prop")
        quote = lp_match.group(2)
        new_content = _RE_LAYOUT_PROP_DESC.sub(
            lambda m: f"{m.group(1)}{quote}{new_description}{quote}",
            content,
            count=1,
        )
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


# ─── Live approval reconciliation (PR #59) ───────────────────────────────────

def _load_approval_log_live() -> list:
    """Load the live approval log from disk. Returns [] if absent."""
    data = _load_json(APPROVAL_LOG_PATH)
    if data is None:
        return []
    if not isinstance(data, list):
        raise ApplyError(f"approval_log is not a list: {APPROVAL_LOG_PATH}")
    return data


def reconcile_with_live_approval_log(action: dict, approval_record_snapshot: dict) -> dict:
    """
    PR #59: Re-verify the selected action against the live seo_level5_approval_log.json.
    Do NOT trust the plan[] snapshot alone.

    Checks (all must pass):
      1. Exactly one matching live record by action_id
      2. decision == 'approved'
      3. decided_by is non-empty
      4. action_type matches plan snapshot
      5. url matches plan snapshot
      6. proposal_snapshot.before matches plan.before
      7. proposal_snapshot.proposal matches plan.proposal
      8. No duplicate 'approved' live records for same action_id

    Returns: the matching live approval record on success.
    Raises: ApplyError with blocking_reason on any mismatch.
    """
    live_log = _load_approval_log_live()
    action_id = action.get("action_id", "")

    matching = [e for e in live_log if e.get("action_id") == action_id]

    if not matching:
        raise ApplyError(
            f"live_approval_record_not_found: no entry in approval_log for action_id='{action_id}'. "
            "blocking_reason=live_approval_record_not_found"
        )

    approved_matching = [e for e in matching if e.get("decision") == "approved"]

    if len(approved_matching) == 0:
        found_decisions = [e.get("decision") for e in matching]
        raise ApplyError(
            f"live_approval_decision_not_approved: action_id='{action_id}' found in log "
            f"but decision={found_decisions}. blocking_reason=live_approval_decision_not_approved"
        )

    if len(approved_matching) > 1:
        raise ApplyError(
            f"live_approval_duplicate: {len(approved_matching)} approved entries found "
            f"for action_id='{action_id}'. Ambiguous — refusing to apply. "
            "blocking_reason=live_approval_duplicate"
        )

    live_record = approved_matching[0]

    # Decided-by must be present
    if not (live_record.get("decided_by") or "").strip():
        raise ApplyError(
            f"live_approval_decided_by_empty: action_id='{action_id}' approved but "
            "decided_by is empty. blocking_reason=live_approval_decided_by_empty"
        )

    # decision_id must match the plan snapshot (if snapshot has it)
    snapshot_decision_id = (approval_record_snapshot or {}).get("decision_id")
    if snapshot_decision_id and live_record.get("decision_id") != snapshot_decision_id:
        raise ApplyError(
            f"live_approval_decision_id_mismatch: plan snapshot decision_id='{snapshot_decision_id}' "
            f"does not match live record decision_id='{live_record.get('decision_id')}'. "
            "blocking_reason=live_approval_decision_id_mismatch"
        )

    # action_type must match
    if live_record.get("action_type") != action.get("action_type"):
        raise ApplyError(
            f"live_approval_action_type_mismatch: plan action_type='{action.get('action_type')}' "
            f"!= live action_type='{live_record.get('action_type')}'. "
            "blocking_reason=live_approval_action_type_mismatch"
        )

    # url must match
    if live_record.get("url") != action.get("url"):
        raise ApplyError(
            f"live_approval_url_mismatch: plan url='{action.get('url')}' "
            f"!= live url='{live_record.get('url')}'. "
            "blocking_reason=live_approval_url_mismatch"
        )

    # proposal_snapshot.before must match plan.before
    live_snap_before = (live_record.get("proposal_snapshot") or {}).get("before", {})
    plan_before = action.get("before", {})
    if live_snap_before != plan_before and live_snap_before:  # only if snapshot exists
        raise ApplyError(
            f"live_approval_before_mismatch: proposal_snapshot.before in live log "
            f"does not match plan.before. "
            "blocking_reason=live_approval_before_mismatch"
        )

    # proposal_snapshot.proposal must match plan.proposal
    live_snap_proposal = (live_record.get("proposal_snapshot") or {}).get("proposal", {})
    plan_proposal = action.get("proposal", {})
    if live_snap_proposal != plan_proposal and live_snap_proposal:  # only if snapshot exists
        raise ApplyError(
            f"live_approval_proposal_mismatch: proposal_snapshot.proposal in live log "
            f"does not match plan.proposal. "
            "blocking_reason=live_approval_proposal_mismatch"
        )

    return live_record


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

        action_id = action.get("action_id", "")
        approval_record_snapshot = action.get("approval_record") or {}
        plan_id = action.get("plan_id", "")
        url = action.get("url", "")
        proposed_description = (action.get("proposal") or {}).get("meta_description", "")
        expected_before = (action.get("before") or {}).get("meta_description", "")

        # PR #59: Live approval reconciliation — do NOT trust plan[] snapshot alone
        live_record = reconcile_with_live_approval_log(action, approval_record_snapshot)
        decision_id = live_record.get("decision_id", "")

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

        # PR #59: Verify after-value in file (post-write read confirmation)
        post_write_meta = extract_current_meta_description(target_path)
        after_value_verified = (
            post_write_meta.get("meta_description", "").strip() == proposed_description.strip()
        )

        # Build rollback
        rollback = build_rollback_payload(
            target_path,
            before_description=expected_before,
            after_description=proposed_description,
        )
        rollback["action_id"] = action_id
        rollback["plan_id"] = plan_id
        rollback["decision_id"] = decision_id
        save_rollback_payload(rollback)

        # PR #59: Validate rollback payload coherence
        rollback_ready = bool(
            rollback.get("before", {}).get("meta_description") is not None
            and rollback.get("after", {}).get("meta_description")
            and rollback.get("file_path")
            and rollback.get("rollback_mode") == "single_file_revert"
        )

        try:
            rollback_path_str = str(
                ROLLBACK_PAYLOAD_PATH.relative_to(ROOT_DIR)
            ).replace("\\", "/")
        except ValueError:
            rollback_path_str = str(ROLLBACK_PAYLOAD_PATH).replace("\\", "/")

        # PR #59: Fail-closed on post-write verification failure.
        # Rollback payload is already saved — do NOT delete it, it may aid manual recovery.
        # applied=0, action goes to blocked[] with explicit blocking_reason.
        if not after_value_verified:
            blocked_actions.append({
                "action_id": action_id,
                "url": url,
                "blocking_reason": "post_write_verification_failed",
                "after_value_verified": False,
                "rollback_payload_path": rollback_path_str,
                "rollback_ready": rollback_ready,
            })
            raise ApplyError(
                f"post_write_verification_failed: file '{target_path}' does not contain "
                "the expected new description after write. "
                "Rollback payload has been saved. Manual review required. "
                "blocking_reason=post_write_verification_failed"
            )

        applied_actions.append({
            # Lineage (PR #59)
            "execution_id": str(uuid.uuid4()),
            "plan_id": plan_id,
            "decision_id": decision_id,
            "policy_version": policy.get("schema_version", ""),
            # Action identity
            "action_id": action_id,
            "action_type": ACTION_TYPE,
            "url": url,
            "file_path": str(target_path.relative_to(ROOT_DIR)).replace("\\", "/"),
            # Before / after
            "before": {"meta_description": expected_before},
            "after": {"meta_description": proposed_description},
            "edit_strategy": write_result["strategy"],
            # Post-write verification
            "after_value_verified": after_value_verified,
            # Rollback
            "rollback_payload_path": rollback_path_str,
            "rollback_ready": rollback_ready,
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
