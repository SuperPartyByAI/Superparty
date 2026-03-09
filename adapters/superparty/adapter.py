"""
adapters/superparty/adapter.py — SuperPartyAdapter

Adapter specific SuperParty pentru seo-control-plane.
Implementeaza SiteAdapter cu regulile exacte din sistemul actual.

Backward-compatible cu PR #88-#94 din SuperPartyByAI/Superparty.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from core.site_adapter import SiteAdapter

# Paths relative la repo-ul SuperParty (configurat la init)
_DEFAULT_SP_ROOT = Path(__file__).parent.parent.parent.parent / "Superparty"


class SuperPartyAdapter(SiteAdapter):
    """
    Adapter pentru SuperParty (superparty.ro).

    Păstrează comportamentul exact din L5/L6 existent.
    """

    def __init__(self, superparty_root: Optional[Path] = None):
        self._root = Path(superparty_root) if superparty_root else _DEFAULT_SP_ROOT
        self._pillar_cache: Optional[set] = None

    # ── Identity ────────────────────────────────────────────────────────────

    @property
    def site_id(self) -> str:
        return "superparty"

    @property
    def site_domain(self) -> str:
        return "https://www.superparty.ro"

    # ── Paths ───────────────────────────────────────────────────────────────

    @property
    def reports_dir(self) -> Path:
        return self._root / "reports" / "superparty"

    @property
    def config_dir(self) -> Path:
        return self._root / "config" / "seo"

    @property
    def pillar_registry_path(self) -> Path:
        return self.config_dir / "pillar_pages_registry.json"

    @property
    def outcome_memory_path(self) -> Path:
        return self.reports_dir / "seo_level6_outcome_memory.json"

    @property
    def cooldown_config_path(self) -> Path:
        return self.config_dir / "auto_apply_cooldown_config.json"

    # ── Pillar Pages ─────────────────────────────────────────────────────────

    def _load_pillar_urls(self) -> set:
        if self._pillar_cache is not None:
            return self._pillar_cache
        path = self.pillar_registry_path
        if not path.exists():
            self._pillar_cache = set()
            return self._pillar_cache
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self._pillar_cache = {u.rstrip("/") for u in data.get("pillar_pages", [])}
        return self._pillar_cache

    def is_pillar_page(self, url_path: str) -> bool:
        normalized = url_path.rstrip("/") or "/"
        return normalized in self._load_pillar_urls()

    # ── Money Pages ──────────────────────────────────────────────────────────

    # Money pages sunt paginile comerciale principale SuperParty
    MONEY_PAGE_PATTERNS = [
        re.compile(r"^/animatori-petreceri-copii/?$"),
        re.compile(r"^/pachete/?"),
        re.compile(r"^/oferta/?"),
        re.compile(r"^/contact/?$"),
    ]

    def is_money_page(self, url_path: str) -> bool:
        normalized = url_path.rstrip("/") or "/"
        return any(p.match(normalized) for p in self.MONEY_PAGE_PATTERNS)

    # ── Page Type ────────────────────────────────────────────────────────────

    def get_page_type(self, url_path: str) -> str:
        if self.is_pillar_page(url_path):
            return "pillar"
        if self.is_money_page(url_path):
            return "money"
        if self.is_tier_c_eligible(url_path):
            return "tier_c"
        return "blocked"

    def is_tier_c_eligible(self, url_path: str) -> bool:
        """
        Tier C SuperParty: /petreceri/* (URL-uri locale)
        Exclude deja pillar și money pages.
        """
        if self.is_pillar_page(url_path) or self.is_money_page(url_path):
            return False
        return bool(re.match(r"^/petreceri/[a-z0-9\-]+/?$", url_path))

    # ── Tier C Catalog ───────────────────────────────────────────────────────

    def get_tier_c_catalog(self) -> list[dict]:
        """Catalog Tier C pentru Run 2 SuperParty."""
        return [
            {
                "url": "/petreceri/otopeni",
                "suggested_strategy": "local_intent",
                "selection_rationale": "Otopeni = zona aeroport, cerere locala puternica.",
                "gsc_data": None,
            },
            {
                "url": "/petreceri/popesti-leordeni",
                "suggested_strategy": "services_list",
                "selection_rationale": "Zona Sector 4, familii tinere. services_list netestata inca.",
                "gsc_data": None,
            },
            {
                "url": "/petreceri/chitila",
                "suggested_strategy": "benefits_first",
                "selection_rationale": "Zona rezidentiala in expansiune, familii ce cauta valoare.",
                "gsc_data": None,
            },
            {
                "url": "/petreceri/bragadiru",
                "suggested_strategy": "price_first",
                "selection_rationale": "Zona sensibila la pret, potrivita pentru price_first.",
                "gsc_data": None,
            },
            {
                "url": "/petreceri/buftea",
                "suggested_strategy": "local_intent",
                "selection_rationale": "Oras cu identitate locala puternica.",
                "gsc_data": None,
            },
        ]

    # ── Meta Description ─────────────────────────────────────────────────────

    def extract_meta_description(self, url_path: str) -> Optional[str]:
        """
        Citeste meta description din fisierul .astro corespunzator URL-ului.

        Suporta pattern:
          /petreceri/voluntari -> src/pages/petreceri/voluntari.astro
          /petreceri/voluntari/index.astro
        """
        normalized = url_path.strip("/")
        candidates = [
            self._root / "src" / "pages" / (normalized + ".astro"),
            self._root / "src" / "pages" / normalized / "index.astro",
        ]

        for f in candidates:
            if f.exists():
                text = f.read_text(encoding="utf-8", errors="ignore")
                # Match description="..." sau description=`...`
                m = re.search(r'description=["\`]([^"\'`\n]{10,300})["\`]', text)
                if m:
                    return m.group(1).strip()
        return None

    def patch_meta_description(self, url_path: str, new_description: str) -> dict:
        """
        Patch meta description în fișierul .astro al URL-ului.
        Suportă atât description="..." cât și description=`...`.

        NOTA: Nu scrie în dry_run mode.
        """
        normalized = url_path.strip("/")
        candidates = [
            self._root / "src" / "pages" / (normalized + ".astro"),
            self._root / "src" / "pages" / normalized / "index.astro",
        ]

        for f in candidates:
            if not f.exists():
                continue
            original = f.read_text(encoding="utf-8", errors="ignore")
            # Replace description="..." sau description=`...`
            pattern = re.compile(r'(description=)["\`]([^"\'`\n]{10,300})["\`]')
            if not pattern.search(original):
                return {"success": False, "error": "description_field_not_found", "patched_file": str(f)}

            new_content = pattern.sub(f'\\1"{new_description}"', original, count=1)
            f.write_text(new_content, encoding="utf-8")
            return {
                "success": True,
                "backup_content": original,
                "patched_file": str(f),
                "error": None,
            }

        return {"success": False, "error": "file_not_found", "patched_file": None}

    # ── Cooldown ─────────────────────────────────────────────────────────────

    @property
    def min_reapply_days(self) -> int:
        if self.cooldown_config_path.exists():
            with open(self.cooldown_config_path, encoding="utf-8") as f:
                cfg = json.load(f)
            return cfg.get("min_reapply_days", 7)
        return 7
