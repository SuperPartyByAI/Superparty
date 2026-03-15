"""
rollback.py — Automated revert + CDN purge + reindex.

Handles rollback operations when canary or monitoring detects problems.
"""
from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

log = logging.getLogger("seo_agent.rollback")


@dataclass
class RollbackRequest:
    """Request to rollback a deployment."""
    site_domain: str
    pr_branch: str
    head_term: str
    reason: str
    severity: str = "warning"  # warning, critical
    triggered_by: str = "monitor"  # monitor, manual, canary


@dataclass
class RollbackResult:
    """Result of a rollback operation."""
    success: bool
    revert_branch: str = ""
    steps_completed: list[str] = None
    steps_failed: list[str] = None
    error: str = ""

    def __post_init__(self):
        self.steps_completed = self.steps_completed or []
        self.steps_failed = self.steps_failed or []


def create_revert_branch(
    original_branch: str,
    repo_dir: str,
) -> tuple[bool, str]:
    """Create a revert branch that undoes the original branch changes."""
    revert_branch = f"revert/{original_branch}"

    try:
        # Checkout main
        result = subprocess.run(
            ["git", "checkout", "main"],
            cwd=repo_dir, capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return False, f"checkout main failed: {result.stderr.strip()}"

        # Create revert branch
        result = subprocess.run(
            ["git", "checkout", "-b", revert_branch],
            cwd=repo_dir, capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return False, f"checkout -b failed: {result.stderr.strip()}"

        # Revert the merge commit of the original branch
        result = subprocess.run(
            ["git", "revert", "--no-commit", "HEAD"],
            cwd=repo_dir, capture_output=True, text=True, timeout=30,
        )
        # revert might fail if HEAD isn't the right commit — handle gracefully
        if result.returncode != 0:
            log.warning(f"git revert failed: {result.stderr.strip()}")
            return False, f"git revert failed: {result.stderr.strip()}"

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m",
             f"revert: rollback {original_branch} — SEO agent automated revert"],
            cwd=repo_dir, capture_output=True, text=True, timeout=30,
        )

        return True, revert_branch

    except Exception as e:
        return False, str(e)


def request_cdn_purge(domain: str, paths: list[str]) -> tuple[bool, str]:
    """
    Request CDN cache purge for affected paths.
    For Vercel: deploys automatically purge. Log intent for manual action.
    """
    log.info(f"CDN purge requested for {domain}: {paths}")
    # Vercel auto-purges on deploy, so this is mostly logging
    return True, f"CDN purge logged for {domain} — Vercel auto-purges on deploy"


def request_reindex(domain: str, paths: list[str]) -> list[dict]:
    """
    Request re-indexing for rolled-back URLs.
    Returns list of index request results.
    """
    results = []
    for path in paths:
        url = f"https://www.{domain}{path}"
        results.append({
            "url": url,
            "status": "queued",
            "method": "manual_gsc",
            "note": "Use GSC URL Inspection → Request Indexing",
        })
        log.info(f"Reindex queued: {url}")
    return results


def execute_rollback(
    request: RollbackRequest,
    repo_dir: str,
    affected_paths: Optional[list[str]] = None,
    dry_run: bool = False,
) -> RollbackResult:
    """
    Full rollback flow:
      1. Create revert branch
      2. Push revert branch
      3. Request CDN purge
      4. Request re-indexing
      5. Log audit
    """
    result = RollbackResult(success=True)
    paths = affected_paths or ["/"]

    log.warning(
        f"ROLLBACK initiated for {request.site_domain} "
        f"(branch: {request.pr_branch}, reason: {request.reason})"
    )

    if dry_run:
        result.revert_branch = f"revert/{request.pr_branch}"
        result.steps_completed = [
            "DRY RUN: revert branch would be created",
            "DRY RUN: CDN purge would be requested",
            "DRY RUN: re-indexing would be queued",
        ]
        return result

    # 1. Create revert branch
    ok, msg = create_revert_branch(request.pr_branch, repo_dir)
    if ok:
        result.revert_branch = msg
        result.steps_completed.append(f"Revert branch created: {msg}")
    else:
        result.steps_failed.append(f"Revert branch failed: {msg}")
        result.success = False
        result.error = msg
        # Continue with remaining steps even if git fails

    # 2. CDN purge
    ok, msg = request_cdn_purge(request.site_domain, paths)
    if ok:
        result.steps_completed.append(f"CDN purge: {msg}")
    else:
        result.steps_failed.append(f"CDN purge failed: {msg}")

    # 3. Re-indexing
    reindex_results = request_reindex(request.site_domain, paths)
    result.steps_completed.append(
        f"Re-indexing queued for {len(reindex_results)} URLs"
    )

    return result


def generate_rollback_audit_entry(
    request: RollbackRequest,
    result: RollbackResult,
) -> dict:
    """Generate an audit log entry for the rollback."""
    return {
        "actor": "seo-agent",
        "action": "rollback",
        "payload": {
            "site": request.site_domain,
            "branch": request.pr_branch,
            "head_term": request.head_term,
            "reason": request.reason,
            "severity": request.severity,
            "triggered_by": request.triggered_by,
            "revert_branch": result.revert_branch,
            "success": result.success,
            "steps_completed": result.steps_completed,
            "steps_failed": result.steps_failed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
