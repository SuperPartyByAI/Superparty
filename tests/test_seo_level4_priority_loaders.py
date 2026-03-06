import pytest
from pathlib import Path
from agent.tasks.seo_level4_priority import load_registry_policies

def test_loader_reads_proper_registry():
    # Se va asigura ca load_registry_policies parseaza exact documentul principal de reguli
    # si il returneaza in cheia globala 'registry'
    registry = load_registry_policies()
    
    assert isinstance(registry, dict)
    
    # Trebuie sa existe macar Pilonul principal (stim ca este deja versionat si scris acolo)
    if "money_root_animatori_petreceri_copii" in registry:
        policy = registry["money_root_animatori_petreceri_copii"]
        assert policy["risk_tier"] == "A"
        assert policy["business_priority"] == "critical"
        assert "owner_url" in policy
