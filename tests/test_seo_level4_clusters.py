import pytest
from agent.tasks.seo_level4_clusters import (
    normalize_query,
    get_cluster_for_query,
    get_queries_for_cluster,
    is_money_cluster
)

def test_normalize_query():
    assert normalize_query("  Animatori  Petreceri Copii   ") == "animatori petreceri copii"
    assert normalize_query("PETRECERI bucuresti") == "petreceri bucuresti"

def test_get_cluster_for_query_canonical_match():
    # Canonical direct
    cluster = get_cluster_for_query("animatori petreceri copii")
    assert cluster is not None
    assert cluster["cluster_id"] == "money_root_animatori_petreceri_copii"
    assert cluster["tier"] == "A"

def test_get_cluster_for_query_pattern_match():
    # Match prin pattern cu wildcard *
    cluster = get_cluster_for_query("animatori petreceri copii ieftini")
    assert cluster is not None
    assert cluster["cluster_id"] == "money_root_animatori_petreceri_copii"

    cluster_geo = get_cluster_for_query("animatori buni sectoarele bucuresti")
    assert cluster_geo is not None
    assert cluster_geo["cluster_id"] == "money_geo_bucuresti"

def test_unmatched_query():
    # Query obscur
    cluster = get_cluster_for_query("masina de spuma inchiriere cluj")
    assert cluster is None

def test_is_money_cluster():
    assert is_money_cluster("money_root_animatori_petreceri_copii") is True
    assert is_money_cluster("money_geo_bucuresti") is True
    assert is_money_cluster("sector_1") is False  # e.g sector, not root money
    assert is_money_cluster("suport_idei_petrecere") is False
