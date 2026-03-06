import json
import logging
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional

log = logging.getLogger(__name__)

REGISTRY_FILE = Path("config/seo/query_ownership_registry.json")

def _load_registry() -> Dict[str, Dict]:
    """Încarcă dicționarul de ownership din configurația JSON Level 4."""
    if not REGISTRY_FILE.exists():
        log.warning(f"Ownership Registry missing at {REGISTRY_FILE}")
        return {}
    try:
        data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        return data.get("registry", {})
    except Exception as e:
        log.error(f"Failed to parse registry JSON: {e}")
        return {}

def get_owner_url(cluster_id: str) -> Optional[str]:
    """Returnează slug-ul curat The Owner pentru cluster_id."""
    reg = _load_registry()
    cluster = reg.get(cluster_id, {})
    return cluster.get("owner_url")

def get_allowed_supporters(cluster_id: str) -> List[str]:
    """Returnează array-ul de string patterns URL admise ca supporter pentru un cluster."""
    reg = _load_registry()
    cluster = reg.get(cluster_id, {})
    return cluster.get("allowed_support_urls", [])

def _match_url(url: str, pattern: str) -> bool:
    """Matcher intern cu suport pentru wildcard (*) via fnmatch."""
    u = url.strip().rstrip("/")
    p = pattern.strip().rstrip("/")
    return fnmatch.fnmatch(u, p)

def is_owner(url: str, cluster_id: str) -> bool:
    """Aprobă dacă URL-ul este Owner-ul exact decretat."""
    owner = get_owner_url(cluster_id)
    if not owner:
        return False
    return _match_url(url, owner)

def is_allowed_supporter(url: str, cluster_id: str) -> bool:
    """Verifică dacă un URL este admis în whitelista suportului clusterului."""
    supporters = get_allowed_supporters(cluster_id)
    for sup in supporters:
        if _match_url(url, sup):
            return True
    return False

def is_forbidden(url: str, cluster_id: str) -> bool:
    """Verifică URL blacklist-ul acestui cluster."""
    reg = _load_registry()
    cluster = reg.get(cluster_id, {})
    forbiddens = cluster.get("forbidden_urls", [])
    for f in forbiddens:
        if _match_url(url, f):
            return True
    return False

def classify_url_vs_cluster(url: str, cluster_id: str) -> str:
    """Returnează poziția URL-ului față de acest cluster: owner | supporter | forbidden | unknown."""
    if is_owner(url, cluster_id):
        return "owner"
    if is_allowed_supporter(url, cluster_id):
        return "supporter"
    if is_forbidden(url, cluster_id):
        return "forbidden"
    
    # Implicit, orice e în sandboxul neclasificat care accesează impresii de cluster fără să fie specificat 
    # ca allowed_supporter prezintă risc.
    return "unknown"

def is_cannibalizing(url: str, cluster_id: str) -> bool:
    """
    Motorul decizional fundamental de Risc Level 4.
    Un URL este garantat canibalizant dacă extrage impresii pe un query direct dar aparține
    listei de `forbidden` SAU apare ca `unknown` pe un Tier A / B cu regim strict conservative fără suport pre-validat. 
    """
    classification = classify_url_vs_cluster(url, cluster_id)
    if classification == "owner" or classification == "supporter":
        return False
    return True
