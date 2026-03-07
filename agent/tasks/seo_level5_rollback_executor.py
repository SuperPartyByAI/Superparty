"""
SEO Level 5 — Manual Rollback Executor (PR #60)

Executes a controlled single-file revert based on seo_level5_rollback_payload.json.

Usage:
  python agent/tasks/seo_level5_rollback_executor.py --dry-run            # validate + show plan, no write
  python agent/tasks/seo_level5_rollback_executor.py --dry-run --validate-only  # coherence check only
  python agent/tasks/seo_level5_rollback_executor.py --execute             # perform the rollback
  python agent/tasks/seo_level5_rollback_executor.py --verify-only         # check post-rollback state

INVARIANTS:
  - Reverts ONLY meta_description, ONLY in the file specified by rollback_payload.file_path
  - Reverts ONLY the single action recorded in rollback_payload
  - Does NOT create commits
  - Does NOT create pull requests
  - Does NOT modify approval_log.json
  - Does NOT overwrite rollback_payload.json
  - Writes rollback_execution.json as audit trail

Runbook: docs/runbooks/seo/level5_rollback_manual.md
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent
REPORTS_DIR = ROOT_DIR / "reports" / "superparty"
PAGES_DIR = ROOT_DIR / "src" / "pages"

ROLLBACK_PAYLOAD_PATH = REPORTS_DIR / "seo_level5_rollback_payload.json"
EXECUTION_REPORT_PATH = REPORTS_DIR / "seo_level5_apply_execution.json"
APPROVAL_LOG_PATH = REPORTS_DIR / "seo_level5_approval_log.json"
ROLLBACK_EXECUTION_PATH = REPORTS_DIR / "seo_level5_rollback_execution.json"

# Patterns — same as apply executor (must stay in sync)
_RE_FRONTMATTER_DESC = re.compile(
    r"""^( *description\s*=\s*)(['"])(.*?)\2(\s*;?\s*)$""",
    re.MULTILINE,
)
_RE_META_TAG_DESC = re.compile(
    r"""(<meta\s+name=["']description["']\s+content=["'])([^"']{0,500})(["'])""",
    re.IGNORECASE,
)


class RollbackError(RuntimeError):
    """Raised when rollback cannot proceed safely."""


class RollbackCoherenceError(RuntimeError):
    """Raised when rollback_payload is incoherent or lineage is broken."""


# ─── Loaders ─────────────────────────────────────────────────────────────────

def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_rollback_payload() -> dict:
    data = _load_json(ROLLBACK_PAYLOAD_PATH)
    if not data or not isinstance(data, dict):
        raise RollbackCoherenceError(
            f"rollback_payload missing or invalid: {ROLLBACK_PAYLOAD_PATH}"
        )
    return data


def load_execution_report() -> Optional[dict]:
    data = _load_json(EXECUTION_REPORT_PATH)
    return data if isinstance(data, dict) else None


def load_approval_log() -> list:
    data = _load_json(APPROVAL_LOG_PATH)
    return data if isinstance(data, list) else []


# ─── Validation ──────────────────────────────────────────────────────────────

def validate_rollback_payload_coherence(payload: dict) -> list[str]:
    """
    Check structural and semantic coherence of rollback_payload.
    Returns list of issues (empty = coherent).
    """
    issues: list[str] = []

    if not payload.get("file_path"):
        issues.append("rollback_payload.file_path is missing")
    if payload.get("rollback_mode") != "single_file_revert":
        issues.append(
            f"rollback_payload.rollback_mode='{payload.get('rollback_mode')}' "
            "— expected 'single_file_revert'"
        )
    before = (payload.get("before") or {}).get("meta_description")
    if before is None:
        issues.append("rollback_payload.before.meta_description is missing")
    after = (payload.get("after") or {}).get("meta_description")
    if not after:
        issues.append("rollback_payload.after.meta_description is missing")
    if not payload.get("action_id"):
        issues.append("rollback_payload.action_id is missing")

    return issues


def validate_lineage_coherence(payload: dict) -> list[str]:
    """
    Cross-check rollback_payload lineage with execution report and approval_log.
    Returns list of issues.
    """
    issues: list[str] = []

    action_id = payload.get("action_id", "")
    plan_id = payload.get("plan_id", "")
    decision_id = payload.get("decision_id", "")

    # Check execution report
    exec_report = load_execution_report()
    if exec_report:
        applied = exec_report.get("applied_actions", [])
        matching = [a for a in applied if a.get("action_id") == action_id]
        if not matching:
            issues.append(
                f"lineage: action_id='{action_id}' not found in execution_report.applied_actions"
            )
        else:
            exec_action = matching[0]
            if plan_id and exec_action.get("plan_id") != plan_id:
                issues.append(
                    f"lineage: plan_id mismatch — payload='{plan_id}', "
                    f"execution_report='{exec_action.get('plan_id')}'"
                )
            if decision_id and exec_action.get("decision_id") != decision_id:
                issues.append(
                    f"lineage: decision_id mismatch — payload='{decision_id}', "
                    f"execution_report='{exec_action.get('decision_id')}'"
                )
    else:
        issues.append("execution_report not found — lineage cannot be verified")

    # Check approval_log
    if decision_id:
        approval_log = load_approval_log()
        matching_dec = [e for e in approval_log if e.get("decision_id") == decision_id]
        if not matching_dec:
            issues.append(
                f"lineage: decision_id='{decision_id}' not found in approval_log.json"
            )

    return issues


def resolve_target_file(payload: dict) -> Path:
    """Resolve file_path from payload to an absolute path."""
    file_path_str = payload.get("file_path", "")
    if not file_path_str:
        raise RollbackError("rollback_payload.file_path is empty")

    candidate = ROOT_DIR / file_path_str
    if candidate.exists():
        return candidate

    # Try from PAGES_DIR prefix
    slug = file_path_str.lstrip("/")
    candidate2 = PAGES_DIR / slug
    if candidate2.exists():
        return candidate2

    raise RollbackError(
        f"Target file not found: tried '{candidate}' and '{candidate2}'"
    )


def extract_current_meta_description(path: Path) -> str:
    """Read the current meta_description from a .astro file. Returns empty string if not found."""
    content = path.read_text(encoding="utf-8")

    m = _RE_FRONTMATTER_DESC.search(content)
    if m:
        return m.group(3)

    m = _RE_META_TAG_DESC.search(content)
    if m:
        return m.group(2)

    return ""


# ─── Core rollback write ──────────────────────────────────────────────────────

def apply_rollback_to_file(target_path: Path, restore_value: str) -> dict:
    """
    Write the restore_value back to the target file.
    Uses the same pattern detection as the apply executor.
    Returns {"strategy": str, "matched": bool}.

    Raises RollbackError if no writable pattern is found.
    """
    content = target_path.read_text(encoding="utf-8")

    # Try frontmatter first
    m = _RE_FRONTMATTER_DESC.search(content)
    if m:
        delimiter = m.group(2)
        if delimiter in restore_value:
            raise RollbackError(
                f"unsafe_restore_contains_delimiter: restore value contains "
                f"'{delimiter}' which is used as frontmatter delimiter. Manual edit required."
            )
        new_content = _RE_FRONTMATTER_DESC.sub(
            lambda match: f"{match.group(1)}{delimiter}{restore_value}{delimiter}{match.group(4)}",
            content,
            count=1,
        )
        target_path.write_text(new_content, encoding="utf-8")
        return {"strategy": "frontmatter_prop", "matched": True}

    # Try meta tag
    m = _RE_META_TAG_DESC.search(content)
    if m:
        delimiter = m.group(3)
        if delimiter in restore_value:
            raise RollbackError(
                f"unsafe_restore_contains_delimiter: restore value contains "
                f"'{delimiter}' which is used as meta_tag delimiter. Manual edit required."
            )
        new_content = _RE_META_TAG_DESC.sub(
            lambda match: f"{match.group(1)}{restore_value}{match.group(3)}",
            content,
            count=1,
        )
        target_path.write_text(new_content, encoding="utf-8")
        return {"strategy": "meta_tag", "matched": True}

    raise RollbackError(
        "unsupported_file_structure: no frontmatter description or meta_tag found. "
        "Manual edit required."
    )


# ─── Rollback report ─────────────────────────────────────────────────────────

def save_rollback_execution_report(report: dict) -> None:
    ROLLBACK_EXECUTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ROLLBACK_EXECUTION_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log.info("Rollback execution report: %s", ROLLBACK_EXECUTION_PATH)


# ─── Main entry points ────────────────────────────────────────────────────────

def run_validate_only() -> bool:
    """
    Validate rollback_payload coherence and lineage.
    Returns True if ready to roll back, False otherwise.
    """
    print("=== Rollback Payload Coherence Check ===")
    try:
        payload = load_rollback_payload()
    except RollbackCoherenceError as e:
        print(f"ERROR: {e}")
        return False

    struct_issues = validate_rollback_payload_coherence(payload)
    lineage_issues = validate_lineage_coherence(payload)
    all_issues = struct_issues + lineage_issues

    if all_issues:
        print("ISSUES FOUND:")
        for i in all_issues:
            print(f"  - {i}")
        print("\nrollback_ready: FALSE")
        return False

    print(f"action_id:   {payload.get('action_id')}")
    print(f"plan_id:     {payload.get('plan_id', 'N/A')}")
    print(f"decision_id: {payload.get('decision_id', 'N/A')}")
    print(f"file_path:   {payload.get('file_path')}")
    print(f"before:      {(payload.get('before') or {}).get('meta_description', '')[:80]}")
    print(f"after:       {(payload.get('after') or {}).get('meta_description', '')[:80]}")
    print("\nrollback_ready: TRUE")
    return True


def run_dry_run(pages_dir: Path = PAGES_DIR) -> bool:
    """
    Show what rollback would do, without writing anything.
    Returns True if rollback is feasible.
    """
    print("=== Rollback Dry Run ===")
    try:
        payload = load_rollback_payload()
    except RollbackCoherenceError as e:
        print(f"ERROR loading payload: {e}")
        return False

    issues = validate_rollback_payload_coherence(payload)
    if issues:
        for i in issues:
            print(f"ISSUE: {i}")
        return False

    try:
        target_path = resolve_target_file(payload)
    except RollbackError as e:
        print(f"ERROR resolving file: {e}")
        return False

    current = extract_current_meta_description(target_path)
    expected_after = (payload.get("after") or {}).get("meta_description", "")
    expected_before = (payload.get("before") or {}).get("meta_description", "")

    current_matches_after = current.strip() == expected_after.strip()

    result = {
        "file_path": str(target_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "current_meta_description": current,
        "expected_after": expected_after,
        "expected_before": expected_before,
        "current_matches_after": current_matches_after,
        "rollback_feasible": current_matches_after,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if not current_matches_after:
        print(
            "\nWARNING: current file content does not match payload.after. "
            "File may have been modified after apply. Rollback BLOCKED. See Scenario D in runbook."
        )
    return current_matches_after


def run_execute(pages_dir: Path = PAGES_DIR, operator: str = "ops-manual-rollback") -> bool:
    """
    Execute the rollback: revert the file and write rollback_execution.json.
    Returns True on success.
    """
    print("=== Rollback Execute ===")

    try:
        payload = load_rollback_payload()
    except RollbackCoherenceError as e:
        print(f"ERROR loading payload: {e}")
        return False

    issues = validate_rollback_payload_coherence(payload)
    if issues:
        for i in issues:
            print(f"BLOCKED: {i}")
        return False

    lineage_issues = validate_lineage_coherence(payload)
    if lineage_issues:
        print("Lineage issues (non-blocking, continuing with caution):")
        for i in lineage_issues:
            print(f"  WARN: {i}")

    try:
        target_path = resolve_target_file(payload)
    except RollbackError as e:
        print(f"ERROR: {e}")
        return False

    action_id = payload.get("action_id", "")
    plan_id = payload.get("plan_id", "")
    decision_id = payload.get("decision_id", "")
    restore_value = (payload.get("before") or {}).get("meta_description", "")
    current_after = (payload.get("after") or {}).get("meta_description", "")

    # Pre-rollback drift check
    current = extract_current_meta_description(target_path)
    if current.strip() != current_after.strip():
        print(
            f"BLOCKED: pre-rollback drift check failed. "
            f"File does not contain payload.after — cannot safely rollback. "
            f"Current='{current[:60]}', expected='{current_after[:60]}'. "
            "See Scenario D in runbook."
        )
        return False

    # Execute write
    try:
        write_result = apply_rollback_to_file(target_path, restore_value)
    except RollbackError as e:
        print(f"BLOCKED: {e}")
        return False

    # Post-rollback verification
    post_value = extract_current_meta_description(target_path)
    post_verified = post_value.strip() == restore_value.strip()

    if not post_verified:
        print(
            "ERROR: post-rollback verification failed. "
            f"File does not contain the restored value. "
            "Manual inspection required."
        )
        # Still write report to aid debugging
        report = {
            "schema_version": "1.0",
            "rollback_type": "automated_executor",
            "reverted": False,
            "post_rollback_verification": False,
            "error": "post_rollback_verification_failed",
            "reverted_at": datetime.now(timezone.utc).isoformat(),
            "reverted_by": operator,
            "original_lineage": {
                "execution_id": "",
                "plan_id": plan_id,
                "decision_id": decision_id,
                "action_id": action_id,
            },
            "file_path": str(target_path.relative_to(ROOT_DIR)).replace("\\", "/"),
            "before_restored": restore_value,
            "after_reverted": current_after,
            "edit_strategy": write_result.get("strategy", ""),
        }
        save_rollback_execution_report(report)
        return False

    # Success — write full report
    # Get execution_id from execution report if available
    exec_report = load_execution_report()
    original_execution_id = ""
    if exec_report:
        applied = exec_report.get("applied_actions", [])
        matching = [a for a in applied if a.get("action_id") == action_id]
        if matching:
            original_execution_id = matching[0].get("execution_id", "")

    report = {
        "schema_version": "1.0",
        "rollback_id": str(uuid.uuid4()),
        "rollback_type": "automated_executor",
        "reverted": True,
        "post_rollback_verification": post_verified,
        "reverted_at": datetime.now(timezone.utc).isoformat(),
        "reverted_by": operator,
        "original_lineage": {
            "execution_id": original_execution_id,
            "plan_id": plan_id,
            "decision_id": decision_id,
            "action_id": action_id,
        },
        "file_path": str(target_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "before_restored": restore_value,
        "after_reverted": current_after,
        "edit_strategy": write_result.get("strategy", ""),
    }
    save_rollback_execution_report(report)

    print(
        f"Rollback complete: '{target_path.name}' restored to before value. "
        f"Report: {ROLLBACK_EXECUTION_PATH}"
    )
    return True


def run_verify_only(pages_dir: Path = PAGES_DIR) -> bool:
    """
    Verify post-rollback state without writing anything.
    Returns True if the file has been correctly reverted.
    """
    print("=== Rollback Post-Verify ===")
    try:
        payload = load_rollback_payload()
    except RollbackCoherenceError as e:
        print(f"ERROR: {e}")
        return False

    restore_value = (payload.get("before") or {}).get("meta_description", "")

    try:
        target_path = resolve_target_file(payload)
    except RollbackError as e:
        print(f"ERROR: {e}")
        return False

    current = extract_current_meta_description(target_path)
    verified = current.strip() == restore_value.strip()

    result = {
        "file_path": str(target_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "restored_value": restore_value,
        "current_value": current,
        "post_rollback_verified": verified,
        "rollback_execution_report_exists": ROLLBACK_EXECUTION_PATH.exists(),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return verified


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Level 5 Manual Rollback Executor")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--execute", action="store_true")
    group.add_argument("--verify-only", action="store_true")
    parser.add_argument("--validate-only", action="store_true",
                        help="With --dry-run: only validate payload coherence, skip file check")
    parser.add_argument("--operator", default="ops-manual-rollback",
                        help="Operator name for rollback_execution.json (default: ops-manual-rollback)")
    args = parser.parse_args()

    if args.dry_run and args.validate_only:
        ok = run_validate_only()
    elif args.dry_run:
        ok = run_dry_run()
    elif args.execute:
        ok = run_execute(operator=args.operator)
    elif args.verify_only:
        ok = run_verify_only()
    else:
        ok = False

    raise SystemExit(0 if ok else 1)
