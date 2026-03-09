"""
SEO Level 5 — Controlled Single Auto-Apply Engine (PR #88 Hardening)

Executa auto-apply pentru exact 1 actiune meta_description_update pe Tier C,
NUMAI daca feature flag este activ.

## Activare feature flag (ordinea de prioritate):
  1. config/seo/auto_apply_runtime_override.json  (neversioned, in .gitignore)
     → daca fisierul exista si are "enabled": true → ACTIVAT
  2. config/seo/level5_action_policy.json
     → daca auto_apply_config.enabled: true → ACTIVAT
  3. Altfel → DEZACTIVAT (default safe)

## Oprire instant:
  - Seteaza "enabled": false in auto_apply_runtime_override.json
  - SAU sterge fisierul auto_apply_runtime_override.json
  - SAU seteaza auto_apply_config.enabled: false in policy

CONSTRAINTS — acest modul NICIODATA:
  - Nu aplica actiuni pe Tier A sau Tier B
  - Nu aplica actiuni pe money pages sau pillar pages
  - Nu aplica actiuni pe URL-uri din pillar_pages_registry.json
  - Nu aplica alt action_type decat meta_description_update
  - Nu creeaza commits sau pull requests
  - Nu aplica mai mult de 1 candidat per run
  - Nu introduce auto-learning sau feedback loop autonom
  - Nu ocoleste rollback_required
  - Nu aplica acelasi URL mai des de 1× la 14 zile (cooldown guard)

OUTPUTS:
  reports/superparty/seo_level5_auto_apply_log.json  (append-only audit trail)
  reports/superparty/seo_level5_apply_execution.json (standard execution report)
  reports/superparty/seo_level5_rollback_payload.json
  reports/superparty/seo_level5_status.json          (ops visibility read-only)
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

ROOT_DIR    = Path(__file__).parent.parent.parent
CONFIG_DIR  = ROOT_DIR / "config" / "seo"
REPORTS_DIR = ROOT_DIR / "reports" / "superparty"
PAGES_DIR   = ROOT_DIR / "src" / "pages"

POLICY_PATH              = CONFIG_DIR  / "level5_action_policy.json"
OVERRIDE_PATH            = CONFIG_DIR  / "auto_apply_runtime_override.json"
PILLAR_REGISTRY_PATH     = CONFIG_DIR  / "pillar_pages_registry.json"
DRY_RUN_REPORT_PATH      = REPORTS_DIR / "seo_level5_dry_run_actions.json"
APPLY_PLAN_PATH          = REPORTS_DIR / "seo_level5_apply_plan.json"
AUTO_APPLY_LOG_PATH      = REPORTS_DIR / "seo_level5_auto_apply_log.json"
EXECUTION_REPORT_PATH    = REPORTS_DIR / "seo_level5_apply_execution.json"
ROLLBACK_PAYLOAD_PATH    = REPORTS_DIR / "seo_level5_rollback_payload.json"
STATUS_REPORT_PATH       = REPORTS_DIR / "seo_level5_status.json"

ACTION_TYPE = "meta_description_update"
APPROVED_BY = "system_auto_apply"
COOLDOWN_DAYS = 14

# Edit patterns
_RE_FRONTMATTER_DESC = re.compile(
    r"""^( *description\s*=\s*)(['"'])(.*?)\2(\s*;?\s*)$""",
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


def load_pillar_registry(registry_path: Path = PILLAR_REGISTRY_PATH) -> list:
    """Load list of pillar page URLs from registry. Returns empty list if missing."""
    data = _load_json(registry_path)
    if not data:
        return []
    return data.get("pillar_pages", [])


# ─── Feature flag — override-first resolution ────────────────────────────────

def get_activation_source(
    policy: dict,
    override_path: Path = OVERRIDE_PATH,
) -> str:
    """
    Returns the source of the activation decision:
      "override_file"  — override file exists and has enabled=true
      "policy"         — policy has auto_apply_config.enabled=true (no override)
      "disabled"       — both sources have enabled=false or override missing
    """
    override = _load_json(override_path)
    if override is not None:
        if override.get("enabled", False) is True:
            return "override_file"
        else:
            return "disabled"  # override file exists but disabled → short-circuit
    # No override file → fall through to policy
    cfg = policy.get("auto_apply_config", {})
    if cfg.get("enabled", False) is True:
        return "policy"
    return "disabled"


def check_auto_apply_enabled(
    policy: dict,
    override_path: Path = OVERRIDE_PATH,
) -> bool:
    """
    Returns True ONLY if activation source is not 'disabled'.
    Override file takes priority over policy.
    """
    return get_activation_source(policy, override_path) != "disabled"


# ─── Pillar registry guard ───────────────────────────────────────────────────

def check_pillar_registry(url: str, registry_path: Path = PILLAR_REGISTRY_PATH) -> list:
    """
    Returns blockers if URL is in pillar registry.
    This guard runs independently of is_pillar_page field in the action plan,
    closing the vulnerability where a plan incorrectly marks a pillar page as non-pillar.
    """
    pillar_urls = load_pillar_registry(registry_path)
    # Normalize: compare without trailing slash
    url_norm = url.rstrip("/")
    for p in pillar_urls:
        if p.rstrip("/") == url_norm:
            return ["pillar_page_in_registry"]
    return []


# ─── Cooldown guard ──────────────────────────────────────────────────────────

def check_url_cooldown(
    url: str,
    log_path: Path = AUTO_APPLY_LOG_PATH,
    days: int = COOLDOWN_DAYS,
) -> list:
    """
    Returns blocker if URL was auto-applied within the last `days` days.
    Prevents re-applying the same URL too frequently.
    """
    existing = _load_json(log_path) or []
    if not isinstance(existing, list):
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    for entry in existing:
        if entry.get("url") != url:
            continue
        applied_str = entry.get("applied_at", "")
        if not applied_str:
            continue
        try:
            applied_at = datetime.fromisoformat(applied_str)
            if applied_at.tzinfo is None:
                applied_at = applied_at.replace(tzinfo=timezone.utc)
            if applied_at >= cutoff:
                return [f"url_in_cooldown_last_{days}_days"]
        except (ValueError, TypeError):
            continue
    return []


# ─── Eligibility ──────────────────────────────────────────────────────────────

def validate_auto_apply_eligibility(action: dict, policy: dict) -> list:
    """
    Returns list of blockers. Empty list = eligible.
    Checks: action_type, tier, money_page, pillar_page (from plan).
    NOTE: feature flag check is done BEFORE calling this function in run_controlled_auto_apply.
    NOTE: pillar_registry check is separate (check_pillar_registry).
    """
    blockers = []
    cfg = policy.get("auto_apply_config", {})

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
    activation_source: str = "policy",
) -> dict:
    """Build the audit trail record for one auto-apply."""
    return {
        "auto_apply_id": str(uuid.uuid4()),
        "action_id": action.get("action_id", ""),
        "url": action.get("url", ""),
        "approved_by": APPROVED_BY,
        "approval_mode": "auto_applied",
        "proposal_source": action.get("proposal_source", "unknown"),
        "activation_source": activation_source,
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


# ─── Status report ────────────────────────────────────────────────────────────

def generate_status_report(
    policy: dict,
    activation_source: str,
    last_run_blocked_reason: Optional[str] = None,
    override_path: Path = OVERRIDE_PATH,
    log_path: Path = AUTO_APPLY_LOG_PATH,
    rollback_path: Path = ROLLBACK_PAYLOAD_PATH,
    status_path: Path = STATUS_REPORT_PATH,
) -> dict:
    """
    Generate a read-only ops visibility report.
    Writes to seo_level5_status.json.
    """
    enabled = activation_source != "disabled"
    log_entries = _load_json(log_path) or []
    last_apply = None
    if isinstance(log_entries, list) and log_entries:
        last = log_entries[-1]
        last_apply = {
            "url": last.get("url"),
            "applied_at": last.get("applied_at"),
            "proposal_source": last.get("proposal_source"),
            "strategy": last.get("strategy"),
            "auto_apply_id": last.get("auto_apply_id"),
            "activation_source": last.get("activation_source"),
        }

    # Cooldown active URLs (applied in last 14 days)
    cutoff = datetime.now(timezone.utc) - timedelta(days=COOLDOWN_DAYS)
    cooldown_urls = []
    if isinstance(log_entries, list):
        seen = set()
        for entry in log_entries:
            url = entry.get("url", "")
            applied_str = entry.get("applied_at", "")
            if url in seen:
                continue
            try:
                applied_at = datetime.fromisoformat(applied_str)
                if applied_at.tzinfo is None:
                    applied_at = applied_at.replace(tzinfo=timezone.utc)
                if applied_at >= cutoff:
                    cooldown_urls.append(url)
                    seen.add(url)
            except (ValueError, TypeError):
                continue

    rollback_available = rollback_path.exists()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "activation": {
            "enabled": enabled,
            "source": activation_source,
        },
        "last_apply": last_apply,
        "cooldown_active_urls": cooldown_urls,
        "rollback_available": rollback_available,
        "last_run_blocked_reason": last_run_blocked_reason,
        "policy_version": policy.get("schema_version", "unknown"),
    }
    _write_json(status_path, report)
    return report


# ─── Main entry point ─────────────────────────────────────────────────────────

def run_controlled_auto_apply(
    pages_dir: Path = PAGES_DIR,
    policy_path: Path = POLICY_PATH,
    apply_plan_path: Path = APPLY_PLAN_PATH,
    override_path: Path = OVERRIDE_PATH,
    pillar_registry_path: Path = PILLAR_REGISTRY_PATH,
    log_path: Path = AUTO_APPLY_LOG_PATH,
) -> Optional[bool]:
    """
    Entry point for controlled single auto-apply.

    Returns:
      None   — feature flag is OFF; no action taken
      True   — apply successful
      False  — blocked by a guardrail; no file modified
    """
    import agent.tasks.seo_level5_auto_apply as _self_mod

    policy = _load_json(policy_path)
    if not policy:
        log.error("Policy not found: %s", policy_path)
        return False

    # ── Feature flag check (override-first) ──────────────────────────────────
    activation_source = get_activation_source(policy, override_path)
    if activation_source == "disabled":
        log.info("auto_apply disabled (source: policy+override) — skipping (flag OFF)")
        generate_status_report(policy, activation_source, last_run_blocked_reason="flag_off",
                               override_path=override_path, log_path=log_path,
                               rollback_path=_self_mod.ROLLBACK_PAYLOAD_PATH,
                               status_path=_self_mod.STATUS_REPORT_PATH)
        return None  # Sentinel: flag OFF, no action

    log.info("auto_apply enabled (source: %s) — checking eligibility", activation_source)

    # ── Load plan ─────────────────────────────────────────────────────────────
    plan = _load_json(apply_plan_path)
    if not plan:
        log.warning("Apply plan not found: %s", apply_plan_path)
        generate_status_report(policy, activation_source, last_run_blocked_reason="no_apply_plan",
                               override_path=override_path, log_path=log_path,
                               rollback_path=_self_mod.ROLLBACK_PAYLOAD_PATH,
                               status_path=_self_mod.STATUS_REPORT_PATH)
        return False

    # ── Candidate count ───────────────────────────────────────────────────────
    count_blockers = validate_candidate_count(plan, policy)
    if count_blockers:
        log.warning("Auto-apply blocked (candidate count): %s", count_blockers)
        generate_status_report(policy, activation_source,
                               last_run_blocked_reason=str(count_blockers),
                               override_path=override_path, log_path=log_path,
                               rollback_path=_self_mod.ROLLBACK_PAYLOAD_PATH,
                               status_path=_self_mod.STATUS_REPORT_PATH)
        return False

    candidates = [a for a in plan.get("plan", []) if a.get("ready_to_apply") is True]
    action = candidates[0]  # exactly 1 at this point
    action_url = action.get("url", "")

    # ── Pillar registry guard (independent of plan's is_pillar_page) ──────────
    registry_blockers = check_pillar_registry(action_url, pillar_registry_path)
    if registry_blockers:
        log.warning("Auto-apply blocked (pillar registry): %s — url=%s", registry_blockers, action_url)
        generate_status_report(policy, activation_source,
                               last_run_blocked_reason=str(registry_blockers),
                               override_path=override_path, log_path=log_path,
                               rollback_path=_self_mod.ROLLBACK_PAYLOAD_PATH,
                               status_path=_self_mod.STATUS_REPORT_PATH)
        return False

    # ── Cooldown guard ────────────────────────────────────────────────────────
    cooldown_blockers = check_url_cooldown(action_url, log_path=log_path)
    if cooldown_blockers:
        log.warning("Auto-apply blocked (cooldown): %s — url=%s", cooldown_blockers, action_url)
        generate_status_report(policy, activation_source,
                               last_run_blocked_reason=str(cooldown_blockers),
                               override_path=override_path, log_path=log_path,
                               rollback_path=_self_mod.ROLLBACK_PAYLOAD_PATH,
                               status_path=_self_mod.STATUS_REPORT_PATH)
        return False

    # ── Eligibility ───────────────────────────────────────────────────────────
    eligibility_blockers = validate_auto_apply_eligibility(action, policy)
    if eligibility_blockers:
        log.warning("Auto-apply blocked (eligibility): %s", eligibility_blockers)
        generate_status_report(policy, activation_source,
                               last_run_blocked_reason=str(eligibility_blockers),
                               override_path=override_path, log_path=log_path,
                               rollback_path=_self_mod.ROLLBACK_PAYLOAD_PATH,
                               status_path=_self_mod.STATUS_REPORT_PATH)
        return False

    # ── Proposal validity ─────────────────────────────────────────────────────
    proposal_desc = (action.get("proposal") or {}).get("meta_description", "")
    proposal_blockers = validate_proposal(proposal_desc)
    if proposal_blockers:
        log.warning("Auto-apply blocked (proposal): %s", proposal_blockers)
        generate_status_report(policy, activation_source,
                               last_run_blocked_reason=str(proposal_blockers),
                               override_path=override_path, log_path=log_path,
                               rollback_path=_self_mod.ROLLBACK_PAYLOAD_PATH,
                               status_path=_self_mod.STATUS_REPORT_PATH)
        return False

    # ── File state (drift check) ──────────────────────────────────────────────
    file_blockers = validate_file_state(action, pages_dir)
    if file_blockers:
        log.warning("Auto-apply blocked (file drift): %s", file_blockers)
        generate_status_report(policy, activation_source,
                               last_run_blocked_reason=str(file_blockers),
                               override_path=override_path, log_path=log_path,
                               rollback_path=_self_mod.ROLLBACK_PAYLOAD_PATH,
                               status_path=_self_mod.STATUS_REPORT_PATH)
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
        "not_in_pillar_registry",
        "not_in_cooldown",
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
    _write_json(_self_mod.ROLLBACK_PAYLOAD_PATH, rollback)

    # ── Audit trail ───────────────────────────────────────────────────────────
    record = build_auto_apply_record(
        action=action,
        policy=policy,
        before_desc=before_desc,
        after_desc=proposal_desc,
        strategy=strategy,
        auto_apply_reason=auto_apply_reason,
        activation_source=activation_source,
    )
    append_auto_apply_log(record, log_path=log_path)

    # ── Execution report ──────────────────────────────────────────────────────
    execution_report = {
        "metadata": {
            "schema_version": policy.get("schema_version", "1.3"),
            "approval_mode": "auto_applied",
            "approved_by": APPROVED_BY,
            "activation_source": activation_source,
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

    # ── Status report ─────────────────────────────────────────────────────────
    generate_status_report(policy, activation_source, last_run_blocked_reason=None,
                           override_path=override_path, log_path=log_path,
                           rollback_path=_self_mod.ROLLBACK_PAYLOAD_PATH,
                           status_path=_self_mod.STATUS_REPORT_PATH)

    log.info(
        "Auto-apply SUCCESS: url=%s strategy=%s auto_apply_id=%s activation_source=%s",
        action.get("url"), strategy, record["auto_apply_id"], activation_source,
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
