"""
agent/tasks/seo_level6_gsc_ingestion.py

GSC Export Ingestion Tool — L6 Learning Loop

Citește exporturi CSV sau JSON din Google Search Console și populează
outcome memory cu date reale pentru scoring L6.

Formate suportate:
  - CSV export din GSC Performance > Pages
    (coloane: page, clicks, impressions, ctr, position)
  - JSON cu schema: {"rows": [{"keys":[url], "clicks":N, "impressions":N, "ctr":F, "position":F}]}

Nu inventează metrici. Dacă URL-ul lipsește din export → insufficient_data explicit.
Nu modifică paginile din Run 1 — doar actualizează outcome memory.
"""
from __future__ import annotations

import csv
import io
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent

# Mapping site domain → normalizare
SITE_DOMAIN = "https://www.superparty.ro"
SITE_DOMAIN_VARIANTS = [
    "https://www.superparty.ro",
    "https://superparty.ro",
    "http://www.superparty.ro",
    "http://superparty.ro",
]


def normalize_url(raw_url: str) -> str:
    """
    Normalizează URL la forma /path (fără domeniu, fără trailing slash).

    Exemple:
      https://www.superparty.ro/petreceri/voluntari → /petreceri/voluntari
      superparty.ro/petreceri/voluntari             → /petreceri/voluntari
      /petreceri/voluntari/                         → /petreceri/voluntari
    """
    url = raw_url.strip()
    for domain in SITE_DOMAIN_VARIANTS:
        if url.startswith(domain):
            url = url[len(domain):]
            break
    # Elimina domeniu fara protocol (ex: superparty.ro/pagina)
    url = re.sub(r"^https?://[^/]+", "", url)
    # Trailing slash (dar pastreaza root /)
    url = url.rstrip("/") or "/"
    # Asigura ca incepe cu /
    if not url.startswith("/"):
        url = "/" + url
    return url


def _parse_ctr(value) -> Optional[float]:
    """Acceptă '5.23%', 0.0523, '0.0523'."""
    if value is None or value == "":
        return None
    if isinstance(value, float):
        return value
    s = str(value).strip().replace("%", "")
    try:
        f = float(s)
        # Dacă e exprimat ca procent (> 1), convertim la 0-1
        return f / 100.0 if f > 1.0 else f
    except ValueError:
        return None


def _parse_int(value) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (ValueError, TypeError):
        return None


def _parse_float(value) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def parse_gsc_csv(content: str) -> list[dict]:
    """
    Parsează un CSV export din GSC Performance > Pages.

    Coloane așteptate (case-insensitive, ordine flexibilă):
      page | clicks | impressions | ctr | position

    Returnează list[dict] cu chei normalizate.
    """
    reader = csv.DictReader(io.StringIO(content.strip()))
    results = []

    # Normalizare coloane (GSC exportă cu litere mici)
    col_map = {}
    if reader.fieldnames:
        for field in reader.fieldnames:
            key = field.strip().lower().replace(" ", "_").replace("-", "_")
            col_map[field] = key

    for row in reader:
        normalized_row = {col_map.get(k, k): v for k, v in row.items()}

        # Detectează coloana URL
        url_raw = (
            normalized_row.get("page")
            or normalized_row.get("url")
            or normalized_row.get("top_pages")
            or normalized_row.get("pages")
            or ""
        )
        if not url_raw:
            continue

        results.append({
            "url": normalize_url(url_raw),
            "url_raw": url_raw.strip(),
            "impressions": _parse_int(normalized_row.get("impressions")),
            "clicks": _parse_int(normalized_row.get("clicks")),
            "ctr": _parse_ctr(normalized_row.get("ctr")),
            "position": _parse_float(
                normalized_row.get("position") or normalized_row.get("average_position")
            ),
        })

    return results


def parse_gsc_json(content: str) -> list[dict]:
    """
    Parsează un JSON cu schema GSC API:
      {"rows": [{"keys": ["url"], "impressions": N, "clicks": N, "ctr": F, "position": F}]}
    Sau lista directă: [{"keys": [...], ...}]
    """
    data = json.loads(content)
    if isinstance(data, dict):
        rows = data.get("rows", [])
    elif isinstance(data, list):
        rows = data
    else:
        return []

    results = []
    for row in rows:
        keys = row.get("keys", [])
        url_raw = keys[0] if keys else row.get("page", row.get("url", ""))
        if not url_raw:
            continue
        results.append({
            "url": normalize_url(url_raw),
            "url_raw": url_raw,
            "impressions": _parse_int(row.get("impressions")),
            "clicks": _parse_int(row.get("clicks")),
            "ctr": _parse_ctr(row.get("ctr")),
            "position": _parse_float(row.get("position")),
        })

    return results


def parse_gsc_export(content: str, format: str = "auto") -> list[dict]:
    """
    Entry point flexibil: detectează automat CSV sau JSON.

    Args:
      content: continutul fisierului
      format: 'csv', 'json', sau 'auto' (detectie automata)
    """
    if format == "csv":
        return parse_gsc_csv(content)
    if format == "json":
        return parse_gsc_json(content)

    # Auto-detect
    stripped = content.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        return parse_gsc_json(content)
    return parse_gsc_csv(content)


def ingest_gsc_into_outcome_memory(
    gsc_rows: list[dict],
    outcome_memory_path: Path,
    mode: str = "before",
) -> dict:
    """
    Injectează date GSC în outcome memory.

    Args:
      gsc_rows: lista returnata de parse_gsc_export
      outcome_memory_path: calea la seo_level6_outcome_memory.json
      mode: 'before' (date de baseline dinainte de apply) sau 'after' (date post-apply)

    Returns dict cu summary al ingestiei.
    """
    if not outcome_memory_path.exists():
        return {
            "status": "error",
            "reason": "outcome_memory_not_found",
            "injected": [],
            "not_found": [],
            "insufficient_data": [],
        }

    with open(outcome_memory_path, encoding="utf-8") as f:
        experiments = json.load(f)

    # Index GSC by URL
    gsc_by_url = {r["url"]: r for r in gsc_rows}

    injected = []
    not_found = []
    insufficient_data_urls = []

    for exp in experiments:
        url = exp["url"]
        gsc_key = f"gsc_{mode}"

        if url not in gsc_by_url:
            # URL nu apare in export
            not_found.append(url)
            if exp.get(gsc_key) is None or exp.get(gsc_key, {}).get("impressions") is None:
                exp[gsc_key] = {"impressions": None, "ctr": None, "position": None}
            continue

        row = gsc_by_url[url]
        impressions = row.get("impressions")

        # Nu inventam — dacă lipsesc date, marcam explicit
        if impressions is None:
            insufficient_data_urls.append(url)
            exp[gsc_key] = {"impressions": None, "ctr": None, "position": None}
        else:
            exp[gsc_key] = {
                "impressions": impressions,
                "clicks": row.get("clicks"),
                "ctr": row.get("ctr"),
                "position": row.get("position"),
            }
            injected.append(url)

    # Salveaza
    with open(outcome_memory_path, "w", encoding="utf-8") as f:
        json.dump(experiments, f, indent=2, ensure_ascii=False)

    return {
        "status": "ok",
        "mode": mode,
        "injected": injected,
        "not_found": not_found,
        "insufficient_data": insufficient_data_urls,
        "total_gsc_rows": len(gsc_rows),
        "total_experiments": len(experiments),
    }


def run_gsc_ingestion(
    export_file: Path,
    outcome_memory_path: Path,
    mode: str = "after",
    output_report_path: Optional[Path] = None,
) -> dict:
    """
    End-to-end: citeste fisier export GSC + injecteaza in outcome memory.

    Args:
      export_file: calea la fisierul CSV sau JSON
      outcome_memory_path: outcome memory L6
      mode: 'before' sau 'after'
      output_report_path: unde sa scrie raportul JSON (optional)
    """
    content = export_file.read_text(encoding="utf-8")
    suffix = export_file.suffix.lower()
    fmt = "csv" if suffix == ".csv" else ("json" if suffix == ".json" else "auto")

    gsc_rows = parse_gsc_export(content, format=fmt)
    ingestion_result = ingest_gsc_into_outcome_memory(gsc_rows, outcome_memory_path, mode=mode)

    report = {
        "ingestion_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "export_file": str(export_file),
        "format_detected": fmt,
        "mode": mode,
        "gsc_rows_parsed": len(gsc_rows),
        "ingestion_summary": ingestion_result,
    }

    if output_report_path:
        output_report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    return report
