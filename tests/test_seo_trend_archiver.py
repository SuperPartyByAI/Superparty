"""
Tests for seo_trend_archiver.py — Level 4.1 PR #51
"""
import json
import pytest
from pathlib import Path
from datetime import date
import agent.tasks.seo_trend_archiver as archiver_module
from agent.tasks.seo_trend_archiver import archive_snapshots, get_latest_snapshot_dates


# ─── Fixtures ────────────────────────────────────────────────────────────────

def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


@pytest.fixture
def fake_reports_dir(tmp_path, monkeypatch):
    """
    Patches REPORTS_DIR and HISTORY_DIR to use tmp_path.
    Writes 2 source files, leaves seo_gap_opportunities.json missing.
    """
    reports = tmp_path / "reports" / "superparty"
    reports.mkdir(parents=True)
    history = reports / "history"
    history.mkdir()

    _write_json(reports / "seo_cluster_health.json", {
        "metadata": {"generated_at": "2026-03-07T10:00:00Z"},
        "clusters": {}
    })
    _write_json(reports / "seo_cluster_priority.json", {
        "metadata": {"priority_generated_at": "2026-03-07T10:01:00Z"},
        "clusters": {}
    })
    # seo_gap_opportunities.json is intentionally missing to test graceful handling

    monkeypatch.setattr(archiver_module, "REPORTS_DIR", reports)
    monkeypatch.setattr(archiver_module, "HISTORY_DIR", history)
    return {"reports": reports, "history": history}


# ─── Tests ────────────────────────────────────────────────────────────────────

def test_archive_creates_dated_folder(fake_reports_dir):
    """Archiver trebuie să creeze folderul history/YYYY-MM-DD/."""
    result = archive_snapshots(snapshot_date="2026-03-07")
    dated_dir = fake_reports_dir["history"] / "2026-03-07"
    assert dated_dir.is_dir(), "Folderul history/2026-03-07 trebuie creat"


def test_archive_copies_existing_files(fake_reports_dir):
    """Fișierele prezente sunt copiate; cel lipsă apare în 'missing'."""
    result = archive_snapshots(snapshot_date="2026-03-07")
    dated_dir = fake_reports_dir["history"] / "2026-03-07"

    assert (dated_dir / "seo_cluster_health.json").exists()
    assert (dated_dir / "seo_cluster_priority.json").exists()
    assert not (dated_dir / "seo_gap_opportunities.json").exists()

    assert "seo_cluster_health.json" in [a["file"] for a in result["archived"]]
    assert "seo_gap_opportunities.json" in result["missing"]


def test_archive_writes_snapshot_manifest(fake_reports_dir):
    """snapshot_manifest.json trebuie scris cu metadata corecte."""
    result = archive_snapshots(snapshot_date="2026-03-07")
    manifest_path = fake_reports_dir["history"] / "2026-03-07" / "snapshot_manifest.json"
    assert manifest_path.exists()

    with open(manifest_path) as f:
        manifest = json.load(f)

    assert manifest["snapshot_date"] == "2026-03-07"
    assert manifest["mode"] == "read_only"
    assert isinstance(manifest["archived"], list)
    assert isinstance(manifest["missing"], list)


def test_archive_overwrite_same_day(fake_reports_dir):
    """Re-rulare pe aceeași zi suprascrie controlat fără eroare."""
    archive_snapshots(snapshot_date="2026-03-07")
    archive_snapshots(snapshot_date="2026-03-07")  # trebuie să nu arunce excepție
    dated_dir = fake_reports_dir["history"] / "2026-03-07"
    assert dated_dir.is_dir()


def test_get_latest_snapshot_dates_empty(fake_reports_dir):
    """Fără niciun snapshot, lista trebuie să fie goală."""
    result = get_latest_snapshot_dates()
    assert result == []


def test_get_latest_snapshot_dates_after_archive(fake_reports_dir):
    """După arhivare, data apare în lista de snapshot-uri."""
    archive_snapshots(snapshot_date="2026-03-07")
    dates = get_latest_snapshot_dates()
    assert "2026-03-07" in dates


def test_archive_graceful_when_all_sources_missing(fake_reports_dir):
    """Dacă niciun fișier sursă nu există, archiver-ul iese curat fără crash."""
    # Șterg fișierele create de fixture
    (fake_reports_dir["reports"] / "seo_cluster_health.json").unlink()
    (fake_reports_dir["reports"] / "seo_cluster_priority.json").unlink()

    result = archive_snapshots(snapshot_date="2026-03-07")
    assert len(result["archived"]) == 0
    assert len(result["missing"]) == 3  # toate 3 surse lipsesc
