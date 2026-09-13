from fastapi import APIRouter, Request
from pydantic import BaseModel, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from services import rag_service, disease_service, weather_service
from services.intent_service import detect_intent, Intent
from prompts.advisory_prompt import ADVISORY_WITH_WEATHER_TEMPLATE

router = APIRouter(tags=["chat"])
limiter = Limiter(key_func=get_remote_address)


class ChatRequest(BaseModel):
    message: str
    location: str | None = None
    session_id: str | None = None

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("message must not be empty")
        return v.strip()


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []
    weather_context: str | None = None


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Main chat endpoint.
    Routes the message to the appropriate service based on intent,
    optionally injecting weather context when a location is provided.
    """
    message = body.message
    location = (body.location or "").strip()

    # ── Weather context ────────────────────────────────────────────────────
    weather_ctx: str | None = None
    if location:
        weather_ctx = weather_service.get_weather_context(location) or None

    # ── Intent routing ─────────────────────────────────────────────────────
    intent = detect_intent(message)

    if intent == Intent.DISEASE:
        # Text-based disease diagnosis
        result = disease_service.diagnose_from_text(
            crop=_extract_crop_hint(message),
            symptoms=message,
        )
        response_text = _format_disease_response(result)
        sources = result.get("sources", [])

    else:
        # General RAG advisory (with optional weather context injection)
        if weather_ctx:
            enriched_query = ADVISORY_WITH_WEATHER_TEMPLATE.format(
                weather_context=weather_ctx,
                question=message,
            )
        else:
            enriched_query = message

        rag_result = rag_service.query(enriched_query)
        response_text = rag_result.get("answer", "")
        sources = rag_result.get("sources", [])

    return ChatResponse(
        response=response_text,
        sources=sources,
        weather_context=weather_ctx,
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

_COMMON_CROPS = [
    "wheat", "rice", "maize", "corn", "cotton", "sugarcane", "soybean",
    "tomato", "potato", "onion", "garlic", "chilli", "pepper", "mango",
    "banana", "apple", "grape", "groundnut", "sunflower", "mustard",
    "barley", "sorghum", "millet", "chickpea", "lentil", "pea", "bean",
]


def _extract_crop_hint(message: str) -> str:
    """Return the first crop name found in the message, or 'crop'."""
    lower = message.lower()
    for crop in _COMMON_CROPS:
        if crop in lower:
            return crop
    return "crop"


def _format_disease_response(result: dict) -> str:
    """Format a disease diagnosis result as a readable chat message."""
    disease = result.get("disease_name", "Unknown")
    description = result.get("description", "")
    steps: list[str] = result.get("management_steps", [])

    lines = [f"**Likely Issue: {disease}**", "", description, ""]
    if steps:
        lines.append("**Management Recommendations:**")
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")

    return "\n".join(lines).strip()
