"""
Tests for language handling in citability_scorer.py.

The scorer used to match English phrasing only, so a German passage scored
far below the same content in English. These tests pin English/German parity
and the language-neutral number, currency and year patterns.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from citability_scorer import (  # noqa: E402
    detect_language,
    score_passage,
    split_sentences,
)


ENGLISH_PASSAGE = (
    "Generative Engine Optimization is a method for making websites visible in AI search engines. "
    "According to Gartner, search volume on traditional engines will drop by 25% by 2026. "
    "Our research shows that pages with clear definitions are cited 3 times more often. "
    "For example, a SaaS company we analyzed grew its AI referrals from 1,200 users to 4,800 users within six months. "
    "The project cost $15,000 and was implemented using Google Search Console and Semrush. "
    "First, the team rewrote the key pages. Second, it added structured data. Finally, it published original statistics. "
    "In simple terms, the approach rewards precise, sourced facts over vague marketing language. "
    "Studies show that AI systems prefer self-contained passages that answer a question directly in the opening sentence."
)

GERMAN_PASSAGE = (
    "Generative Engine Optimization ist eine Methode, um Websites in KI-Suchmaschinen sichtbar zu machen. "
    "Laut Gartner wird das Suchvolumen klassischer Suchmaschinen bis 2026 um 25 % sinken. "
    "Unsere Untersuchung zeigt, dass Seiten mit klaren Definitionen 3-mal häufiger zitiert werden. "
    "Ein von uns analysiertes SaaS-Unternehmen steigerte zum Beispiel seine KI-Verweise innerhalb von sechs Monaten "
    "von 1.200 auf 4.800 Nutzer. "
    "Das Projekt kostete 15.000 € und wurde mit Google Search Console und Semrush umgesetzt. "
    "Zuerst überarbeitete das Team die wichtigsten Seiten. Danach ergänzte es strukturierte Daten. "
    "Schließlich veröffentlichte es eigene Statistiken. "
    "Einfach gesagt belohnt der Ansatz präzise, belegte Fakten statt vager Werbesprache. "
    "Studien zeigen, dass KI-Systeme in sich geschlossene Passagen bevorzugen, die eine Frage direkt im ersten Satz beantworten."
)

PLAIN_GERMAN = (
    "Das Team hat die Seite im letzten Monat neu gestaltet und dabei viele Inhalte gekürzt, "
    "weil die Besucher schneller zu den wichtigen Informationen kommen sollten."
)


class TestLanguageDetection:
    def test_detects_german(self):
        assert detect_language(GERMAN_PASSAGE) == "de"

    def test_detects_english(self):
        assert detect_language(ENGLISH_PASSAGE) == "en"

    def test_defaults_to_english(self):
        assert detect_language("") == "en"

    def test_score_reports_language(self):
        assert score_passage(GERMAN_PASSAGE)["language"] == "de"
        assert score_passage(ENGLISH_PASSAGE)["language"] == "en"

    def test_explicit_language_overrides_detection(self):
        assert score_passage(GERMAN_PASSAGE, lang="en")["language"] == "en"


class TestGermanParity:
    def test_same_content_scores_alike_in_both_languages(self):
        en = score_passage(ENGLISH_PASSAGE, "What is GEO?")["total_score"]
        de = score_passage(GERMAN_PASSAGE, "Was ist GEO?")["total_score"]
        assert abs(en - de) <= 5, f"EN {en} vs DE {de}"

    def test_english_score_unchanged(self):
        # Score from before German support was added; English rules are
        # untouched for text without decimals or abbreviations.
        result = score_passage(ENGLISH_PASSAGE, "What is GEO?")
        assert result["total_score"] == 87
        assert result["breakdown"] == {
            "answer_block_quality": 30,
            "self_containment": 17,
            "structural_readability": 16,
            "statistical_density": 14,
            "uniqueness_signals": 10,
        }

    def test_german_answer_patterns_count(self):
        breakdown = score_passage(GERMAN_PASSAGE)["breakdown"]
        assert breakdown["answer_block_quality"] >= 25

    def test_german_uniqueness_signals_count(self):
        # "von uns analysiert" (5) + "zum Beispiel" (3) + "mit Google Search Console" (2)
        assert score_passage(GERMAN_PASSAGE)["breakdown"]["uniqueness_signals"] == 10

    def test_plain_german_gets_no_pattern_bonus(self):
        breakdown = score_passage(PLAIN_GERMAN)["breakdown"]
        assert breakdown["statistical_density"] == 0
        assert breakdown["uniqueness_signals"] == 0


class TestGermanPronouns:
    def test_german_pronouns_lower_self_containment(self):
        with_pronouns = (
            "Es ist wichtig, dass er sie früh informiert. Sie wissen dann, was es bedeutet "
            "und wie sie damit umgehen. Dies hilft ihnen, ihre Arbeit besser zu planen."
        )
        without_pronouns = (
            "Frühe Information ist wichtig für das Projektteam. Das Projektteam weiß dann, "
            "was die Änderung bedeutet und wie das Team damit umgeht. Das hilft dem Team bei der Planung."
        )
        assert (
            score_passage(with_pronouns)["breakdown"]["self_containment"]
            < score_passage(without_pronouns)["breakdown"]["self_containment"]
        )

    def test_formal_address_is_not_counted(self):
        formal = (
            "Mit dem Werkzeug planen Sie Kampagnen schneller. Sie verbinden Ihre Werkzeuge "
            "in wenigen Minuten und sehen Ihre Ergebnisse in einem Dashboard für das ganze Team."
        )
        neutral = (
            "Mit dem Werkzeug planen Teams Kampagnen schneller. Teams verbinden vorhandene Werkzeuge "
            "in wenigen Minuten und sehen alle Ergebnisse in einem Dashboard für das ganze Team."
        )
        assert (
            score_passage(formal)["breakdown"]["self_containment"]
            == score_passage(neutral)["breakdown"]["self_containment"]
        )


class TestNumbersAndCurrency:
    def _density(self, sentence, lang):
        return score_passage(sentence, lang=lang)["breakdown"]["statistical_density"]

    def test_german_percent_with_space(self):
        assert self._density("Die Quote stieg um 25 % im Vergleich.", "de") >= 3

    def test_euro_amounts(self):
        assert self._density("Das Projekt kostete 15.000 € insgesamt.", "de") >= 3
        assert self._density("Das Budget betrug 2,5 Mio. € pro Jahr.", "de") >= 3
        assert self._density("The budget was €2,500 per month.", "en") >= 3

    def test_dollar_amounts_still_count(self):
        assert self._density("The project cost $15,000 in total.", "en") >= 3

    def test_german_thousands_with_units(self):
        assert self._density("Die Plattform hat 4.800 Nutzer gewonnen.", "de") >= 2


class TestYears:
    def test_2020_to_2022_count(self):
        for year in (2020, 2021, 2022):
            text = f"The figure was measured in {year} across the market."
            assert score_passage(text, lang="en")["breakdown"]["statistical_density"] >= 2, year

    def test_years_after_2026_count(self):
        text = "The figure was measured in 2027 across the market."
        assert score_passage(text, lang="en")["breakdown"]["statistical_density"] >= 2


class TestSentenceSplitting:
    def test_decimals_do_not_end_sentences(self):
        assert [s for s in split_sentences("Der Umsatz lag bei 1.200 Euro und 3,5 Prozent.") if s.strip()] == [
            "Der Umsatz lag bei 1.200 Euro und 3,5 Prozent"
        ]
        assert len([s for s in split_sentences("Pages load in 2.5 seconds.") if s.strip()]) == 1

    def test_abbreviations_do_not_end_sentences(self):
        assert len([s for s in split_sentences("Viele Tools, z. B. Semrush, helfen dabei.") if s.strip()]) == 1
        assert len([s for s in split_sentences("Der Umsatz lag bei 1,2 Mrd. € im Jahr.") if s.strip()]) == 1
        assert len([s for s in split_sentences("Many tools, e.g. Semrush, help here.") if s.strip()]) == 1

    def test_sentence_ends_still_split(self):
        assert len([s for s in split_sentences("Erster Satz. Zweiter Satz! Dritter Satz?") if s.strip()]) == 3

    def test_sentence_ends_before_closing_quotes(self):
        assert len([s for s in split_sentences("Er sagte „Ja.“ Dann ging er.") if s.strip()]) == 2
        assert len([s for s in split_sentences('She said "yes." Then she left (quickly.) Done.') if s.strip()]) == 3
