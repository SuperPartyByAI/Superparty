"""
seo_control.py — Control plane enterprise pentru agentul SEO.

Kill switches, state machine per URL, tier control, allow/deny list.
Toate valorile vin din env vars sau control_state.json — fara cod nou la deploy.

Kill switches (env vars):
  SEO_FREEZE=1                 — opreste complet apply + experiments
  SEO_FREEZE_APPLY=1           — opreste doar apply real
  SEO_FREEZE_EXPERIMENTS=1     — opreste doar experiments
  SEO_PILLAR_LOCK=1            — interzice experiments pe pilon
  SEO_ALLOWLIST=slug1,slug2    — doar acestea pot fi procesate
  SEO_DENYLIST=slug1,slug2     — acestea sunt blocate explicit
  SEO_TIER_A_ONLY=1            — ruleaza doar pe Tier A

State machine per URL:
  eligible -> planned -> applied_real / experiment_A / experiment_B
           -> blocked_policy / blocked_budget / blocked_cooldown / blocked_active_experiment
           -> winner / reverted / frozen / manual_lock

Tier-uri:
  Tier A: pilon + hub-uri principale (max protectie)
  Tier B: sectoare (control moderat)
  Tier C: localitati Ilfov (expansiune controlata)
"""

import os
import json
from pathlib import Path
from datetime import date, datetime

# ─── Kill switches ────────────────────────────────────────────────────────────

def is_frozen() -> bool:
    """SEO_FREEZE=1 opreste complet tot agentul."""
    return os.environ.get("SEO_FREEZE", "0") == "1"

def is_apply_frozen() -> bool:
    return is_frozen() or os.environ.get("SEO_FREEZE_APPLY", "0") == "1"

def is_experiments_frozen() -> bool:
    return is_frozen() or os.environ.get("SEO_FREEZE_EXPERIMENTS", "0") == "1"

def is_pillar_locked() -> bool:
    """SEO_PILLAR_LOCK=1 interzice experiments pe /animatori-petreceri-copii."""
    return os.environ.get("SEO_PILLAR_LOCK", "0") == "1"

def get_allowlist() -> set:
    """SEO_ALLOWLIST=slug1,slug2 — doar acestea pot fi procesate (gol = toate)."""
    raw = os.environ.get("SEO_ALLOWLIST", "").strip()
    return {s.strip() for s in raw.split(",") if s.strip()} if raw else set()

def get_denylist() -> set:
    """SEO_DENYLIST=slug1,slug2 — blocate explicit."""
    raw = os.environ.get("SEO_DENYLIST", "").strip()
    return {s.strip() for s in raw.split(",") if s.strip()} if raw else set()

def is_tier_a_only() -> bool:
    return os.environ.get("SEO_TIER_A_ONLY", "0") == "1"


# ─── Tier classification ─────────────────────────────────────────────────────

TIER_A = {
    "animatori-petreceri-copii",      # pilon
    "bucuresti",                       # hub principal
    "ilfov",                           # hub principal
}

TIER_B = {
    "sector-1", "sector-2", "sector-3",
    "sector-4", "sector-5", "sector-6",
}

# Tier C = localitati Ilfov (orice altceva din manifest indexabil)

def get_tier(slug: str) -> str:
    """Returnează Tier A / B / C pentru un slug."""
    slug_lower = slug.lower().replace("/petreceri/", "").replace("/", "").strip()
    if slug_lower in TIER_A:
        return "A"
    if slug_lower in TIER_B:
        return "B"
    return "C"

def get_tier_config(tier: str) -> dict:
    """Configuratie per tier: agresivitate, experiments, cooldown."""
    configs = {
        "A": {
            "max_experiments": 1,
            "experiment_policy": "conservative",
            "rollback_threshold": 0.10,   # 10% CTR drop => rollback
            "position_guard": 1.0,         # max 1 pozitie drop acceptata
            "cooldown_days": 14,
            "apply_policy": "gated",
        },
        "B": {
            "max_experiments": 2,
            "experiment_policy": "moderate",
            "rollback_threshold": 0.15,
            "position_guard": 1.5,
            "cooldown_days": 7,
            "apply_policy": "standard",
        },
        "C": {
            "max_experiments": 3,
            "experiment_policy": "expansive",
            "rollback_threshold": 0.20,
            "position_guard": 2.0,
            "cooldown_days": 7,
            "apply_policy": "standard",
        },
    }
    return configs.get(tier, configs["C"])


# ─── URL State Machine ─────────────────────────────────────────────────────────

VALID_STATES = {
    "eligible",
    "planned",
    "applied_real",
    "experiment_A",
    "experiment_B",
    "winner",
    "reverted",
    "blocked_policy",
    "blocked_budget",
    "blocked_cooldown",
    "blocked_active_experiment",
    "frozen",
    "manual_lock",
}

STATE_FILE = Path("reports/seo/url_states.json")

def load_url_states() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_url_states(states: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(states, indent=2, ensure_ascii=False), encoding="utf-8")

def get_url_state(url_path: str) -> str:
    states = load_url_states()
    return states.get(url_path, "eligible")

def set_url_state(url_path: str, state: str, reason: str = ""):
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state: {state}. Must be one of: {VALID_STATES}")
    states = load_url_states()
    states[url_path] = {
        "state": state,
        "reason": reason,
        "updated_at": str(datetime.now()),
        "tier": get_tier(url_path),
    }
    save_url_states(states)

def freeze_url(url_path: str, reason: str = "manual"):
    """Manual lock / freeze pe un URL specific."""
    set_url_state(url_path, "frozen", reason)

def lock_url(url_path: str, reason: str = "manual_lock"):
    set_url_state(url_path, "manual_lock", reason)

def unfreeze_url(url_path: str):
    set_url_state(url_path, "eligible", "unfrozen")


# ─── Policy check complet (de rulat înainte de orice apply/experiment) ─────────

def check_policy(url_path: str, action: str = "apply") -> dict:
    """
    Verifică dacă un URL poate fi procesat.
    action = "apply" | "experiment"
    
    Returns: {"allowed": bool, "reason": str, "tier": str}
    """
    slug = url_path.strip("/").replace("petreceri/", "")
    tier = get_tier(url_path)

    # 1. Global freeze
    if is_frozen():
        return {"allowed": False, "reason": "SEO_FREEZE=1 (global freeze)", "tier": tier}

    # 2. Action-specific freeze
    if action == "apply" and is_apply_frozen():
        return {"allowed": False, "reason": "SEO_FREEZE_APPLY=1", "tier": tier}
    if action == "experiment" and is_experiments_frozen():
        return {"allowed": False, "reason": "SEO_FREEZE_EXPERIMENTS=1", "tier": tier}

    # 3. Pilon lock pe experiments
    if action == "experiment" and is_pillar_locked() and slug == "animatori-petreceri-copii":
        return {"allowed": False, "reason": "SEO_PILLAR_LOCK=1 (pilon protejat)", "tier": tier}

    # 4. Tier A only mode
    if is_tier_a_only() and tier != "A":
        return {"allowed": False, "reason": "SEO_TIER_A_ONLY=1 (doar Tier A activ)", "tier": tier}

    # 5. Allowlist
    allowlist = get_allowlist()
    if allowlist and slug not in allowlist:
        return {"allowed": False, "reason": f"Not in SEO_ALLOWLIST: {slug}", "tier": tier}

    # 6. Denylist
    denylist = get_denylist()
    if slug in denylist:
        return {"allowed": False, "reason": f"In SEO_DENYLIST: {slug}", "tier": tier}

    # 7. Manual state check
    states = load_url_states()
    url_state_data = states.get(url_path, {})
    url_state = url_state_data.get("state", "eligible") if isinstance(url_state_data, dict) else url_state_data
    if url_state in {"frozen", "manual_lock"}:
        return {"allowed": False, "reason": f"URL state = {url_state}", "tier": tier}

    return {"allowed": True, "reason": "policy OK", "tier": tier}


# ─── Smoke test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== SEO Control Plane Status ===")
    print(f"  SEO_FREEZE: {os.environ.get('SEO_FREEZE','0')}")
    print(f"  SEO_FREEZE_APPLY: {os.environ.get('SEO_FREEZE_APPLY','0')}")
    print(f"  SEO_FREEZE_EXPERIMENTS: {os.environ.get('SEO_FREEZE_EXPERIMENTS','0')}")
    print(f"  SEO_PILLAR_LOCK: {os.environ.get('SEO_PILLAR_LOCK','0')}")
    print(f"  SEO_ALLOWLIST: {os.environ.get('SEO_ALLOWLIST','(gol = toate)')}")
    print(f"  SEO_DENYLIST: {os.environ.get('SEO_DENYLIST','(gol = niciunul)')}")
    print(f"  SEO_TIER_A_ONLY: {os.environ.get('SEO_TIER_A_ONLY','0')}")
    print()
    for path in ["/animatori-petreceri-copii", "/petreceri/bucuresti", "/petreceri/ilfov",
                 "/petreceri/sector-1", "/petreceri/otopeni"]:
        result = check_policy(path, "apply")
        tier = result["tier"]
        ok = "✓" if result["allowed"] else "✗"
        print(f"  {ok} [{tier}] {path}: {result['reason']}")
