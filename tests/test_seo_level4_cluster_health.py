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
