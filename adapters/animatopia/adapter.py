"""
adapters/animatopia/adapter.py — AnimatopiaAdapter

Adapter pentru Animatopia (animatopia.ro).
Implementează SiteAdapter cu regulile proprii site-ului editorial.

Reguli confirmate:
  / → pillar, blocat
  /articole (index) → pillar, blocat
  /despre → blocat
  /contact → blocat
  /servicii/* → money/B, blocat
  /articole/[slug] → Tier C, DAR cu guard pentru articole prea comerciale
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from core.site_adapter import SiteAdapter

_DEFAULT_AT_ROOT = Path(__file__).parent.parent.parent.parent / "Animatopia"

# ─── Cuvinte-cheie care indică intenție comercială puternică ─────────────────
# Dacă meta description SAU titlul articolului conțin prea mulți termeni comerciali,
# articolul este tratat ca money-like și exclus din Tier C.
COMMERCIAL_SIGNALS = [
    "preț", "pret", "tarif", "tarife", "ofertă", "oferta",
    "commandă", "comanda", "rezervă", "rezerva",
    "pachet", "pachete", "cumpără", "cumpara",
    "discount", "reducere", "promotie", "promotie",
    "comandati", "comandați",
]

EDITORIAL_SIGNALS = [
    "cum", "ghid", "sfat", "sfaturi", "idei", "inspiratie",
    "inspirație", "activitate", "activitati", "activități",
    "creative", "distractiv", "copii", "parinti", "părinți",
    "organizare", "jocuri", "joc",
]

COMMERCIAL_THRESHOLD = 3   # câte semnale comerciale → money-like
EDITORIAL_THRESHOLD = 2    # câte semnale editoriale → editorial clar


class AnimatopiaAdapter(SiteAdapter):
    """
    Adapter pentru Animatopia (animatopia.ro).

    Site editorial cu blog de articole pentru părinți.
    Structura: home / articole / servicii / despre / contact.
    """

    def __init__(self, animatopia_root: Optional[Path] = None):
        self._root = Path(animatopia_root) if animatopia_root else _DEFAULT_AT_ROOT

    # ── Identity ────────────────────────────────────────────────────────────

    @property
    def site_id(self) -> str:
        return "animatopia"

    @property
    def site_domain(self) -> str:
        return "https://www.animatopia.ro"

    # ── Paths ───────────────────────────────────────────────────────────────

    @property
    def reports_dir(self) -> Path:
        return self._root / "reports" / "animatopia"

    @property
    def config_dir(self) -> Path:
        return self._root / "config" / "seo"

    # ── Pillar Pages ─────────────────────────────────────────────────────────

    PILLAR_EXACT = {"/", "/articole", "/blog", "/despre", "/contact", "/about"}
    PILLAR_PREFIXES = ["/articole/page/", "/blog/page/"]  # paginare = pillar

    def is_pillar_page(self, url_path: str) -> bool:
        normalized = url_path.rstrip("/") or "/"
        if normalized in self.PILLAR_EXACT:
            return True
        return any(normalized.startswith(p) for p in self.PILLAR_PREFIXES)

    # ── Money Pages ──────────────────────────────────────────────────────────

    MONEY_PATTERNS = [
        re.compile(r"^/servicii/?"),
        re.compile(r"^/pachete/?"),
        re.compile(r"^/comanda/?"),
        re.compile(r"^/rezerva/?"),
        re.compile(r"^/oferta/?"),
    ]

    def is_money_page(self, url_path: str) -> bool:
        normalized = url_path.rstrip("/") or "/"
        return any(p.match(normalized) for p in self.MONEY_PATTERNS)

    # ── Editorial Article Guard ───────────────────────────────────────────────

    def _score_article_intent(self, url_path: str) -> dict:
        """
        Analizează URL-ul + conținutul articolului și determină dacă e:
          - 'editorial' = conținut de valoare, eligibil Tier C
          - 'money_like' = tratat ca pagina comercială, blocat
          - 'unknown' = nu se poate determina (implicit editorial dacă path ok)
        """
        text = self._read_article_text(url_path)
        if not text:
            return {"intent": "unknown", "commercial_score": 0, "editorial_score": 0}

        text_lower = text.lower()

        commercial_score = sum(1 for sig in COMMERCIAL_SIGNALS if sig in text_lower)
        editorial_score = sum(1 for sig in EDITORIAL_SIGNALS if sig in text_lower)

        if commercial_score >= COMMERCIAL_THRESHOLD and editorial_score < EDITORIAL_THRESHOLD:
            intent = "money_like"
        elif commercial_score >= COMMERCIAL_THRESHOLD and editorial_score >= EDITORIAL_THRESHOLD:
            # Mix: mai multă cautela — blocat dacă commercial >> editorial
            intent = "money_like" if commercial_score > editorial_score * 1.5 else "editorial"
        else:
            intent = "editorial"

        return {
            "intent": intent,
            "commercial_score": commercial_score,
            "editorial_score": editorial_score,
        }

    def is_editorial_article(self, url_path: str) -> bool:
        """True dacă articolul este editorial (nu comercial mascat)."""
        analysis = self._score_article_intent(url_path)
        return analysis["intent"] in ("editorial", "unknown")

    def is_money_like_article(self, url_path: str) -> bool:
        """True dacă articolul este tratat ca money-like (exclus Tier C)."""
        analysis = self._score_article_intent(url_path)
        return analysis["intent"] == "money_like"

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
        Tier C Animatopia: /articole/[slug] care sunt editoriale.

        Exclude:
          - pillar pages
          - money pages
          - money-like articles
          - slug-uri care nu sunt articole (ex: /articole/page/2)
        """
        if self.is_pillar_page(url_path) or self.is_money_page(url_path):
            return False

        # Trebuie să fie un slug de articol
        if not re.match(r"^/articole/[a-z0-9\-]{3,}/?$", url_path):
            return False

        # Guard: verifică dacă e editorial (doar dacă fișierul există)
        if self.is_money_like_article(url_path):
            return False

        return True

    # ── Tier C Catalog ───────────────────────────────────────────────────────

    def get_tier_c_catalog(self) -> list[dict]:
        """
        Catalog Tier C Animatopia.
        Populat dinamic dacă există articole, sau cu placeholder read-only.
        """
        catalog = []
        articles_dir = self._root / "src" / "content" / "articole"
        if not articles_dir.exists():
            articles_dir = self._root / "src" / "pages" / "articole"

        if articles_dir.exists():
            for f in articles_dir.glob("*.md"):
                url = f"/articole/{f.stem}"
                analysis = self._score_article_intent(url)
                if analysis["intent"] in ("editorial", "unknown"):
                    catalog.append({
                        "url": url,
                        "suggested_strategy": "benefits_first",
                        "selection_rationale": f"Articol editorial detectat: {f.name}",
                        "gsc_data": None,
                        "article_intent": analysis["intent"],
                        "commercial_score": analysis["commercial_score"],
                        "editorial_score": analysis["editorial_score"],
                    })
        return catalog

    # ── Meta Description ─────────────────────────────────────────────────────

    def _read_article_text(self, url_path: str) -> Optional[str]:
        """Citeste continutul unui articol din diferite locatii possible."""
        slug = url_path.strip("/").replace("articole/", "")
        candidates = [
            self._root / "src" / "content" / "articole" / (slug + ".md"),
            self._root / "src" / "pages" / "articole" / (slug + ".md"),
            self._root / "src" / "pages" / "articole" / (slug + ".astro"),
            self._root / "src" / "pages" / "articole" / slug / "index.md",
            self._root / "src" / "pages" / "articole" / slug / "index.astro",
        ]
        for f in candidates:
            if f.exists():
                return f.read_text(encoding="utf-8", errors="ignore")
        return None

    def extract_meta_description(self, url_path: str) -> Optional[str]:
        """
        Citeste meta description din frontmatter YAML al articolului.

        Suportă:
          description: "..."  (YAML frontmatter .md)
          description="..."   (Astro component)
        """
        text = self._read_article_text(url_path)
        if not text:
            return None

        # YAML frontmatter: description: "..." sau description: |
        m = re.search(r'^description:\s*["\']?([^\n"\']{10,300})["\']?', text, re.MULTILINE)
        if m:
            return m.group(1).strip()

        # Astro prop: description="..."
        m = re.search(r'description=["\`]([^"\'`\n]{10,300})["\`]', text)
        if m:
            return m.group(1).strip()

        return None

    def patch_meta_description(self, url_path: str, new_description: str) -> dict:
        """
        Patch meta description în frontmatter YAML al articolului.

        Suporta .md cu YAML frontmatter.
        """
        slug = url_path.strip("/").replace("articole/", "")
        candidates = [
            self._root / "src" / "content" / "articole" / (slug + ".md"),
            self._root / "src" / "pages" / "articole" / (slug + ".md"),
        ]

        for f in candidates:
            if not f.exists():
                continue
            original = f.read_text(encoding="utf-8", errors="ignore")

            pattern = re.compile(r"^(description:\s*)['\"]?([^\n\"']{10,300})['\"]?$", re.MULTILINE)
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

        # .astro fallback
        for f in [
            self._root / "src" / "pages" / "articole" / (slug + ".astro"),
            self._root / "src" / "pages" / "articole" / slug / "index.astro",
        ]:
            if not f.exists():
                continue
            original = f.read_text(encoding="utf-8", errors="ignore")
            pattern = re.compile(r'(description=)["\`]([^"\'`\n]{10,300})["\`]')
            if not pattern.search(original):
                return {"success": False, "error": "description_field_not_found", "patched_file": str(f)}
            new_content = pattern.sub(f'\\1"{new_description}"', original, count=1)
            f.write_text(new_content, encoding="utf-8")
            return {"success": True, "backup_content": original, "patched_file": str(f), "error": None}

        return {"success": False, "error": "file_not_found", "patched_file": None}
