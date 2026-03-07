"""
SEO Level 5 — Manual Approval Workflow (PR #56)

Captures a human operator's decision (approved / rejected) on proposed dry-run actions
from seo_level5_dry_run_actions.json.

CONSTRAINTS — this module NEVER:
  - Edits page source files
  - Creates commits
  - Creates pull requests
  - Triggers any apply engine hook
  - Writes back to the dry-run report itself

OUTPUT: reports/superparty/seo_level5_approval_log.json
  A structured, append-only log of operator decisions.

Schema for each approval record:
{
  "decision_id":    str,      # unique ID for this decision record
  "action_id":      str,      # matches action_id in seo_level5_dry_run_actions.json
  "action_type":    str,
  "url":            str,
  "decision":       "approved" | "rejected",
  "decided_by":     str,      # operator identifier (e.g. "ops-review-manual")
  "decided_at":     str,      # ISO 8601 UTC
  "notes":          str|None, # optional operator notes
  "proposal_snapshot": {      # snapshot of what was proposed at decision time
    "before":   dict,
    "proposal": dict,
  }
}
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent
REPORTS_DIR = ROOT_DIR / "reports" / "superparty"

DRY_RUN_REPORT_PATH = REPORTS_DIR / "seo_level5_dry_run_actions.json"
APPROVAL_LOG_PATH = REPORTS_DIR / "seo_level5_approval_log.json"

Decision = Literal["approved", "rejected"]

VALID_DECISIONS = {"approved", "rejected"}


class ApprovalError(ValueError):
    """Raised when an approval operation fails a pre-condition."""


# ─── Readers (read-only) ──────────────────────────────────────────────────────

def load_dry_run_report() -> dict:
    """
    Load the current dry-run proposals report.
    STRICTLY read-only — this function does not write anything.
    """
    if not DRY_RUN_REPORT_PATH.exists():
        raise ApprovalError(
            f"Dry-run report not found: {DRY_RUN_REPORT_PATH}. "
            "Run seo_level5_meta_description_dry_run.py first."
        )
    with open(DRY_RUN_REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_approval_log() -> list[dict]:
    """
    Load the existing approval log. Returns empty list if no log exists yet.
    STRICTLY read-only.
    """
    if not APPROVAL_LOG_PATH.exists():
        return []
    with open(APPROVAL_LOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def list_pending_actions() -> list[dict]:
    """
    Returns the list of proposed actions from the dry-run report that have
    not yet received a decision in the approval log.

    An action is "pending" if its action_id does NOT appear in the approval log.
    This function does NOT modify any file.
    """
    report = load_dry_run_report()
    log_entries = load_approval_log()

    decided_ids = {entry["action_id"] for entry in log_entries}
    actions = report.get("actions", [])

    pending = [a for a in actions if a.get("action_id") not in decided_ids]
    return pending


def get_action_by_id(action_id: str) -> Optional[dict]:
    """
    Retrieve a single proposed action from the dry-run report by its action_id.
    Returns None if not found. Read-only.
    """
    report = load_dry_run_report()
    for action in report.get("actions", []):
        if action.get("action_id") == action_id:
            return action
    return None


# ─── Decision recording (append-only log write) ───────────────────────────────

def _build_decision_record(
    action: dict,
    decision: Decision,
    decided_by: str,
    notes: Optional[str],
) -> dict:
    """Build the approval record dict. Does not write anything."""
    return {
        "decision_id": str(uuid.uuid4()),
        "action_id": action["action_id"],
        "action_type": action.get("action_type", ""),
        "url": action.get("url", ""),
        "decision": decision,
        "decided_by": decided_by,
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
        "proposal_snapshot": {
            "before": action.get("before", {}),
            "proposal": action.get("proposal", {}),
        },
    }


def record_decision(
    action_id: str,
    decision: Decision,
    decided_by: str = "ops-manual-review",
    notes: Optional[str] = None,
) -> dict:
    """
    Record an operator's decision for a single proposed action.

    Constraints:
    - action_id must exist in the dry-run report
    - decision must be 'approved' or 'rejected'
    - If action_id already has a decision, raises ApprovalError (no overwrite)
    - Writes ONLY to seo_level5_approval_log.json (append-only)
    - Does NOT edit any page source file
    - Does NOT create commits or PRs
    - Does NOT trigger any apply engine

    Returns the created decision record.
    """
    if decision not in VALID_DECISIONS:
        raise ApprovalError(
            f"Invalid decision '{decision}'. Must be one of: {VALID_DECISIONS}"
        )

    if not decided_by or not decided_by.strip():
        raise ApprovalError("decided_by cannot be empty — operator must be identified")

    action = get_action_by_id(action_id)
    if action is None:
        raise ApprovalError(
            f"action_id '{action_id}' not found in dry-run report. "
            "Proposed actions: run list_pending_actions() to see available IDs."
        )

    # Guard: prevent duplicate decisions
    existing_log = load_approval_log()
    for entry in existing_log:
        if entry.get("action_id") == action_id:
            raise ApprovalError(
                f"action_id '{action_id}' already has a recorded decision: "
                f"'{entry['decision']}' by '{entry['decided_by']}' at {entry['decided_at']}. "
                "Decisions are immutable once recorded."
            )

    record = _build_decision_record(action, decision, decided_by, notes)

    # Append-only write to approval log
    updated_log = existing_log + [record]
    APPROVAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(APPROVAL_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_log, f, indent=2, ensure_ascii=False)

    log.info(
        "Decision recorded: action_id=%s decision=%s by=%s",
        action_id, decision, decided_by
    )
    return record


def get_approval_summary() -> dict:
    """
    Returns a summary of decisions in the approval log alongside pending counts.
    Read-only.
    """
    report = load_dry_run_report()
    total_proposed = len(report.get("actions", []))

    log_entries = load_approval_log()
    approved = sum(1 for e in log_entries if e.get("decision") == "approved")
    rejected = sum(1 for e in log_entries if e.get("decision") == "rejected")
    decided = len(log_entries)
    pending = total_proposed - decided

    return {
        "total_proposed": total_proposed,
        "total_decided": decided,
        "approved": approved,
        "rejected": rejected,
        "pending": pending,
        "applied": 0,  # invariant: approval workflow never applies anything
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys

    pending = list_pending_actions()
    if not pending:
        print("No pending actions to review.")
        sys.exit(0)

    print(f"\n{len(pending)} action(s) pending review:\n")
    for action in pending:
        print(f"  ID:       {action['action_id']}")
        print(f"  URL:      {action['url']}")
        print(f"  Before:   {action.get('before', {}).get('meta_description', '(empty)')[:80]}")
        print(f"  Proposal: {action.get('proposal', {}).get('meta_description', '')[:80]}")
        print()
        decision_input = input("Decision [approved/rejected/skip]: ").strip().lower()
        if decision_input in ("approved", "rejected"):
            notes = input("Notes (optional): ").strip() or None
            record = record_decision(action["action_id"], decision_input, notes=notes)  # type: ignore
            print(f"  ✓ Recorded: {record['decision_id']}\n")
        else:
            print("  Skipped.\n")

    summary = get_approval_summary()
    print(f"Summary: {summary}")
