"""
Intent Detection Service
========================
Simple keyword-based routing to decide whether a user message should
be handled by the disease diagnosis service or the general RAG advisory.
"""

from __future__ import annotations

DISEASE_KEYWORDS: frozenset[str] = frozenset(
    [
        "disease", "pest", "yellowing", "yellow leaves", "spots", "brown spots",
        "wilting", "wilt", "fungal", "fungus", "bacterial", "virus", "viral",
        "infected", "infection", "symptom", "lesion", "blight", "rust", "mold",
        "mould", "rot", "rotting", "powdery", "downy", "leaf curl", "insect",
        "bug", "worm", "caterpillar", "aphid", "whitefly", "nematode", "sick",
        "dying", "dead", "damage", "damaged",
    ]
)

WEATHER_KEYWORDS: frozenset[str] = frozenset(
    [
        "rain", "rainfall", "drought", "temperature", "irrigation", "weather",
        "flood", "waterlog", "humidity", "frost", "heat", "cold", "monsoon",
        "dry", "wet", "climate", "forecast",
    ]
)


class Intent:
    DISEASE = "disease"
    WEATHER = "weather"
    GENERAL = "general"


def detect_intent(message: str) -> str:
    """
    Return the detected intent for a user message.

    Returns:
        Intent.DISEASE  — message is about disease/pest symptoms
        Intent.WEATHER  — message is primarily about weather
        Intent.GENERAL  — general crop advisory query
    """
    lower = message.lower()

    disease_hits = sum(1 for kw in DISEASE_KEYWORDS if kw in lower)
    weather_hits = sum(1 for kw in WEATHER_KEYWORDS if kw in lower)

    if disease_hits > 0 and disease_hits >= weather_hits:
        return Intent.DISEASE
    if weather_hits > 0:
        return Intent.WEATHER
    return Intent.GENERAL
