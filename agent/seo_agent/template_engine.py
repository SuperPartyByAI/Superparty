"""
template_engine.py — Parametric JSON-LD and meta tag generator.

Produces validated structured data for owner pages:
  - LocalBusiness
  - OfferCatalog  
  - FAQPage
  - AggregateRating
  - BreadcrumbList

Also generates optimized meta title + description.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger("seo_agent.templates")


@dataclass
class PackageOffer:
    """A service package/offer."""
    name: str
    price: str
    currency: str = "RON"
    description: str = ""


@dataclass
class FAQItem:
    """A FAQ question + answer pair."""
    question: str
    answer: str


@dataclass
class OwnerPageData:
    """All data needed to generate templates for an owner page."""
    brand: str
    domain: str
    path: str
    phone: str
    head_term: str
    h1: str
    city: str = "București"
    area: str = "Ilfov"
    rating: str = "5.0"
    review_count: str = "1498"
    event_count: str = "10.000+"
    packages: list[PackageOffer] = field(default_factory=list)
    faqs: list[FAQItem] = field(default_factory=list)
    meta_title: str = ""
    meta_description: str = ""


# ── JSON-LD Generators ───────────────────────────────────────────────────────

def generate_local_business(data: OwnerPageData) -> dict:
    """Generate LocalBusiness JSON-LD."""
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": data.brand,
        "url": f"https://www.{data.domain}{data.path}",
        "description": (
            f"{data.head_term.capitalize()} în {data.city} și {data.area} — "
            f"personaje costumate, jocuri interactive, pictură pe față, confetti party. "
            f"{data.event_count} evenimente."
        ),
        "telephone": data.phone,
        "areaServed": [
            {"@type": "City", "name": data.city},
            {"@type": "AdministrativeArea", "name": data.area},
        ],
    }

    if data.rating and data.review_count:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": data.rating,
            "reviewCount": data.review_count,
        }

    if data.packages:
        price_min = min(data.packages, key=lambda p: int(p.price)).price
        price_max = max(data.packages, key=lambda p: int(p.price)).price
        schema["priceRange"] = f"{price_min}-{price_max} {data.packages[0].currency}"

    return schema


def generate_offer_catalog(data: OwnerPageData) -> Optional[dict]:
    """Generate OfferCatalog JSON-LD (only if packages exist)."""
    if not data.packages:
        return None

    return {
        "@type": "OfferCatalog",
        "name": f"Pachete {data.head_term.capitalize()}",
        "itemListElement": [
            {
                "@type": "Offer",
                "name": pkg.name,
                "price": pkg.price,
                "priceCurrency": pkg.currency,
                "description": pkg.description,
            }
            for pkg in data.packages
        ],
    }


def generate_faq_page(data: OwnerPageData) -> Optional[dict]:
    """Generate FAQPage JSON-LD (only if FAQs exist)."""
    if not data.faqs:
        return None

    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq.question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.answer,
                },
            }
            for faq in data.faqs
        ],
    }


def generate_breadcrumb(data: OwnerPageData) -> dict:
    """Generate BreadcrumbList JSON-LD."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": data.brand,
                "item": f"https://www.{data.domain}/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": data.h1,
                "item": f"https://www.{data.domain}{data.path}",
            },
        ],
    }


# ── Combined JSON-LD ─────────────────────────────────────────────────────────

def generate_combined_jsonld(data: OwnerPageData) -> str:
    """
    Generate combined JSON-LD array with all applicable schemas.
    Returns a JSON string ready for <script type="application/ld+json">.
    """
    schemas = []

    # LocalBusiness (always)
    lb = generate_local_business(data)

    # Attach OfferCatalog to LocalBusiness if packages exist
    offers = generate_offer_catalog(data)
    if offers:
        lb["hasOfferCatalog"] = offers

    schemas.append(lb)

    # FAQPage (if FAQs exist)
    faq = generate_faq_page(data)
    if faq:
        schemas.append(faq)

    # Breadcrumb (always)
    schemas.append(generate_breadcrumb(data))

    return json.dumps(schemas, ensure_ascii=False, indent=2)


# ── Meta Tag Generators ──────────────────────────────────────────────────────

def generate_meta_title(data: OwnerPageData) -> str:
    """
    Generate SEO-optimized meta title.
    Format: {Head Term} {City} & {Area} | {Brand} (#1) Peste {events} evenimente
    Max ~60 chars displayed, but can be longer.
    """
    if data.meta_title:
        return data.meta_title

    return (
        f"{data.head_term.capitalize()} {data.city} & {data.area} | "
        f"{data.brand} (#1) Peste {data.event_count} evenimente"
    )


def generate_meta_description(data: OwnerPageData) -> str:
    """
    Generate CTR-optimized meta description.
    Includes: head-term, brand, features, price, rating, CTA.
    Max ~155 chars displayed.
    """
    if data.meta_description:
        return data.meta_description

    price_part = ""
    if data.packages:
        min_price = min(data.packages, key=lambda p: int(p.price)).price
        price_part = f" De la {min_price} lei."

    return (
        f"{data.head_term.capitalize()} {data.city} — {data.brand}: "
        f"personaje costumate, jocuri interactive, confetti party."
        f"{price_part} {data.event_count} evenimente, "
        f"rating {data.rating} ⭐. Sună: {data.phone}"
    )


# ── Astro Component Snippet ──────────────────────────────────────────────────

def generate_astro_frontmatter_snippet(data: OwnerPageData) -> str:
    """
    Generate the Astro frontmatter JavaScript for combined JSON-LD schema.
    This can be pasted into the --- block of an .astro file.
    """
    jsonld = generate_combined_jsonld(data)
    return f"const combinedSchema = JSON.stringify({jsonld});"


def generate_internal_link_html(
    target_path: str,
    anchor_text: str,
    context_text: str = "",
) -> str:
    """Generate an HTML internal link snippet."""
    link = f'<a href="{target_path}" style="color:var(--primary); font-weight:600;">{anchor_text}</a>'
    if context_text:
        return f'<p style="color:var(--text-muted); font-size:0.95rem; margin-top:1.5rem;">{context_text} {link}</p>'
    return link


# ── Validation ───────────────────────────────────────────────────────────────

def validate_jsonld(jsonld_str: str) -> tuple[bool, list[str]]:
    """
    Basic validation of JSON-LD structure.
    Returns (valid, errors).
    """
    errors = []

    try:
        data = json.loads(jsonld_str)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    if isinstance(data, list):
        schemas = data
    elif isinstance(data, dict):
        schemas = [data]
    else:
        return False, ["JSON-LD must be object or array"]

    for i, schema in enumerate(schemas):
        if "@type" not in schema:
            errors.append(f"Schema [{i}]: missing @type")
        if "@context" not in schema and i == 0:
            # First schema should have @context
            pass  # nested schemas may not need it

        schema_type = schema.get("@type", "")

        if schema_type == "LocalBusiness":
            for field in ["name", "url", "telephone"]:
                if field not in schema:
                    errors.append(f"LocalBusiness: missing required field '{field}'")

        elif schema_type == "FAQPage":
            if "mainEntity" not in schema:
                errors.append("FAQPage: missing 'mainEntity'")
            else:
                for j, q in enumerate(schema["mainEntity"]):
                    if "name" not in q:
                        errors.append(f"FAQ Q[{j}]: missing 'name'")
                    if "acceptedAnswer" not in q:
                        errors.append(f"FAQ Q[{j}]: missing 'acceptedAnswer'")

        elif schema_type == "BreadcrumbList":
            if "itemListElement" not in schema:
                errors.append("BreadcrumbList: missing 'itemListElement'")

    return len(errors) == 0, errors
