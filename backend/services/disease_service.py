"""
Disease Diagnosis Service
=========================
Diagnoses crop diseases from either a text symptom description or
an uploaded leaf/plant image using Google Gemini Vision.
"""

from __future__ import annotations

import base64
import json

import google.generativeai as genai
from PIL import Image
import io

from config import GEMINI_API_KEY
from prompts.disease_prompt import DISEASE_VISION_PROMPT, DISEASE_TEXT_TEMPLATE
from services import rag_service

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


def _build_response(
    disease_name: str,
    description: str,
    rag_result: dict,
) -> dict:
    """Merge disease identification with RAG management steps."""
    answer: str = rag_result.get("answer", "")
    sources: list[str] = rag_result.get("sources", [])

    # Parse management steps: split numbered lines or bullet points
    management_steps: list[str] = []
    for line in answer.splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading numbers/bullets
        for prefix in ("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "-", "•", "*"):
            if line.startswith(prefix):
                line = line[len(prefix):].strip()
                break
        if line:
            management_steps.append(line)

    # Fallback: use full answer as a single step
    if not management_steps and answer:
        management_steps = [answer]

    return {
        "disease_name": disease_name,
        "description": description,
        "management_steps": management_steps,
        "sources": sources,
    }


# ── Public API ────────────────────────────────────────────────────────────────

def diagnose_from_text(crop: str, symptoms: str) -> dict:
    """
    Diagnose a crop disease from a text symptom description.
    """
    query = DISEASE_TEXT_TEMPLATE.format(crop=crop, symptoms=symptoms)
    rag_result = rag_service.query(query)

    answer: str = rag_result.get("answer", "")
    first_sentence = answer.split(".")[0].strip() if answer else "Unknown disease"
    disease_name = first_sentence[:80] if first_sentence else "Unknown disease"

    return _build_response(
        disease_name=disease_name,
        description=f"Based on the described symptoms on {crop}: {symptoms}",
        rag_result=rag_result,
    )


def diagnose_from_image(image_bytes: bytes, crop: str) -> dict:
    """
    Diagnose a crop disease from an uploaded leaf/plant image using Gemini Vision.
    """
    try:
        # Load image using PIL
        image = Image.open(io.BytesIO(image_bytes))

        # Use Gemini Vision model (gemini-1.5-flash supports images natively)
        model = genai.GenerativeModel("gemini-3.6-flash")

        response = model.generate_content(
            [DISEASE_VISION_PROMPT, image],
            generation_config={"temperature": 0.1, "max_output_tokens": 500},
        )
        raw_text = response.text or ""

    except Exception as e:
        return {
            "disease_name": "Vision analysis failed",
            "description": f"Could not analyse the image: {e}",
            "management_steps": [],
            "sources": [],
        }

    # Parse JSON response from vision model
    disease_name = "Unknown disease"
    description = raw_text
    try:
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        if start != -1 and end > start:
            parsed = json.loads(raw_text[start:end])
            disease_name = parsed.get("disease_name", disease_name)
            observed = parsed.get("observed_symptoms", "")
            confidence = parsed.get("confidence", "")
            description = f"{observed} (Confidence: {confidence})" if observed else raw_text
    except (json.JSONDecodeError, ValueError):
        pass

    # Query RAG for management recommendations
    rag_query = f"How to manage {disease_name} in {crop}? What are the treatment and prevention steps?"
    rag_result = rag_service.query(rag_query)

    return _build_response(
        disease_name=disease_name,
        description=description,
        rag_result=rag_result,
    )
