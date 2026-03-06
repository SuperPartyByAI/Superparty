import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

log = logging.getLogger(__name__)

CLUSTERS_FILE = Path("config/seo/query_clusters.json")

def _load_clusters() -> List[Dict]:
    """Încarcă definițiile clustererelor din sursa JSON Level 4."""
    if not CLUSTERS_FILE.exists():
        log.warning(f"Clusters registry missing at {CLUSTERS_FILE}")
        return []
    try:
        data = json.loads(CLUSTERS_FILE.read_text(encoding="utf-8"))
        return data.get("clusters", [])
    except Exception as e:
        log.error(f"Failed to parse query clusters JSON: {e}")
        return []

def normalize_query(query: str) -> str:
    """Normalizează un GSC query eliminând spațiile excedentare și casing-ul."""
    if not query:
        return ""
    return " ".join(query.lower().split())

def get_cluster_for_query(query: str) -> Optional[Dict]:
    """
    Identifică cărui cluster aparține un text query dat.
    Potrivește mai întâi exact pe canonical_queries, apoi parțial pe query_patterns.
    """
    normalized = normalize_query(query)
    if not normalized:
        return None
        
    clusters = _load_clusters()
    
    # Pass 1: Canonical Exact Match
    for c in clusters:
        canonicals = [normalize_query(q) for q in c.get("canonical_queries", [])]
        if normalized in canonicals:
            return c
            
    # Pass 2: Pattern Match (Asterisk wildcard simplu)
    for c in clusters:
        patterns = c.get("query_patterns", [])
        for pat in patterns:
            pat_clean = normalize_query(pat)
            if pat_clean.startswith("*") and pat_clean.endswith("*"):
                core = pat_clean.strip("*").strip()
                if core in normalized:
                    return c
            elif pat_clean.startswith("*"):
                if normalized.endswith(pat_clean.strip("*").strip()):
                    return c
            elif pat_clean.endswith("*"):
                if normalized.startswith(pat_clean.strip("*").strip()):
                    return c
            else:
                if normalized == pat_clean:
                    return c
                    
    return None

def get_queries_for_cluster(cluster_id: str) -> List[str]:
    """Returnează lista query-urilor canonice pentru un ID de cluster specificat."""
    clusters = _load_clusters()
    for c in clusters:
        if c.get("cluster_id") == cluster_id:
            return c.get("canonical_queries", [])
    return []

def is_money_cluster(cluster_id: str) -> bool:
    """Verifică dacă un cluster are importanță comercială directă (Pilon / Geo-Root)."""
    clusters = _load_clusters()
    for c in clusters:
        if c.get("cluster_id") == cluster_id:
            return c.get("cluster_type") in ["money_root", "money_geo"]
    return False
