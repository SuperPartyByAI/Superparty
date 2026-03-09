"""
tests/test_seo_level6_learning_loop.py

Suite completa de teste pentru L6 learning loop:
- Strategy tagger (7 strategii + uncategorized)
- Outcome memory (add, update, query, rollback, deadline)
- Scorer (positive/neutral/negative/insufficient_data/strong_negative)
- Experiment engine (max 3, pillar guard, active guard, open/close)
- Observability snapshot (toate artefactele)
"""
import json
import uuid
import pytest
from pathlib import Path
from datetime import datetime, timedelta, timezone

# ── Imports module ─────────────────────────────────────────────────────────────
import agent.tasks.seo_level6_strategy_tagger as tagger_mod
from agent.tasks.seo_level6_strategy_tagger import (
    tag_strategy,
    tag_strategy_explain,
    get_all_strategy_names,
)

import agent.tasks.seo_level6_outcome_memory as memory_mod
from agent.tasks.seo_level6_outcome_memory import (
    add_experiment,
    update_outcome,
    mark_rollback,
    get_all_experiments,
    get_pending,
    get_closed,
    get_by_url,
    get_experiments_past_deadline,
    is_url_in_active_experiment,
)

import agent.tasks.seo_level6_scorer as scorer_mod
from agent.tasks.seo_level6_scorer import (
    score_experiment,
    compute_strategy_scores,
    get_best_strategy,
    MIN_IMPRESSIONS,
    CTR_THRESHOLD,
)

import agent.tasks.seo_level6_experiment_engine as engine_mod
from agent.tasks.seo_level6_experiment_engine import (
    can_open_experiment,
    open_experiment,
    close_expired_experiments,
    inject_gsc_data,
    get_active_experiment_count,
    generate_observability_snapshot,
    MAX_EXPERIMENTS,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _make_experiment(
    url: str = "/test/pagina",
    strategy: str = "local_intent",
    result_label: str = "pending",
    rollback_happened: bool = False,
    applied_days_ago: int = 0,
    observation_window_days: int = 14,
    gsc_before: dict = None,
    gsc_after: dict = None,
) -> dict:
    """Build a synthetic experiment record for testing."""
    now = datetime.now(timezone.utc)
    applied_at = now - timedelta(days=applied_days_ago)
    deadline = applied_at + timedelta(days=observation_window_days)
    return {
        "experiment_id": str(uuid.uuid4()),
        "url": url,
        "applied_at": applied_at.isoformat(),
        "strategy": strategy,
        "proposal_source": "deterministic_fallback",
        "before_meta": "Text vechi.",
        "after_meta": "Text nou optimizat.",
        "observation_window_days": observation_window_days,
        "observation_deadline": deadline.isoformat(),
        "gsc_before": gsc_before or {"impressions": None, "ctr": None, "position": None},
        "gsc_after": gsc_after or {"impressions": None, "ctr": None, "position": None},
        "result_label": result_label,
        "rollback_happened": rollback_happened,
        "closed_at": None if result_label == "pending" else now.isoformat(),
        "score_explanation": None,
    }


@pytest.fixture
def memory_file(tmp_path):
    """Isolated outcome memory file."""
    return tmp_path / "seo_level6_outcome_memory.json"


@pytest.fixture
def pillar_registry_file(tmp_path):
    """Pillar registry with one entry."""
    path = tmp_path / "pillar_pages_registry.json"
    _write_json(path, {
        "schema_version": "1.0",
        "pillar_pages": ["/animatori-petreceri-copii", "/arcade-baloane"],
    })
    return path


@pytest.fixture
def empty_pillar_registry(tmp_path):
    """Empty pillar registry for experiments that should succeed."""
    path = tmp_path / "pillar_pages_registry.json"
    _write_json(path, {"schema_version": "1.0", "pillar_pages": []})
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# 1. STRATEGY TAGGER
# ═══════════════════════════════════════════════════════════════════════════════

class TestStrategyTagger:

    def test_tag_price_first(self):
        text = "Pachete animatori de la 490 lei. Transport gratuit."
        assert tag_strategy(text) == "price_first"

    def test_tag_benefits_first(self):
        text = "Animatori profesionisti premium cu experienta certificata."
        assert tag_strategy(text) == "benefits_first"

    def test_tag_services_list(self):
        text = "Animatori cu baloane modelate, pictura pe fata si jocuri interactive."
        assert tag_strategy(text) == "services_list"

    def test_tag_local_intent(self):
        text = "Animatori petreceri copii Bucuresti si Ilfov. Rezerva: 0722 744 377."
        # price_first keywords absent, benefits_first absent, services_list absent
        # only local_intent
        result = tag_strategy(text)
        assert result == "local_intent"

    def test_tag_urgency_soft(self):
        text = "Animatori petreceri copii. Rezerva acum locul tau pentru weekend-ul viitor."
        # No price, benefits, services, local keywords
        assert tag_strategy(text) == "urgency_soft"

    def test_tag_family_trust(self):
        text = "Animatori siguri pentru copiii tai. Parinti fericiti la fiecare petrecere."
        assert tag_strategy(text) == "family_trust"

    def test_tag_brand_first(self):
        text = "SuperParty - animatori petreceri copii Bucuresti. Pachete 490 lei."
        assert tag_strategy(text) == "brand_first"

    def test_tag_uncategorized(self):
        text = "Servicii diverse fara niciun keyword relevant. Contactati-ne."
        assert tag_strategy(text) == "uncategorized"

    def test_tag_empty_string_returns_uncategorized(self):
        assert tag_strategy("") == "uncategorized"

    def test_tag_strategy_explain_includes_matched_keywords(self):
        text = "Pachete de la 490 lei."
        result = tag_strategy_explain(text)
        assert result["strategy"] == "price_first"
        assert len(result["matched_keywords"]) > 0

    def test_all_strategy_names_returns_all(self):
        names = get_all_strategy_names()
        assert "price_first" in names
        assert "benefits_first" in names
        assert "services_list" in names
        assert "local_intent" in names
        assert "urgency_soft" in names
        assert "family_trust" in names
        assert "brand_first" in names

    def test_tag_case_insensitive(self):
        text = "SUPERPARTY - animatori de top."
        assert tag_strategy(text) == "brand_first"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. OUTCOME MEMORY
# ═══════════════════════════════════════════════════════════════════════════════

class TestOutcomeMemory:

    def test_add_experiment_creates_pending_record(self, memory_file):
        record = add_experiment(
            url="/test/pagina",
            strategy="local_intent",
            before_meta="Vechi.",
            after_meta="Nou optimizat.",
            memory_path=memory_file,
        )
        assert record["result_label"] == "pending"
        assert record["url"] == "/test/pagina"
        assert record["strategy"] == "local_intent"
        assert "experiment_id" in record

    def test_add_experiment_appends_to_memory(self, memory_file):
        add_experiment(url="/a", strategy="local_intent", before_meta="x", after_meta="y", memory_path=memory_file)
        add_experiment(url="/b", strategy="price_first", before_meta="x", after_meta="y", memory_path=memory_file)
        all_exp = get_all_experiments(memory_file)
        assert len(all_exp) == 2

    def test_get_pending_returns_only_pending(self, memory_file):
        _write_json(memory_file, [
            _make_experiment(url="/a", result_label="pending"),
            _make_experiment(url="/b", result_label="positive"),
        ])
        pending = get_pending(memory_file)
        assert len(pending) == 1
        assert pending[0]["url"] == "/a"

    def test_get_closed_returns_non_pending(self, memory_file):
        _write_json(memory_file, [
            _make_experiment(url="/a", result_label="pending"),
            _make_experiment(url="/b", result_label="positive"),
            _make_experiment(url="/c", result_label="negative"),
        ])
        closed = get_closed(memory_file)
        assert len(closed) == 2

    def test_update_outcome_sets_result_label(self, memory_file):
        record = add_experiment(url="/test", strategy="price_first", before_meta="x", after_meta="y", memory_path=memory_file)
        updated = update_outcome(
            experiment_id=record["experiment_id"],
            result_label="positive",
            gsc_after={"impressions": 100, "ctr": 0.08, "position": 3.2},
            memory_path=memory_file,
        )
        assert updated["result_label"] == "positive"
        assert updated["closed_at"] is not None

    def test_mark_rollback_sets_strong_negative(self, memory_file):
        add_experiment(url="/test", strategy="urgency_soft", before_meta="x", after_meta="y", memory_path=memory_file)
        result = mark_rollback(url="/test", memory_path=memory_file)
        assert result["result_label"] == "strong_negative"
        assert result["rollback_happened"] is True

    def test_is_url_in_active_experiment_true(self, memory_file):
        add_experiment(url="/test", strategy="local_intent", before_meta="x", after_meta="y", memory_path=memory_file)
        assert is_url_in_active_experiment("/test", memory_file) is True

    def test_is_url_in_active_experiment_false_after_close(self, memory_file):
        record = add_experiment(url="/test", strategy="local_intent", before_meta="x", after_meta="y", memory_path=memory_file)
        update_outcome(record["experiment_id"], "positive", memory_path=memory_file)
        assert is_url_in_active_experiment("/test", memory_file) is False

    def test_get_experiments_past_deadline_returns_expired(self, memory_file):
        _write_json(memory_file, [
            _make_experiment(url="/old", result_label="pending", applied_days_ago=20, observation_window_days=14),
            _make_experiment(url="/new", result_label="pending", applied_days_ago=1, observation_window_days=14),
        ])
        expired = get_experiments_past_deadline(memory_file)
        assert len(expired) == 1
        assert expired[0]["url"] == "/old"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SCORER
# ═══════════════════════════════════════════════════════════════════════════════

class TestScorer:

    def _exp(self, imp_before=0, ctr_before=0.0, pos_before=5.0,
             imp_after=0, ctr_after=0.0, pos_after=5.0,
             rollback=False, result_label="closed"):
        return _make_experiment(
            result_label=result_label,
            rollback_happened=rollback,
            gsc_before={"impressions": imp_before, "ctr": ctr_before, "position": pos_before},
            gsc_after={"impressions": imp_after, "ctr": ctr_after, "position": pos_after},
        )

    def test_strong_negative_when_rollback(self):
        exp = self._exp(imp_after=200, ctr_before=0.05, ctr_after=0.08, rollback=True)
        result = score_experiment(exp)
        assert result["result_label"] == "strong_negative"

    def test_insufficient_data_when_gsc_after_null(self):
        exp = _make_experiment(result_label="positive",
                               gsc_after={"impressions": None, "ctr": None, "position": None})
        result = score_experiment(exp)
        assert result["result_label"] == "insufficient_data"

    def test_insufficient_data_when_impressions_below_minimum(self):
        exp = self._exp(imp_before=100, ctr_before=0.05, imp_after=MIN_IMPRESSIONS - 1, ctr_after=0.10)
        result = score_experiment(exp)
        assert result["result_label"] == "insufficient_data"

    def test_insufficient_data_when_still_pending(self):
        exp = _make_experiment(result_label="pending")
        result = score_experiment(exp)
        assert result["result_label"] == "insufficient_data"

    def test_positive_when_ctr_improves_above_threshold(self):
        ctr_before = 0.05
        ctr_after = ctr_before * (1 + CTR_THRESHOLD + 0.01)  # just above threshold
        exp = self._exp(imp_before=100, ctr_before=ctr_before,
                        imp_after=100, ctr_after=ctr_after)
        result = score_experiment(exp)
        assert result["result_label"] == "positive"

    def test_negative_when_ctr_drops_below_threshold(self):
        ctr_before = 0.05
        ctr_after = ctr_before * (1 - CTR_THRESHOLD - 0.01)  # just below threshold
        exp = self._exp(imp_before=100, ctr_before=ctr_before,
                        imp_after=100, ctr_after=ctr_after)
        result = score_experiment(exp)
        assert result["result_label"] == "negative"

    def test_neutral_when_ctr_within_noise_band(self):
        ctr_before = 0.05
        ctr_after = ctr_before * 1.02  # 2% change — within 5% threshold
        exp = self._exp(imp_before=100, ctr_before=ctr_before,
                        imp_after=100, ctr_after=ctr_after)
        result = score_experiment(exp)
        assert result["result_label"] == "neutral"

    def test_strategy_scores_aggregation(self):
        experiments = [
            {**_make_experiment(strategy="local_intent", result_label="positive"),
             "gsc_before": {"impressions": 100, "ctr": 0.05, "position": 5.0},
             "gsc_after": {"impressions": 120, "ctr": 0.07, "position": 4.5},
             "rollback_happened": False},
            {**_make_experiment(strategy="local_intent", result_label="negative"),
             "gsc_before": {"impressions": 100, "ctr": 0.05, "position": 5.0},
             "gsc_after": {"impressions": 110, "ctr": 0.03, "position": 5.5},
             "rollback_happened": False},
            {**_make_experiment(strategy="price_first", result_label="positive"),
             "gsc_before": {"impressions": 100, "ctr": 0.04, "position": 6.0},
             "gsc_after": {"impressions": 200, "ctr": 0.07, "position": 5.0},
             "rollback_happened": False},
        ]
        scores = compute_strategy_scores(experiments)
        assert "local_intent" in scores
        assert "price_first" in scores
        assert scores["price_first"]["n_positive"] >= 1

    def test_rollback_counts_as_strong_negative_in_aggregation(self):
        experiments = [
            {**_make_experiment(strategy="urgency_soft", rollback_happened=True),
             "gsc_before": {"impressions": 100, "ctr": 0.05, "position": 5.0},
             "gsc_after": {"impressions": 100, "ctr": 0.10, "position": 4.0},
             "result_label": "strong_negative"},
        ]
        scores = compute_strategy_scores(experiments)
        assert scores["urgency_soft"]["n_strong_negative"] == 1
        assert scores["urgency_soft"]["score"] < 0

    def test_get_best_strategy_returns_none_when_insufficient(self):
        scores = {"local_intent": {"score": 0.8, "n_total": 2, "n_positive": 2,
                                   "n_neutral": 0, "n_negative": 0, "n_strong_negative": 0,
                                   "n_insufficient_data": 0}}
        best = get_best_strategy(scores, min_experiments=3)
        assert best is None

    def test_get_best_strategy_returns_highest_scoring(self):
        scores = {
            "local_intent": {"score": 0.8, "n_total": 5, "n_positive": 5,
                              "n_neutral": 0, "n_negative": 0, "n_strong_negative": 0,
                              "n_insufficient_data": 0},
            "price_first": {"score": 0.4, "n_total": 5, "n_positive": 3,
                            "n_neutral": 1, "n_negative": 1, "n_strong_negative": 0,
                            "n_insufficient_data": 0},
        }
        best = get_best_strategy(scores, min_experiments=3)
        assert best == "local_intent"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. EXPERIMENT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestExperimentEngine:

    def test_can_open_experiment_blocked_pillar(self, pillar_registry_file, memory_file):
        can_open, blockers = can_open_experiment(
            "/animatori-petreceri-copii",
            pillar_registry_path=pillar_registry_file,
            memory_path=memory_file,
        )
        assert can_open is False
        assert "pillar_page_in_registry" in blockers

    def test_can_open_experiment_allowed_non_pillar(self, empty_pillar_registry, memory_file):
        can_open, blockers = can_open_experiment(
            "/baloane-latex",
            pillar_registry_path=empty_pillar_registry,
            memory_path=memory_file,
        )
        assert can_open is True
        assert blockers == []

    def test_can_open_experiment_blocked_active_experiment(self, empty_pillar_registry, memory_file):
        # Open first experiment
        add_experiment(url="/test", strategy="local_intent", before_meta="x", after_meta="y", memory_path=memory_file)
        # Try to open second for same URL
        can_open, blockers = can_open_experiment(
            "/test",
            pillar_registry_path=empty_pillar_registry,
            memory_path=memory_file,
        )
        assert can_open is False
        assert "url_has_active_experiment" in blockers

    def test_can_open_experiment_blocked_max_count(self, empty_pillar_registry, memory_file):
        # Fill up to max
        for i in range(MAX_EXPERIMENTS):
            add_experiment(url=f"/page-{i}", strategy="local_intent", before_meta="x", after_meta="y", memory_path=memory_file)
        # Try to open one more
        can_open, blockers = can_open_experiment(
            "/new-page",
            pillar_registry_path=empty_pillar_registry,
            memory_path=memory_file,
            max_experiments=MAX_EXPERIMENTS,
        )
        assert can_open is False
        assert any("max_experiments_reached" in b for b in blockers)

    def test_open_experiment_success(self, empty_pillar_registry, memory_file, tmp_path, monkeypatch):
        monkeypatch.setattr(engine_mod, "PILLAR_REGISTRY_PATH", empty_pillar_registry)
        monkeypatch.setattr(engine_mod, "OUTCOME_MEMORY_PATH", memory_file)
        result = open_experiment(
            url="/baloane-latex",
            strategy="price_first",
            before_meta="Baloane de la 100 lei.",
            after_meta="Baloane latex profesionale de la 100 lei. Livrare Bucuresti.",
            pillar_registry_path=empty_pillar_registry,
            memory_path=memory_file,
        )
        assert result["blocked"] is False
        assert result["experiment"] is not None
        assert result["experiment"]["strategy"] == "price_first"

    def test_open_experiment_blocked_pillar(self, pillar_registry_file, memory_file):
        result = open_experiment(
            url="/animatori-petreceri-copii",
            strategy="local_intent",
            before_meta="Text vechi.",
            after_meta="Text nou.",
            pillar_registry_path=pillar_registry_file,
            memory_path=memory_file,
        )
        assert result["blocked"] is True
        assert "pillar_page_in_registry" in result["blockers"]

    def test_get_active_experiment_count(self, memory_file, monkeypatch):
        monkeypatch.setattr(memory_mod, "OUTCOME_MEMORY_PATH", memory_file)
        add_experiment(url="/a", strategy="local_intent", before_meta="x", after_meta="y", memory_path=memory_file)
        add_experiment(url="/b", strategy="price_first", before_meta="x", after_meta="y", memory_path=memory_file)
        count = get_active_experiment_count(memory_file)
        assert count == 2

    def test_close_expired_experiments_marks_outcome(self, memory_file, monkeypatch):
        # Experiment past deadline with GSC data
        _write_json(memory_file, [
            {**_make_experiment(url="/old", result_label="pending",
                                applied_days_ago=16, observation_window_days=14,
                                gsc_before={"impressions": 100, "ctr": 0.04, "position": 5.0},
                                gsc_after={"impressions": 120, "ctr": 0.07, "position": 4.5}),
             "rollback_happened": False},
        ])
        closed = close_expired_experiments(memory_path=memory_file)
        assert len(closed) == 1
        assert closed[0]["result_label"] in {
            "positive", "neutral", "negative", "insufficient_data", "strong_negative"
        }

    def test_inject_gsc_data_updates_experiment(self, memory_file):
        record = add_experiment(url="/test", strategy="local_intent", before_meta="x", after_meta="y", memory_path=memory_file)
        updated = inject_gsc_data(
            experiment_id=record["experiment_id"],
            impressions_after=150,
            ctr_after=0.08,
            position_after=4.2,
            memory_path=memory_file,
        )
        assert updated["gsc_after"]["impressions"] == 150
        assert updated["gsc_after"]["ctr"] == 0.08


# ═══════════════════════════════════════════════════════════════════════════════
# 5. OBSERVABILITY SNAPSHOT
# ═══════════════════════════════════════════════════════════════════════════════

class TestObservabilitySnapshot:

    def test_generates_all_four_artefacts(self, tmp_path, memory_file):
        active_path = tmp_path / "experiments_active.json"
        closed_path = tmp_path / "experiments_closed.json"
        scores_path = tmp_path / "strategy_scores.json"
        status_path = tmp_path / "level6_status.json"

        # Empty memory
        _write_json(memory_file, [])

        status = generate_observability_snapshot(
            memory_path=memory_file,
            active_path=active_path,
            closed_path=closed_path,
            scores_path=scores_path,
            status_path=status_path,
        )

        assert active_path.exists()
        assert closed_path.exists()
        assert scores_path.exists()
        assert status_path.exists()
        assert "experiments" in status
        assert "outcomes" in status

    def test_status_shows_correct_active_count(self, tmp_path, memory_file):
        _write_json(memory_file, [
            _make_experiment(url="/a", result_label="pending"),
            _make_experiment(url="/b", result_label="positive"),
        ])

        status = generate_observability_snapshot(
            memory_path=memory_file,
            active_path=tmp_path / "a.json",
            closed_path=tmp_path / "c.json",
            scores_path=tmp_path / "s.json",
            status_path=tmp_path / "st.json",
        )
        assert status["experiments"]["active_count"] == 1
        assert status["experiments"]["closed_count"] == 1

    def test_rollback_urls_in_status(self, tmp_path, memory_file):
        _write_json(memory_file, [
            _make_experiment(url="/rolledback", result_label="strong_negative", rollback_happened=True),
        ])

        status = generate_observability_snapshot(
            memory_path=memory_file,
            active_path=tmp_path / "a.json",
            closed_path=tmp_path / "c.json",
            scores_path=tmp_path / "s.json",
            status_path=tmp_path / "st.json",
        )
        assert "/rolledback" in status["rollback_urls"]

    def test_budget_remaining_correct(self, tmp_path, memory_file):
        _write_json(memory_file, [
            _make_experiment(url="/a", result_label="pending"),
        ])
        status = generate_observability_snapshot(
            memory_path=memory_file,
            active_path=tmp_path / "a.json",
            closed_path=tmp_path / "c.json",
            scores_path=tmp_path / "s.json",
            status_path=tmp_path / "st.json",
        )
        assert status["experiments"]["budget_remaining"] == MAX_EXPERIMENTS - 1


# ═══════════════════════════════════════════════════════════════════════════════
# 6. INVARIANTE CRITICE
# ═══════════════════════════════════════════════════════════════════════════════

class TestCriticalInvariants:

    def test_rollback_overrides_positive_gsc_data(self):
        """strong_negative must take precedence even if GSC shows improvement."""
        exp = _make_experiment(
            result_label="positive",
            rollback_happened=True,
            gsc_before={"impressions": 100, "ctr": 0.05, "position": 5.0},
            gsc_after={"impressions": 200, "ctr": 0.10, "position": 3.0},
        )
        result = score_experiment(exp)
        assert result["result_label"] == "strong_negative"

    def test_insufficient_data_with_only_1_impression(self):
        """Must not make conclusions from 1 impression."""
        exp = _make_experiment(
            result_label="closed",
            gsc_before={"impressions": 100, "ctr": 0.05, "position": 5.0},
            gsc_after={"impressions": 1, "ctr": 0.99, "position": 1.0},
        )
        result = score_experiment(exp)
        assert result["result_label"] == "insufficient_data"

    def test_tier_ab_pillar_blocked_in_experiment(self, pillar_registry_file, memory_file):
        """Pillar pages must always be blocked regardless of how they are categorized."""
        can_open, blockers = can_open_experiment(
            "/arcade-baloane",  # in pilot registry
            pillar_registry_path=pillar_registry_file,
            memory_path=memory_file,
        )
        assert can_open is False

    def test_uncategorized_strategy_never_fails(self):
        """Strategy tagger must never raise an exception."""
        for text in ["", " ", "random text fara niciun keyword", "123 456 789"]:
            result = tag_strategy(text)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_update_outcome_rejects_invalid_label(self, memory_file):
        """update_outcome must reject invalid result_label values."""
        record = add_experiment(url="/test", strategy="local_intent", before_meta="x", after_meta="y", memory_path=memory_file)
        with pytest.raises(ValueError):
            update_outcome(record["experiment_id"], "invalid_label", memory_path=memory_file)
