"""
owner_mapper.py — Head-term → Owner Page mapping and management.

Handles:
  - Loading existing owner mappings from Supabase
  - Validating owner assignments (no duplicates across sites)
  - Seeding initial data for SP/AN/WP
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

log = logging.getLogger("seo_agent.owner_mapper")


# ── Seed Data ────────────────────────────────────────────────────────────────

# Known owner assignments (source of truth for initial seeding)
SEED_OWNERS = [
    {
        "domain": "superparty.ro",
        "head_term": "animatori petreceri copii",
        "path": "/animatori-petreceri-copii",
        "title": "Animatori petreceri copii București & Ilfov | Superparty (#1) Peste 10.000 de evenimente",
        "h1": "Animatori Petreceri Copii",
    },
    {
        "domain": "animatopia.ro",
        "head_term": "mascote si personaje",
        "path": "/mascote-si-personaje",
        "title": "Mascote și Personaje pentru Petreceri | Animatopia",
        "h1": "Mascote și Personaje",
    },
    {
        "domain": "animatopia.ro",
        "head_term": "petreceri tematice",
        "path": "/petreceri-tematice",
        "title": "Petreceri Tematice pentru Copii | Animatopia",
        "h1": "Petreceri Tematice",
    },
    {
        "domain": "animatopia.ro",
        "head_term": "petreceri acasa",
        "path": "/petreceri-acasa",
        "title": "Petreceri Acasă pentru Copii | Animatopia",
        "h1": "Petreceri Acasă",
    },
    {
        "domain": "wowparty.ro",
        "head_term": "pachete animatori",
        "path": "/pachete",
        "title": "Pachete Animatori Petreceri — Prețuri Clare | WowParty",
        "h1": "Pachete Animatori",
    },
]


@dataclass
class OwnerMapping:
    """A resolved owner mapping."""
    domain: str
    head_term: str
    path: str
    title: str
    h1: str
    site_id: Optional[str] = None
    head_term_id: Optional[str] = None
    owner_page_id: Optional[str] = None


class OwnerMapper:
    """
    Manages head-term → owner page mappings.
    
    Can operate in two modes:
      - Live: backed by Supabase
      - Local: backed by in-memory seed data (for testing)
    """

    def __init__(self, supabase_client=None):
        self._db = supabase_client
        self._local_cache: dict[str, OwnerMapping] = {}

        # Always load seed data into local cache
        for seed in SEED_OWNERS:
            key = f"{seed['domain']}:{seed['head_term']}"
            self._local_cache[key] = OwnerMapping(**seed)

    def get_owner(self, head_term: str) -> Optional[OwnerMapping]:
        """Get the owner mapping for a head-term (across all sites)."""
        for key, mapping in self._local_cache.items():
            if mapping.head_term == head_term:
                return mapping
        return None

    def get_owner_for_site(self, domain: str, head_term: str) -> Optional[OwnerMapping]:
        """Get the owner mapping for a specific site + head-term."""
        key = f"{domain}:{head_term}"
        return self._local_cache.get(key)

    def get_all_owners_for_term(self, head_term: str) -> list[OwnerMapping]:
        """Get ALL owners for a term across all sites."""
        results = []
        for key, mapping in self._local_cache.items():
            if mapping.head_term == head_term:
                results.append(mapping)
        return results

    def get_all_owners_for_site(self, domain: str) -> list[OwnerMapping]:
        """Get all owner mappings for a specific site."""
        results = []
        for key, mapping in self._local_cache.items():
            if mapping.domain == domain:
                results.append(mapping)
        return results

    def is_term_owned(self, head_term: str) -> bool:
        """Check if a head-term already has an owner."""
        return self.get_owner(head_term) is not None

    def is_term_owned_by_other(self, head_term: str, exclude_domain: str) -> bool:
        """Check if a head-term is owned by a site OTHER than exclude_domain."""
        owners = self.get_all_owners_for_term(head_term)
        return any(o.domain != exclude_domain for o in owners)

    def register_owner(
        self,
        domain: str,
        head_term: str,
        path: str,
        title: str,
        h1: str,
    ) -> tuple[bool, str]:
        """
        Register a new owner mapping.
        Returns (success, message).
        Fails if term is already owned by another site.
        """
        if self.is_term_owned_by_other(head_term, domain):
            existing = self.get_owner(head_term)
            return False, (
                f"Cannot register — '{head_term}' is already owned by "
                f"{existing.domain} at {existing.path}"
            )

        key = f"{domain}:{head_term}"
        self._local_cache[key] = OwnerMapping(
            domain=domain,
            head_term=head_term,
            path=path,
            title=title,
            h1=h1,
        )
        log.info(f"Registered owner: {domain}{path} for '{head_term}'")
        return True, f"Owner registered: {domain}{path}"

    def get_ownership_report(self) -> list[dict]:
        """Generate a report of all owner assignments."""
        report = []
        for key, mapping in sorted(self._local_cache.items()):
            report.append({
                "domain": mapping.domain,
                "head_term": mapping.head_term,
                "path": mapping.path,
                "title": mapping.title,
                "h1": mapping.h1,
            })
        return report

    def validate_no_conflicts(self) -> list[str]:
        """
        Check for conflicts: multiple sites owning the same head-term.
        Returns list of conflict descriptions (empty = no conflicts).
        """
        term_owners: dict[str, list[str]] = {}
        for key, mapping in self._local_cache.items():
            term = mapping.head_term
            if term not in term_owners:
                term_owners[term] = []
            term_owners[term].append(mapping.domain)

        conflicts = []
        for term, domains in term_owners.items():
            if len(set(domains)) > 1:
                conflicts.append(
                    f"CONFLICT: '{term}' is owned by multiple sites: {', '.join(domains)}"
                )

        return conflicts
