"""Tests for the intent detection service."""
from services.intent_service import detect_intent, Intent


def test_disease_intent_keyword():
    assert detect_intent("my wheat has yellow spots and is wilting") == Intent.DISEASE


def test_disease_intent_pest():
    assert detect_intent("There are aphids on my tomato plants") == Intent.DISEASE


def test_weather_intent():
    assert detect_intent("Will it rain tomorrow? Should I irrigate?") == Intent.WEATHER


def test_general_intent_crop_selection():
    assert detect_intent("Which crop should I grow in sandy soil?") == Intent.GENERAL


def test_general_intent_fertilizer():
    assert detect_intent("How much urea for wheat per acre?") == Intent.GENERAL


def test_disease_wins_over_weather():
    # disease hits should dominate over a single weather keyword
    assert detect_intent("My crop is infected and there is drought stress") == Intent.DISEASE
