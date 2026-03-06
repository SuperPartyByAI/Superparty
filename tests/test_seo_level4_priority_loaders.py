import pytest
from agent.tasks.seo_level4_priority import load_registry_policies

def test_loader_reads_proper_registry():
    # Asigura ca load_registry_policies extrage cu adevarat dict-ul 'registry'
    registry = load_registry_policies()
    
    assert isinstance(registry, dict), "Loader should return a dictionary"
    
    # Assert explicit pe cheia master de testare enterprise
    assert "money_root_animatori_petreceri_copii" in registry, "Master root key must be present in the loaded registry"
    
    policy = registry["money_root_animatori_petreceri_copii"]
    
    # Assertions dure pe configuratia reala
    assert policy["risk_tier"] == "A", "Master URL should be Tier A"
    assert policy["business_priority"] == "critical", "Master URL should have critical business priority"
    assert "owner_url" in policy, "Policy must expose the owner_url"
    assert policy["owner_url"] == "/animatori-petreceri-copii", "Owner URL must match the expected root"
