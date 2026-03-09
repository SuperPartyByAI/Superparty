"""
core/site_adapter.py — SiteAdapter ABC

Interfața abstractă pe care fiecare adapter de site trebuie să o implementeze.
Engine-ul core folosește exclusiv această interfață — nu știe nimic despre
SuperParty, Animatopia sau orice alt site.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class SiteAdapter(ABC):
    """
    Contract obligatoriu pentru orice site integrat cu seo-control-plane.

    Implementează toate metodele abstract pentru a putea folosi engine-ul.
    """

    # ── Identity ────────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def site_id(self) -> str:
        """Identificator unic pentru site, ex: 'superparty', 'animatopia'."""

    @property
    @abstractmethod
    def site_domain(self) -> str:
        """Domeniu principal, ex: 'https://www.superparty.ro'."""

    # ── Paths ───────────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def reports_dir(self) -> Path:
        """Directorul unde se salveaza artefactele (outcome memory, status, etc.)."""

    @property
    @abstractmethod
    def config_dir(self) -> Path:
        """Directorul cu configuratia specifica site-ului (policy, pillar registry, etc.)."""

    # ── Path Classification ─────────────────────────────────────────────────

    @abstractmethod
    def is_pillar_page(self, url_path: str) -> bool:
        """
        True daca URL-ul este o pagina 'pillar' (Tier A) — nu poate fi modificata.

        Args:
          url_path: calea relativa, ex: '/animatori-petreceri-copii'
        """

    @abstractmethod
    def is_money_page(self, url_path: str) -> bool:
        """
        True daca URL-ul este o pagina comerciala importanta (Tier B) — blocata.

        Args:
          url_path: calea relativa, ex: '/servicii/pachet-premium'
        """

    @abstractmethod
    def is_tier_c_eligible(self, url_path: str) -> bool:
        """
        True daca URL-ul este eligibil pentru experimente L6 (Tier C).

        Nota: trebuie sa returneze False daca is_pillar_page sau is_money_page.

        Args:
          url_path: calea relativa, ex: '/petreceri/voluntari'
        """

    @abstractmethod
    def get_page_type(self, url_path: str) -> str:
        """
        Returneaza tipul de pagina: 'pillar', 'money', 'tier_c', 'blocked', 'unknown'.
        """

    # ── Tier C Catalog ──────────────────────────────────────────────────────

    @abstractmethod
    def get_tier_c_catalog(self) -> list[dict]:
        """
        Lista de pagini Tier C candidate pentru Run 2.

        Fiecare dict trebuie sa contina:
          url: str
          suggested_strategy: str
          selection_rationale: str
          gsc_data: Optional[dict]  (None daca nu exista)
        """

    # ── Meta Description ────────────────────────────────────────────────────

    @abstractmethod
    def extract_meta_description(self, url_path: str) -> Optional[str]:
        """
        Citeste meta description curenta pentru un URL.

        Returneaza None daca nu poate fi citita.
        """

    @abstractmethod
    def patch_meta_description(self, url_path: str, new_description: str) -> dict:
        """
        Scrie noua meta description pentru un URL.

        Returneaza dict cu:
          success: bool
          backup_content: str  (continutul anterior — pentru rollback)
          patched_file: str
          error: Optional[str]

        NOTA: In mod read-only / dry-run, nu se scrie nimic.
        """

    # ── Cooldown & Policy ───────────────────────────────────────────────────

    @property
    def min_reapply_days(self) -> int:
        """Numarul minim de zile cooldown intre apply-uri pe acelasi URL."""
        return 7

    @property
    def max_experiments_concurrent(self) -> int:
        """Numarul maxim de experimente active simultan."""
        return 3

    @property
    def min_impressions_for_scoring(self) -> int:
        """Numarul minim de impresii GSC pentru a putea judeca CTR."""
        return 80

    # ── Helpers (opționale, cu implementare implicita) ─────────────────────

    def normalize_url(self, url: str) -> str:
        """Normalizeaza un URL la forma /path (fara domeniu, fara trailing slash)."""
        import re
        url = url.strip()
        # Strip domain
        domain_pattern = re.compile(r"^https?://[^/]+")
        url = domain_pattern.sub("", url)
        url = url.rstrip("/") or "/"
        if not url.startswith("/"):
            url = "/" + url
        return url

    def is_blocked(self, url_path: str) -> tuple[bool, list[str]]:
        """
        Verifica daca un URL este blocat si returneaza motivele.

        Returns: (blocked: bool, reasons: list[str])
        """
        reasons = []
        if self.is_pillar_page(url_path):
            reasons.append("pillar_page")
        if self.is_money_page(url_path):
            reasons.append("money_page")
        return len(reasons) > 0, reasons

    def describe(self) -> dict:
        """Returneaza un dict cu informatiile despre adapter."""
        return {
            "site_id": self.site_id,
            "site_domain": self.site_domain,
            "reports_dir": str(self.reports_dir),
            "config_dir": str(self.config_dir),
            "min_reapply_days": self.min_reapply_days,
            "max_experiments_concurrent": self.max_experiments_concurrent,
            "min_impressions_for_scoring": self.min_impressions_for_scoring,
        }
