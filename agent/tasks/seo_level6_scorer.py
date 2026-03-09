"""
SEO Level 6 — Learning Scorer

Scorer transparent cu reguli explicabile pentru evaluarea outcome-urilor experimentelor.
Nu foloseste ML sau modele externe. Toate regulile sunt documentate explicit.

REGULI SCORER v1.0:
────────────────────────────────────────────────────────────────────────────────
  strong_negative:
    rollback_happened = True  (override orice alt rezultat)

  insufficient_data:
    gsc_after is None
    OR impressions_after < MIN_IMPRESSIONS
    OR fereastra de observare nu s-a scurs (pending)

  positive:
    impressions_after >= MIN_IMPRESSIONS
    AND ctr_after > ctr_before * (1 + CTR_THRESHOLD)
    AND position_after <= position_before + POSITION_TOLERANCE

  negative:
    impressions_after >= MIN_IMPRESSIONS
    AND ctr_after < ctr_before * (1 - CTR_THRESHOLD)

  neutral:
    impressions_after >= MIN_IMPRESSIONS
    AND abs(ctr_after - ctr_before) <= CTR_THRESHOLD * max(ctr_before, 0.001)
────────────────────────────────────────────────────────────────────────────────

Scorer per strategie agregate:
  strategy_score = (n_positive - n_negative) / max(n_total, 1)
  Range: [-1.0, 1.0]
  Experiment sunt ignorate daca result_label == insufficient_data
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent
STRATEGY_SCORES_PATH = ROOT_DIR / "reports" / "superparty" / "seo_level6_strategy_scores.json"

# ─── Thresholds (explicit, documentate) ──────────────────────────────────────

MIN_IMPRESSIONS: int = 50       # Minimul de impresii pentru a considera date suficiente
CTR_THRESHOLD: float = 0.05     # 5% variatie minima pentru a declara positive/negative
POSITION_TOLERANCE: float = 1.0 # Pozitia poate scadea cu max 1 loc fara a penaliza


# ─── Single experiment scorer ─────────────────────────────────────────────────

def score_experiment(experiment: dict) -> dict:
    """
    Score a single experiment record.

    Returns a dict:
    {
      "result_label": str,   # positive / neutral / negative / insufficient_data / strong_negative
      "explanation": str,
      "details": dict        # valori relevante utilizate
    }
    """
    # ── strong_negative override ──────────────────────────────────────────────
    if experiment.get("rollback_happened", False):
        return {
            "result_label": "strong_negative",
            "explanation": "Rollback happened — strong_negative override applies.",
            "details": {"rollback_happened": True},
        }

    # ── Check pending (fereastra nu s-a scurs) ───────────────────────────────
    result_label = experiment.get("result_label", "pending")
    if result_label == "pending":
        return {
            "result_label": "insufficient_data",
            "explanation": "Experiment still pending — observation window not elapsed.",
            "details": {"result_label_in_memory": "pending"},
        }

    # ── Extract GSC data ──────────────────────────────────────────────────────
    gsc_before = experiment.get("gsc_before") or {}
    gsc_after = experiment.get("gsc_after") or {}

    imp_before = gsc_before.get("impressions")
    imp_after = gsc_after.get("impressions")
    ctr_before = gsc_before.get("ctr")
    ctr_after = gsc_after.get("ctr")
    pos_before = gsc_before.get("position")
    pos_after = gsc_after.get("position")

    # ── insufficient_data checks ─────────────────────────────────────────────
    if imp_after is None or ctr_after is None:
        return {
            "result_label": "insufficient_data",
            "explanation": "No GSC data after experiment — cannot evaluate.",
            "details": {"gsc_after": gsc_after},
        }

    if imp_after < MIN_IMPRESSIONS:
        return {
            "result_label": "insufficient_data",
            "explanation": f"Impressions after ({imp_after}) < MIN_IMPRESSIONS ({MIN_IMPRESSIONS}).",
            "details": {"impressions_after": imp_after, "min_required": MIN_IMPRESSIONS},
        }

    # ── If before data missing → insufficient ────────────────────────────────
    if ctr_before is None or imp_before is None:
        return {
            "result_label": "insufficient_data",
            "explanation": "No GSC data before experiment — cannot compare.",
            "details": {"gsc_before": gsc_before},
        }

    # ── Scoring logic ─────────────────────────────────────────────────────────
    ctr_delta = ctr_after - ctr_before
    ctr_before_safe = max(ctr_before, 0.001)  # avoid division by zero

    is_positive = ctr_after > ctr_before * (1 + CTR_THRESHOLD)
    is_negative = ctr_after < ctr_before * (1 - CTR_THRESHOLD)

    # Position check for positive (optional data)
    position_ok = True
    if is_positive and pos_before is not None and pos_after is not None:
        position_ok = pos_after <= pos_before + POSITION_TOLERANCE

    if is_positive and position_ok:
        return {
            "result_label": "positive",
            "explanation": (
                f"CTR improved: {ctr_before:.4f} → {ctr_after:.4f} "
                f"(+{ctr_delta:.4f}, >{CTR_THRESHOLD*100:.0f}% threshold). "
                f"Impressions: {imp_after} >= {MIN_IMPRESSIONS}."
            ),
            "details": {
                "ctr_before": ctr_before,
                "ctr_after": ctr_after,
                "ctr_delta": round(ctr_delta, 6),
                "impressions_after": imp_after,
                "position_before": pos_before,
                "position_after": pos_after,
            },
        }

    if is_negative:
        return {
            "result_label": "negative",
            "explanation": (
                f"CTR declined: {ctr_before:.4f} → {ctr_after:.4f} "
                f"({ctr_delta:.4f}, <-{CTR_THRESHOLD*100:.0f}% threshold). "
                f"Impressions: {imp_after} >= {MIN_IMPRESSIONS}."
            ),
            "details": {
                "ctr_before": ctr_before,
                "ctr_after": ctr_after,
                "ctr_delta": round(ctr_delta, 6),
                "impressions_after": imp_after,
            },
        }

    # Fallthrough → neutral
    return {
        "result_label": "neutral",
        "explanation": (
            f"CTR within noise band: {ctr_before:.4f} → {ctr_after:.4f} "
            f"(delta {ctr_delta:.4f}, threshold ±{CTR_THRESHOLD*100:.0f}%). "
            f"Impressions: {imp_after} >= {MIN_IMPRESSIONS}."
        ),
        "details": {
            "ctr_before": ctr_before,
            "ctr_after": ctr_after,
            "ctr_delta": round(ctr_delta, 6),
            "impressions_after": imp_after,
        },
    }


# ─── Strategy aggregate scorer ────────────────────────────────────────────────

def compute_strategy_scores(experiments: list) -> dict:
    """
    Compute aggregate scores per strategy from a list of experiment records.

    Ignores insufficient_data experiments.
    Returns dict:
    {
      "strategy_name": {
        "score": float,          # [-1.0, 1.0]
        "n_positive": int,
        "n_neutral": int,
        "n_negative": int,
        "n_strong_negative": int,
        "n_total": int,          # excludes insufficient_data
        "n_insufficient_data": int,
      }
    }
    """
    aggregates: dict = {}

    for exp in experiments:
        strategy = exp.get("strategy", "uncategorized")
        scored = score_experiment(exp)
        label = scored["result_label"]

        if strategy not in aggregates:
            aggregates[strategy] = {
                "score": 0.0,
                "n_positive": 0,
                "n_neutral": 0,
                "n_negative": 0,
                "n_strong_negative": 0,
                "n_total": 0,
                "n_insufficient_data": 0,
            }

        agg = aggregates[strategy]

        if label == "insufficient_data":
            agg["n_insufficient_data"] += 1
        elif label == "positive":
            agg["n_positive"] += 1
            agg["n_total"] += 1
        elif label == "neutral":
            agg["n_neutral"] += 1
            agg["n_total"] += 1
        elif label == "negative":
            agg["n_negative"] += 1
            agg["n_total"] += 1
        elif label == "strong_negative":
            agg["n_strong_negative"] += 1
            agg["n_total"] += 1

    # Compute normalized score
    for strategy, agg in aggregates.items():
        n = agg["n_total"]
        if n == 0:
            agg["score"] = 0.0
        else:
            # positive = +1, neutral = 0, negative = -1, strong_negative = -1
            numerator = agg["n_positive"] - agg["n_negative"] - agg["n_strong_negative"]
            agg["score"] = round(numerator / n, 4)

    return aggregates


def get_best_strategy(strategy_scores: dict, min_experiments: int = 3) -> Optional[str]:
    """
    Returns the strategy with highest score, if it has >= min_experiments evaluations.
    Returns None if no strategy has enough data.
    """
    eligible = {
        name: data for name, data in strategy_scores.items()
        if data["n_total"] >= min_experiments
    }
    if not eligible:
        return None
    return max(eligible, key=lambda k: eligible[k]["score"])
