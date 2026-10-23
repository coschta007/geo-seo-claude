#!/usr/bin/env python3
"""
Citability Scorer — Analyzes content blocks for AI citation readiness.
Scores passages against a heuristic rubric of signals associated with
passages that AI models quote:
- Self-contained (extractable without context)
- Fact-rich with specific statistics
- Structured with clear answer patterns

The rubric also gives partial credit for passages of roughly 134-167 words.
That range comes from third-party analysis of AI-cited passages, not from any
search engine; Google states there is no ideal content length for its AI
features. Treat the score as a checklist result, not a measured citation rate.

Language support: English and German. The language is detected from the text,
and other languages are scored with the English patterns, so their scores are
less meaningful.
"""

import sys
import json
import re
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Required packages not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


# Language-neutral patterns
PERCENT = r"\d+(?:[.,]\d+)?\s?%"  # "25%", and "25 %" as written in German
CURRENCY = (
    r"(?:[$€£]\s?\d[\d.,]*(?:\s*(?:million|billion|Mio\.|Mrd\.|Millionen|Milliarden|M|B|K)\b)?"
    r"|\d[\d.,]*(?:\s*(?:Mio\.|Mrd\.|Millionen|Milliarden|million|billion))?\s?(?:€|EUR\b|Euro\b|USD\b|CHF\b))"
)
YEAR = r"\b20[1-3]\d\b"
KNOWN_SOURCES = r"(?:Gartner|Forrester|McKinsey|Harvard|Stanford|MIT|Google|Microsoft|OpenAI|Anthropic)"

# Abbreviations whose periods must not end a sentence ("z. B.", "e.g.", "Dr.")
ABBREVIATIONS = re.compile(
    r"\b(?:z\.\s?B|d\.\s?h|u\.\s?a|bzw|ca|evtl|ggf|inkl|vgl|usw|Nr|Mio|Mrd|Tsd|Dr|Prof|Mr|Mrs|e\.g|i\.e|etc|vs)\.",
    re.IGNORECASE,
)

PATTERNS = {
    "en": {
        "definitions": [
            r"\b\w+\s+is\s+(?:a|an|the)\s",
            r"\b\w+\s+refers?\s+to\s",
            r"\b\w+\s+means?\s",
            r"\b\w+\s+(?:can be |are )?defined\s+as\s",
            r"\bin\s+(?:simple|other)\s+(?:terms|words)\s*,",
        ],
        "answer_verbs": r"\b(?:is|are|was|were|means?|refers?)\b",
        "magnitudes": r"\d+\s+(?:million|billion|thousand)",
        "attributed_claims": r"(?:according to|research shows|studies? (?:show|indicate|suggest|found)|data (?:shows|indicates|suggests))",
        "pronouns": r"\b(?:it|they|them|their|this|that|these|those|he|she|his|her)\b",
        "pronoun_exclusions": set(),
        "proper_nouns": r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b",
        "transitions": r"(?:first|second|third|finally|additionally|moreover|furthermore)",
        "numbered_items": r"(?:\d+[\.\)]\s|\b(?:step|tip|point)\s+\d+)",
        "counted_numbers": r"\b\d+(?:,\d{3})*(?:\.\d+)?\s+(?:users|customers|pages|sites|companies|businesses|people|percent|times|x\b)",
        "named_sources": [
            r"(?:according to|per|from|by)\s+[A-Z]",
            KNOWN_SOURCES,
            r"\([A-Z][a-z]+(?:\s+\d{4})?\)",
        ],
        "original_data": r"(?:our (?:research|study|data|analysis|survey|findings)|we (?:found|discovered|analyzed|surveyed|measured))",
        "examples": r"(?:case study|for example|for instance|in practice|real-world|hands-on)",
        "tool_mentions": r"(?:using|with|via|through)\s+[A-Z][a-z]+",
    },
    "de": {
        "definitions": [
            r"\b\w+\s+(?:ist|sind)\s+(?:ein|eine|einer|der|die|das)\s",
            r"\b\w+\s+(?:bezeichnet|beschreibt)\s",
            r"\bversteht\s+man\b",
            r"\b\w+\s+bedeutet\s",
            r"\bdefiniert\s+als\b|\bals\s+\S+\s+definiert\b",
            r"\b(?:einfach|kurz)\s+gesagt\b|\bmit\s+anderen\s+Worten\b",
        ],
        "answer_verbs": r"\b(?:ist|sind|war|waren|bedeutet|bezeichnet|heißt)\b",
        "magnitudes": r"\d+(?:[.,]\d+)?\s+(?:Millionen|Milliarden|Tausend|Mio\.|Mrd\.)",
        "attributed_claims": (
            r"(?:\blaut\b|\bgemäß\b|\bzufolge\b"
            r"|\b(?:Studien?|Untersuchungen?|Umfragen?|Analysen?|Daten|Forschung|Zahlen)\s+"
            r"(?:zeigt|zeigen|belegt|belegen|ergab|ergaben|deutet|deuten|legt|legen)\b)"
        ),
        "pronouns": (
            r"\b(?:es|er|sie|ihn|ihm|ihnen|ihr|ihre|ihren|ihrem|ihrer|ihres"
            r"|sein|seine|seinen|seinem|seiner|seines"
            r"|dies|diese|dieser|dieses|diesen|diesem|jene|jener|jenes|jenen|jenem)\b"
        ),
        # Formal address ("Sie erhalten ...") addresses the reader, like the
        # English "you", which the English list does not count either.
        "pronoun_exclusions": {"Sie", "Ihr", "Ihre", "Ihren", "Ihrem", "Ihrer", "Ihres", "Ihnen"},
        # As loose as the English check, which also counts sentence-initial
        # words; both languages clear the 3-word threshold in normal prose.
        "proper_nouns": r"\b[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)*\b",
        "transitions": (
            r"\b(?:erstens|zweitens|drittens|zuerst|zunächst|danach|anschließend"
            r"|schließlich|außerdem|zudem|darüber hinaus|ferner|abschließend)\b"
        ),
        "numbered_items": r"(?:\d+[\.\)]\s|\b(?:Schritt|Tipp|Punkt)\s+\d+)",
        "counted_numbers": (
            r"\b\d+(?:\.\d{3})*(?:,\d+)?(?:\s+|-)"
            r"(?:Nutzer(?:innen)?|Kund(?:en|innen)|Seiten|Websites|Webseiten|Unternehmen|Firmen"
            r"|Betriebe|Menschen|Personen|Besucher(?:innen)?|Mitarbeiter(?:innen)?|Prozent|Mal)\b"
        ),
        "named_sources": [
            r"\b(?:[Ll]aut|[Gg]emäß|[Nn]ach Angaben (?:von|des|der))\s+[A-ZÄÖÜ]",
            r"\b[A-ZÄÖÜ]\w+\s+zufolge\b",
            KNOWN_SOURCES,
            r"\([A-ZÄÖÜ][a-zäöüß]+(?:\s+\d{4})?\)",
        ],
        "original_data": (
            r"(?:\bunser(?:e|er|en|em)?\s+(?:Studie|Untersuchung|Analyse|Umfrage|Daten|Auswertung|Erhebung|Forschung|Ergebnisse)"
            r"|\bwir\s+haben\s+(?:\w+\s+){0,5}?(?:festgestellt|herausgefunden|analysiert|untersucht|befragt|gemessen|ausgewertet)\b"
            r"|\bvon\s+uns\s+(?:\w+\s+)?(?:analysiert|untersucht|befragt|gemessen|ausgewertet)\w*)"
        ),
        "examples": r"(?:Fallstudie|Praxisbeispiel|zum Beispiel|beispielsweise|\bz\.\s?B\.|in der Praxis|aus der Praxis|praxisnah)",
        # German capitalizes every noun, so a capitalized word after "mit" is
        # not evidence of a product; require a multi-word name or an acronym.
        "tool_mentions": (
            r"\b(?:mit|mittels|per|via|über)\s+"
            r"(?:[A-ZÄÖÜ][\w-]*\s+[A-ZÄÖÜ][\w-]*|[A-Z]{2,}[\w-]*|[A-Z][a-z]+[A-Z][\w-]*)"
        ),
    },
}

# Function words detected per language. Words spelled the same in both
# languages ("in", "an", "was", "will", "so") are left out.
STOPWORDS = {
    "en": {
        "the", "and", "is", "are", "of", "to", "that", "it", "for", "with", "as",
        "on", "be", "by", "this", "or", "from", "have", "not", "you", "we",
        "they", "can", "which",
    },
    "de": {
        "der", "die", "das", "und", "ist", "nicht", "mit", "sich", "auf", "für",
        "ein", "eine", "einen", "dem", "den", "des", "zu", "im", "von", "wird",
        "sind", "auch", "werden", "wie", "bei", "oder", "nach", "dass", "noch",
        "nur", "über", "aus", "sie", "es", "wir",
    },
}

def detect_language(text: str) -> str:
    """Return "de" for German text and "en" otherwise."""
    tokens = re.findall(r"[a-zäöüß]+", text.lower())
    de_hits = sum(1 for t in tokens if t in STOPWORDS["de"])
    en_hits = sum(1 for t in tokens if t in STOPWORDS["en"])
    return "de" if de_hits > en_hits else "en"


def split_sentences(text: str) -> list:
    """Split on sentence punctuation, keeping decimals ("1.200", "3.5") and
    abbreviations ("z. B.", "e.g.") inside their sentence."""
    masked = ABBREVIATIONS.sub(lambda m: m.group(0).replace(".", ""), text)
    return re.split(r"[.!?]+(?=[\"'“”‘’»«)\]]*(?:\s|$))", masked)


def score_passage(text: str, heading: Optional[str] = None, lang: Optional[str] = None) -> dict:
    """Score a single passage for AI citability (0-100).

    lang is "en" or "de"; it is detected from the text when not given.
    """
    if lang not in PATTERNS:
        lang = detect_language(text)
    p = PATTERNS[lang]

    words = text.split()
    word_count = len(words)

    scores = {
        "answer_block_quality": 0,
        "self_containment": 0,
        "structural_readability": 0,
        "statistical_density": 0,
        "uniqueness_signals": 0,
    }

    # === 1. Answer Block Quality (30%) ===
    abq_score = 0

    # Check for definition patterns ("X is...", "X ist ein...")
    for pattern in p["definitions"]:
        if re.search(pattern, text, re.IGNORECASE):
            abq_score += 15
            break

    # Check if answer appears early (first 60 words)
    first_60_words = " ".join(words[:60])
    if any(
        re.search(pattern, first_60_words, re.IGNORECASE)
        for pattern in [p["answer_verbs"], PERCENT, CURRENCY, p["magnitudes"]]
    ):
        abq_score += 15

    # Question-based heading bonus
    if heading and heading.endswith("?"):
        abq_score += 10

    # Clear, direct sentence structure
    sentences = split_sentences(text)
    short_clear_sentences = sum(
        1 for s in sentences if 5 <= len(s.split()) <= 25
    )
    if sentences:
        clarity_ratio = short_clear_sentences / len(sentences)
        abq_score += int(clarity_ratio * 10)

    # Has specific, quotable claim
    if re.search(p["attributed_claims"], text, re.IGNORECASE):
        abq_score += 10

    scores["answer_block_quality"] = min(abq_score, 30)

    # === 2. Self-Containment (25%) ===
    sc_score = 0

    # Passage length heuristic (134-167 words; not a documented requirement)
    if 134 <= word_count <= 167:
        sc_score += 10
    elif 100 <= word_count <= 200:
        sc_score += 7
    elif 80 <= word_count <= 250:
        sc_score += 4
    elif word_count < 30 or word_count > 400:
        sc_score += 0
    else:
        sc_score += 2

    # Low pronoun density (fewer pronouns = more self-contained)
    pronoun_count = sum(
        1
        for pronoun in re.findall(p["pronouns"], text, re.IGNORECASE)
        if pronoun not in p["pronoun_exclusions"]
    )
    if word_count > 0:
        pronoun_ratio = pronoun_count / word_count
        if pronoun_ratio < 0.02:
            sc_score += 8
        elif pronoun_ratio < 0.04:
            sc_score += 5
        elif pronoun_ratio < 0.06:
            sc_score += 3

    # Contains named entities (proper nouns, brands, specific terms)
    proper_nouns = len(re.findall(p["proper_nouns"], text))
    if proper_nouns >= 3:
        sc_score += 7
    elif proper_nouns >= 1:
        sc_score += 4

    scores["self_containment"] = min(sc_score, 25)

    # === 3. Structural Readability (20%) ===
    sr_score = 0

    # Sentence count and length distribution
    if sentences:
        avg_sentence_length = word_count / len(sentences)
        if 10 <= avg_sentence_length <= 20:
            sr_score += 8
        elif 8 <= avg_sentence_length <= 25:
            sr_score += 5
        else:
            sr_score += 2

    # Contains list-like structures
    if re.search(p["transitions"], text, re.IGNORECASE):
        sr_score += 4

    # Contains numbered items or bullet-like content
    if re.search(p["numbered_items"], text, re.IGNORECASE):
        sr_score += 4

    # Paragraph breaks (indicates structure)
    if "\n" in text:
        sr_score += 4

    scores["structural_readability"] = min(sr_score, 20)

    # === 4. Statistical Density (15%) ===
    sd_score = 0

    # Percentages
    pct_count = len(re.findall(PERCENT, text))
    sd_score += min(pct_count * 3, 6)

    # Currency amounts ($, €, £, EUR, ...)
    currency_count = len(re.findall(CURRENCY, text))
    sd_score += min(currency_count * 3, 5)

    # Other numbers with context
    number_count = len(re.findall(p["counted_numbers"], text, re.IGNORECASE))
    sd_score += min(number_count * 2, 4)

    # Year references (indicates timeliness)
    year_count = len(re.findall(YEAR, text))
    if year_count > 0:
        sd_score += 2

    # Named sources
    for pattern in p["named_sources"]:
        if re.search(pattern, text):
            sd_score += 2

    scores["statistical_density"] = min(sd_score, 15)

    # === 5. Uniqueness Signals (10%) ===
    us_score = 0

    # Original data indicators
    if re.search(p["original_data"], text, re.IGNORECASE):
        us_score += 5

    # Case study or example indicators
    if re.search(p["examples"], text, re.IGNORECASE):
        us_score += 3

    # Specific tool/product mentions (shows practical experience)
    if re.search(p["tool_mentions"], text):
        us_score += 2

    scores["uniqueness_signals"] = min(us_score, 10)

    # === Calculate total ===
    total = sum(scores.values())

    # Determine grade
    if total >= 80:
        grade = "A"
        label = "Highly Citable"
    elif total >= 65:
        grade = "B"
        label = "Good Citability"
    elif total >= 50:
        grade = "C"
        label = "Moderate Citability"
    elif total >= 35:
        grade = "D"
        label = "Low Citability"
    else:
        grade = "F"
        label = "Poor Citability"

    return {
        "heading": heading,
        "language": lang,
        "word_count": word_count,
        "total_score": total,
        "grade": grade,
        "label": label,
        "breakdown": scores,
        "preview": " ".join(words[:30]) + ("..." if word_count > 30 else ""),
    }


def analyze_page_citability(url: str) -> dict:
    """Analyze all content blocks on a page for citability."""
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            timeout=30,
        )
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch page: {str(e)}"}

    soup = BeautifulSoup(response.text, "lxml")

    # Remove non-content elements
    for element in soup.find_all(
        ["script", "style", "nav", "footer", "header", "aside", "form"]
    ):
        element.decompose()

    # Extract content blocks
    blocks = []
    current_heading = "Introduction"
    current_paragraphs = []

    for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol", "table"]):
        if element.name.startswith("h"):
            # Save previous section
            if current_paragraphs:
                combined = " ".join(current_paragraphs)
                if len(combined.split()) >= 20:
                    blocks.append(
                        {"heading": current_heading, "content": combined}
                    )
            current_heading = element.get_text(strip=True)
            current_paragraphs = []
        else:
            text = element.get_text(strip=True)
            if text and len(text.split()) >= 5:
                current_paragraphs.append(text)

    # Last block
    if current_paragraphs:
        combined = " ".join(current_paragraphs)
        if len(combined.split()) >= 20:
            blocks.append({"heading": current_heading, "content": combined})

    # Detect the language once per page so every block uses the same patterns
    page_language = detect_language(" ".join(b["content"] for b in blocks))

    # Score each block
    scored_blocks = []
    for block in blocks:
        score = score_passage(block["content"], block["heading"], page_language)
        scored_blocks.append(score)

    # Calculate page-level metrics
    if scored_blocks:
        avg_score = sum(b["total_score"] for b in scored_blocks) / len(scored_blocks)
        top_blocks = sorted(scored_blocks, key=lambda x: x["total_score"], reverse=True)[:5]
        bottom_blocks = sorted(scored_blocks, key=lambda x: x["total_score"])[:5]

        # Passages in the 134-167 word heuristic range
        optimal_count = sum(
            1 for b in scored_blocks if 134 <= b["word_count"] <= 167
        )
    else:
        avg_score = 0
        top_blocks = []
        bottom_blocks = []
        optimal_count = 0

    # Grade distribution
    grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for block in scored_blocks:
        grade_dist[block["grade"]] += 1

    return {
        "url": url,
        "language": page_language,
        "total_blocks_analyzed": len(scored_blocks),
        "average_citability_score": round(avg_score, 1),
        "optimal_length_passages": optimal_count,
        "grade_distribution": grade_dist,
        "top_5_citable": top_blocks,
        "bottom_5_citable": bottom_blocks,
        "all_blocks": scored_blocks,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python citability_scorer.py <url>")
        print("Returns JSON with citability analysis for all content blocks.")
        sys.exit(1)

    url = sys.argv[1]
    result = analyze_page_citability(url)
    print(json.dumps(result, indent=2, default=str))
