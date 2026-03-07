import pytest
from agent.tasks.seo_level4_cluster_health import generate_cluster_health

def test_generate_cluster_health():
    mock_gsc_data = [
        # București acționează ca suport curat (conform fix PR#42) -> zero warning
        {"query": "animatori petreceri copii", "page": "https://superparty.ro/petreceri/bucuresti/", "impressions": 500, "clicks": 50},
        
        # Pilonul central convertește la sine însuși -> zero warning
        {"query": "petreceri copii", "page": "/animatori-petreceri-copii", "impressions": 1000, "clicks": 150},
        
        # Sector 1 încearcă să vândă pe query național -> Forbidden -> Canibalizare 
        {"query": "animatori copii", "page": "/petreceri/sector-1", "impressions": 100, "clicks": 5},
        
        # Owner curat de geo bucurești -> zero warning
        {"query": "animatori petreceri copii bucuresti", "page": "/petreceri/bucuresti", "impressions": 300, "clicks": 40},
        
        # Sub-pilon Ilfov încearcă expansiune invalidă peste București -> Forbidden -> Canibalizare
        {"query": "animatori copii bucuresti", "page": "/petreceri/ilfov", "impressions": 50, "clicks": 0}
    ]
    
    report = generate_cluster_health(mock_gsc_data)
    clusters = report.get("clusters", {})
    
    # 1. Evaluare Cluster ROOT
    root_cluster = clusters.get("money_root_animatori_petreceri_copii")
    assert root_cluster is not None
    assert root_cluster["total_impressions"] == 1600
    assert root_cluster["owner_present"] is True
    assert root_cluster["owner_impressions"] == 1000
    assert root_cluster["supporter_count"] == 1
    assert root_cluster["forbidden_count"] == 1
    
    root_warning_urls = [w["url"] for w in root_cluster["cannibalization_warnings"]]
    assert "/petreceri/sector-1" in root_warning_urls
    assert "/petreceri/bucuresti" not in root_warning_urls
    assert "/animatori-petreceri-copii" not in root_warning_urls
    
    # Level 4.1 PR #50: verific ca owner_clicks si owner_share sunt calculate corect
    assert root_cluster["owner_clicks"] == 150  # clicks venind de la owner URL
    assert root_cluster["owner_share"] == round(1000 / 1600, 4)  # 0.625
    
    # Validează payload metadate pe return object
    assert "metadata" in report
    assert report["metadata"]["input_rows"] == 5
    assert report["metadata"]["clusters_count"] == 2
    
    # 2. Evaluare Cluster GEO BUCURESTI
    buc_cluster = clusters.get("money_geo_bucuresti")
    assert buc_cluster is not None
    assert buc_cluster["total_impressions"] == 350
    assert buc_cluster["owner_present"] is True
    
    buc_warning_urls = [w["url"] for w in buc_cluster["cannibalization_warnings"]]
    assert "/petreceri/ilfov" in buc_warning_urls
    assert "/petreceri/bucuresti" not in buc_warning_urls


def test_owner_present_accumulates_owner_impressions_clicks_and_share():
    """
    PR #50: Cluster cu owner URL prezent — verifica ca owner_impressions, owner_clicks
    si owner_share sunt calculate corect din GSC rows.
    """
    gsc_rows = [
        {"query": "animatori petreceri copii", "page": "/animatori-petreceri-copii", "impressions": 800, "clicks": 60},
        {"query": "animatori petreceri copii", "page": "/animatori-petreceri-copii", "impressions": 200, "clicks": 15},
        {"query": "animatori petreceri copii", "page": "/petreceri/bucuresti", "impressions": 100, "clicks": 5},
    ]
    report = generate_cluster_health(gsc_rows)
    cluster = report["clusters"].get("money_root_animatori_petreceri_copii")
    assert cluster is not None
    assert cluster["owner_present"] is True
    assert cluster["total_impressions"] == 1100
    assert cluster["owner_impressions"] == 1000  # 800 + 200
    assert cluster["owner_clicks"] == 75           # 60 + 15
    assert cluster["owner_share"] == round(1000 / 1100, 4)  # ~0.9091


def test_owner_absent_returns_all_owner_fields_zero():
    """
    PR #50: Cluster fara URL owner in GSC — owner_impressions, owner_clicks si owner_share
    trebuie sa fie 0/0/0.0. owner_present trebuie sa fie False.
    """
    gsc_rows = [
        # Sector 1 apare pe query-ul root, dar NU este owner URL
        {"query": "animatori petreceri copii", "page": "/petreceri/sector-1", "impressions": 300, "clicks": 10},
        {"query": "animatori petreceri copii", "page": "/petreceri/sector-2", "impressions": 150, "clicks": 5},
    ]
    report = generate_cluster_health(gsc_rows)
    cluster = report["clusters"].get("money_root_animatori_petreceri_copii")
    assert cluster is not None
    assert cluster["owner_present"] is False
    assert cluster["owner_impressions"] == 0
    assert cluster["owner_clicks"] == 0
    assert cluster["owner_share"] == 0.0


def test_total_impressions_zero_gives_owner_share_zero():
    """
    PR #50: Guard pentru impartire la zero — daca total_impressions este 0,
    owner_share trebuie sa fie 0.0, nu NaN sau ZeroDivisionError.
    """
    # Rows cu impressions=0 dar valide ca query/page
    gsc_rows = [
        {"query": "animatori petreceri copii", "page": "/animatori-petreceri-copii", "impressions": 0, "clicks": 0},
    ]
    report = generate_cluster_health(gsc_rows)
    cluster = report["clusters"].get("money_root_animatori_petreceri_copii")
    assert cluster is not None
    assert cluster["total_impressions"] == 0
    assert cluster["owner_impressions"] == 0
    assert cluster["owner_clicks"] == 0
    assert cluster["owner_share"] == 0.0, "Guard div-by-zero: owner_share trebuie sa fie 0.0 cand total_impressions=0"
