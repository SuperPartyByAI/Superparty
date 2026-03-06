import pytest
from agent.tasks.seo_level4_registry import (
    get_owner_url,
    get_allowed_supporters,
    is_owner,
    is_allowed_supporter,
    is_forbidden,
    classify_url_vs_cluster,
    is_cannibalizing
)

def test_get_owner():
    assert get_owner_url("money_root_animatori_petreceri_copii") == "/animatori-petreceri-copii"
    assert get_owner_url("money_geo_bucuresti") == "/petreceri/bucuresti"

def test_is_owner():
    assert is_owner("/animatori-petreceri-copii", "money_root_animatori_petreceri_copii") is True
    assert is_owner("/petreceri/bucuresti/sector-1", "money_root_animatori_petreceri_copii") is False

def test_allowed_supporters():
    # pilonul accepta toate articolele
    assert is_allowed_supporter("/articole/de-citit", "money_root_animatori_petreceri_copii") is True
    
    # bucuresti accepta pilon si contact
    assert is_allowed_supporter("/animatori-petreceri-copii", "money_geo_bucuresti") is True
    assert is_allowed_supporter("/contact", "money_geo_bucuresti") is True
    assert is_allowed_supporter("/petreceri/ilfov", "money_geo_bucuresti") is False

def test_is_forbidden():
    # pilonul respinge alte URL-uri pe termenii sai cheie (petreceri comerciale)
    assert is_forbidden("/petreceri/ilfov", "money_root_animatori_petreceri_copii") is True
    assert is_forbidden("/servicii-optionale/mascote", "money_root_animatori_petreceri_copii") is True

def test_classify_and_cannibalize():
    # 1. Scenariu Owner
    assert classify_url_vs_cluster("/petreceri/bucuresti", "money_geo_bucuresti") == "owner"
    assert is_cannibalizing("/petreceri/bucuresti", "money_geo_bucuresti") is False

    # 2. Scenariu Supporter valid
    assert classify_url_vs_cluster("/contact", "money_geo_bucuresti") == "supporter"
    assert is_cannibalizing("/contact", "money_geo_bucuresti") is False

    # 3. Scenariu Forbidden (Canibalizare directa / Drift)
    assert classify_url_vs_cluster("/petreceri/ilfov", "money_geo_bucuresti") == "forbidden"
    assert is_cannibalizing("/petreceri/ilfov", "money_geo_bucuresti") is True

    # 4. Scenariu Unknown (nevalidat conform planului Level 4 => interzis automat conform reguli drift)
    assert classify_url_vs_cluster("/preturi", "sector_1") == "unknown"
    assert is_cannibalizing("/preturi", "sector_1") is True
