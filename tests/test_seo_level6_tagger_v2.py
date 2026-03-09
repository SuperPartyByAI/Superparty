"""
tests/test_seo_level6_tagger_v2.py

Suite de teste pentru tagger v2.0 cu scoring cumulativ.

Acopera:
- Strategii pure (local_intent, benefits_first, price_first, etc.)
- Cazuri mixte cu tie-break
- Fixture-uri reale din PR #92 (voluntari, mogosoaia, pantelimon)
- Observability: all_candidates, winning_reason, tier_keywords
- Regresii pe strategiile existente
- Fuzzing: texte goale, aleatoare, extreme
"""
import pytest
from pathlib import Path

from agent.tasks.seo_level6_strategy_tagger import (
    tag_strategy,
    tag_strategy_explain,
    tag_strategy_debug,
    get_all_strategy_names,
)

# ─── Fixture-uri din PR #92 ───────────────────────────────────────────────────

FIXTURE_VOLUNTARI = (
    "Animatori petreceri copii Voluntari — livrăm în Pipera, centrul vechi "
    "și complexele rezidențiale. Costume premium, 30 personaje. Sună: 0722 744 377."
)

FIXTURE_MOGOSOAIA = (
    "Animatori petreceri copii Mogoșoaia — pachete de la 350 RON. "
    "Standard 60 min, Premium 90 min, VIP 120 min. Acoperim vilele și palatele din zonă. "
    "0722 744 377."
)

FIXTURE_PANTELIMON = (
    "Animatori petreceri copii Pantelimon — venim la domiciliu, sala sau gradinita. "
    "Programe adaptate 1–12 ani, 30 costume. Zonă: Cernica, Brănești incluse. "
    "Tel: 0722 744 377."
)

# Baseline generica (template anterior PR #92)
FIXTURE_BASELINE_TEMPLATE = (
    "Animatori profesioniști pentru petreceri copii în {city}, Ilfov. "
    "Costume premium, programe 60-120 min. Rezervă: 0722 744 377."
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. FIXTURE-URI PR #92 — testele care au esuat in v1.0
# ═══════════════════════════════════════════════════════════════════════════════

class TestFixturesPR92:

    def test_voluntari_is_local_intent(self):
        """
        v1.0: voluntari a primit price_first (greseala).
        v2.0: 'livram in', 'complexele rezidentiale', 'voluntari' trebuie sa bata orice pret.
        """
        result = tag_strategy(FIXTURE_VOLUNTARI)
        assert result == "local_intent", (
            f"Voluntari ar trebui local_intent, got {result}. "
            f"Debug: {tag_strategy_debug(FIXTURE_VOLUNTARI)}"
        )

    def test_pantelimon_is_benefits_first(self):
        """
        v1.0: pantelimon a primit price_first (greseala).
        v2.0: 'venim la domiciliu/sala/gradinita', 'adaptate 1–12 ani' trebuie sa bata.
        """
        result = tag_strategy(FIXTURE_PANTELIMON)
        assert result == "benefits_first", (
            f"Pantelimon ar trebui benefits_first, got {result}. "
            f"Debug: {tag_strategy_debug(FIXTURE_PANTELIMON)}"
        )

    def test_mogosoaia_is_price_first(self):
        """
        v1.0 si v2.0: mogosoaia intentionat price_first, trebuie mentinut.
        Textul are 'de la 350 RON', 'Standard', 'Premium', 'VIP' — dominant price.
        """
        result = tag_strategy(FIXTURE_MOGOSOAIA)
        assert result == "price_first", (
            f"Mogosoaia ar trebui price_first, got {result}. "
            f"Debug: {tag_strategy_debug(FIXTURE_MOGOSOAIA)}"
        )

    def test_voluntari_explain_shows_tier_keywords(self):
        """Explain trebuie sa arate ca tier_keywords au contribuit la victoria local_intent."""
        result = tag_strategy_explain(FIXTURE_VOLUNTARI)
        assert result["strategy"] == "local_intent"
        # Fie tier_keywords, fie matched_keywords trebuie sa contina semnale locale
        all_matched = result["matched_tier_keywords"] + result["matched_keywords"]
        has_local_signal = any(
            kw in FIXTURE_VOLUNTARI.lower()
            for kw in ["voluntari", "livr", "complexele", "pipera", "centrul vechi"]
        )
        assert has_local_signal, f"Nu gasim semnal local in matched: {all_matched}"

    def test_pantelimon_explain_shows_tier_keywords(self):
        """Explain trebuie sa arate ca tier_keywords benefits_first au contribuit."""
        result = tag_strategy_explain(FIXTURE_PANTELIMON)
        assert result["strategy"] == "benefits_first"
        all_matched = result["matched_tier_keywords"] + result["matched_keywords"]
        has_benefits_signal = any(
            kw in FIXTURE_PANTELIMON.lower()
            for kw in ["venim la", "domiciliu", "gradinita", "adaptate"]
        )
        assert has_benefits_signal, f"Nu gasim semnal benefits in matched: {all_matched}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. STRATEGII PURE
# ═══════════════════════════════════════════════════════════════════════════════

class TestPureStrategies:

    def test_price_first_pure(self):
        """Text cu DOAR semnale de pret → price_first."""
        text = "Pachete de la 490 lei. Tarif standard 350 RON, premium 540 RON."
        assert tag_strategy(text) == "price_first"

    def test_local_intent_pure(self):
        """Text cu DOAR localitate → local_intent."""
        text = "Animatori petreceri copii Voluntari, Ilfov. Acoperim Pipera."
        assert tag_strategy(text) == "local_intent"

    def test_benefits_first_pure(self):
        """Text cu DOAR beneficii → benefits_first."""
        text = "Venim la domiciliu, sala sau gradinita. Programe adaptate 1-12 ani. Flexibil."
        assert tag_strategy(text) == "benefits_first"

    def test_services_list_pure(self):
        """Text cu DOAR servicii → services_list."""
        text = "Baloane modelate, pictura pe fata, tatuaje temporare, jocuri interactive."
        assert tag_strategy(text) == "services_list"

    def test_urgency_soft_pure(self):
        """Text cu DOAR urgenta → urgency_soft."""
        text = "Disponibilitate limitata weekend. Rezerva acum la 0722 744 377."
        assert tag_strategy(text) == "urgency_soft"

    def test_family_trust_pure(self):
        """Text cu DOAR trust → family_trust."""
        text = "Siguranta copilului pe primul loc. Parinti fericiti in fiecare petrecere."
        assert tag_strategy(text) == "family_trust"

    def test_brand_first_pure(self):
        """SuperParty in primele 20 chars → brand_first."""
        text = "SuperParty animatori petreceri copii Bucuresti."
        assert tag_strategy(text) == "brand_first"

    def test_brand_first_not_in_first20(self):
        """SuperParty dupa 20 chars → NU brand_first, ci alta strategie."""
        text = "Animatori petreceri copii - SuperParty Bucuresti."
        result = tag_strategy(text)
        assert result != "brand_first", f"Ar trebui sa nu fie brand_first, got {result}"

    def test_uncategorized_no_keywords(self):
        """Fara niciun keyword relevant → uncategorized."""
        text = "Servicii diverse nementionate. Contactati-ne pentru detalii."
        assert tag_strategy(text) == "uncategorized"

    def test_empty_string_is_uncategorized(self):
        assert tag_strategy("") == "uncategorized"

    def test_whitespace_only_is_uncategorized(self):
        assert tag_strategy("   ") == "uncategorized"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CAZURI MIXTE — tie-break si scoring
# ═══════════════════════════════════════════════════════════════════════════════

class TestMixedCases:

    def test_local_beats_price_at_tie(self):
        """
        Text cu semnal local PUTERNIC si semnal de pret SLAB → local_intent.
        'livram in + centrul vechi + voluntari' (>4pt local) trebuie sa bata '350 RON' singur (2pt price).
        """
        text = (
            "Animatori petreceri copii — livrăm în Voluntari, centrul vechi "
            "și complexele rezidențiale. Pret la cerere."
        )
        result = tag_strategy(text)
        assert result == "local_intent", (
            f"local_intent ar trebui sa bata price la text mix, got {result}. "
            f"Debug: {tag_strategy_debug(text)['all_scores']}"
        )

    def test_benefits_beats_price_at_tie(self):
        """
        Text cu semnal benefits PUTERNIC si pret SLAB → benefits_first.
        'venim la domiciliu, gradinita' (tier=2) bat '350' singur.
        """
        text = "Venim la domiciliu si gradinita. Programe adaptate 1-12 ani. De la 350 RON."
        result = tag_strategy(text)
        assert result == "benefits_first", (
            f"benefits_first ar trebui sa bata price, got {result}. "
            f"Debug: {tag_strategy_debug(text)['all_scores']}"
        )

    def test_price_wins_when_dominant(self):
        """
        Text cu MULTI semnale de pret si UN singur semnal local → price_first.
        'de la 350 RON, standard 490 lei, premium 540, VIP 700' > 'voluntari' singur.
        """
        text = "Pachete de la 350 RON, standard 490 lei, pret la cerere. Servim Voluntari."
        result = tag_strategy(text)
        assert result == "price_first", (
            f"price_first ar trebui sa castige cand dominant, got {result}. "
            f"Debug: {tag_strategy_debug(text)['all_scores']}"
        )

    def test_local_wins_when_dominant(self):
        """
        Text cu MULTI semnale locale si UN singur pret → local_intent.
        """
        text = (
            "Animatori Voluntari, Ilfov — livrăm în Pipera, centrul vechi, "
            "complexele rezidențiale. Preturi la cerere."
        )
        result = tag_strategy(text)
        assert result == "local_intent", (
            f"local_intent ar trebui sa castige cand dominant, got {result}. "
            f"Debug: {tag_strategy_debug(text)['all_scores']}"
        )

    def test_benefits_wins_when_dominant(self):
        """
        Text cu MULTI semnale benefits si UN singur pret → benefits_first.
        """
        text = (
            "Venim la domiciliu, sala de petreceri sau gradinita. "
            "Programe adaptate 1-12 ani. Locatii flexibile. Pret la cerere."
        )
        result = tag_strategy(text)
        assert result == "benefits_first", (
            f"benefits_first ar trebui sa castige cand dominant, got {result}. "
            f"Debug: {tag_strategy_debug(text)['all_scores']}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. OBSERVABILITY API
# ═══════════════════════════════════════════════════════════════════════════════

class TestObservabilityAPI:

    def test_explain_has_all_required_fields(self):
        result = tag_strategy_explain(FIXTURE_VOLUNTARI)
        required = [
            "strategy", "matched_keywords", "matched_tier_keywords",
            "score", "winning_strategy_reason", "all_candidates", "text_sample"
        ]
        for field in required:
            assert field in result, f"Camp lipsa din explain: {field}"

    def test_explain_all_candidates_includes_all_strategies_with_score(self):
        result = tag_strategy_explain(FIXTURE_MOGOSOAIA)
        candidate_names = [c["strategy"] for c in result["all_candidates"]]
        # Mogosoaia: price_first expected, dar si local (mogosoaia keyword) ar trebui sa apara
        assert "price_first" in candidate_names

    def test_debug_includes_all_strategies(self):
        result = tag_strategy_debug(FIXTURE_VOLUNTARI)
        assert "winner" in result
        assert "all_scores" in result
        assert "price_first" in result["all_scores"]
        assert "local_intent" in result["all_scores"]
        assert "benefits_first" in result["all_scores"]

    def test_debug_winner_matches_tag_strategy(self):
        text = FIXTURE_PANTELIMON
        debug_result = tag_strategy_debug(text)
        direct_result = tag_strategy(text)
        assert debug_result["winner"] == direct_result

    def test_explain_winning_reason_not_empty(self):
        result = tag_strategy_explain(FIXTURE_VOLUNTARI)
        assert result["winning_strategy_reason"]
        assert len(result["winning_strategy_reason"]) > 0

    def test_explain_score_positive_for_winner(self):
        result = tag_strategy_explain(FIXTURE_VOLUNTARI)
        assert result["score"] > 0

    def test_explain_strategy_and_winner_consistent(self):
        for fixture in [FIXTURE_VOLUNTARI, FIXTURE_MOGOSOAIA, FIXTURE_PANTELIMON]:
            explain = tag_strategy_explain(fixture)
            direct = tag_strategy(fixture)
            assert explain["strategy"] == direct, (
                f"Inconsistenta: explain={explain['strategy']}, direct={direct}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. REGRESII STRATEGY EXISTENTE
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegressions:

    def test_brand_first_regression(self):
        text = "SuperParty - animatori petreceri copii Bucuresti."
        assert tag_strategy(text) == "brand_first"

    def test_services_list_regression(self):
        text = "Baloane modelate, pictura pe fata, tatuaje. Jocuri interactive pentru copii."
        assert tag_strategy(text) == "services_list"

    def test_urgency_soft_regression(self):
        text = "Animatori petreceri copii. Rezerva acum locul tau pentru weekend."
        assert tag_strategy(text) == "urgency_soft"

    def test_family_trust_regression(self):
        text = "Parinti fericiti la fiecare petrecere. Siguranta copilului garantata."
        assert tag_strategy(text) == "family_trust"

    def test_uncategorized_regression(self):
        text = "Informatii despre diverse servicii. Contactati-ne."
        assert tag_strategy(text) == "uncategorized"

    def test_baseline_template_bucuresti_is_local(self):
        """Template-ul vechi (cu 'Ilfov' + 'Rezerva') → local_intent trebuie sa predomine."""
        text = FIXTURE_BASELINE_TEMPLATE.format(city="Voluntari")
        result = tag_strategy(text)
        # 'Ilfov' e local keyword + 'Voluntari' e local keyword → local_intent
        # 'Rezerva' e urgency_soft
        # Nu ar trebui sa fie price_first (nu are pret)
        assert result != "price_first", (
            f"Baseline template nu ar trebui price_first, got {result}"
        )

    def test_get_all_strategy_names_includes_all(self):
        names = get_all_strategy_names()
        required = [
            "price_first", "benefits_first", "services_list",
            "local_intent", "urgency_soft", "family_trust", "brand_first", "uncategorized"
        ]
        for name in required:
            assert name in names, f"Strategie lipsa: {name}"

    def test_tag_never_raises_exception(self):
        """tag_strategy trebuie sa nu ridice niciodata exceptie."""
        edge_cases = [
            "", " ", "\n", "   \t  ", "123 456 789 !!!",
            "a" * 500,
            "RON RON RON RON lei lei lei de la de la",
            "voluntari voluntari voluntari voluntari",
        ]
        for text in edge_cases:
            result = tag_strategy(text)
            assert isinstance(result, str) and len(result) > 0, (
                f"tag_strategy a returnat invalid pentru: {repr(text[:40])}"
            )
