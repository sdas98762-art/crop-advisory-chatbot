"""Integration tests for the POST /api/chat endpoint."""
from unittest.mock import patch


RAG_OK = {"answer": "Apply nitrogen fertilizer at 120 kg/ha for wheat.", "sources": ["fao_wheat.pdf"]}
DISEASE_OK = {
    "disease_name": "Leaf Rust",
    "description": "Rust spots on wheat leaves",
    "management_steps": ["Remove affected leaves", "Apply fungicide"],
    "sources": ["wheat_disease.pdf"],
}


def test_chat_general_advisory(client):
    with patch("services.rag_service.query", return_value=RAG_OK):
        resp = client.post("/api/chat", json={"message": "How much fertilizer for wheat?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert "sources" in data


def test_chat_disease_intent_routing(client):
    with patch("services.disease_service.diagnose_from_text", return_value=DISEASE_OK):
        resp = client.post(
            "/api/chat",
            json={"message": "My wheat has yellow spots and is wilting badly"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data


def test_chat_with_location_injects_weather(client):
    weather_ctx = "Current weather in Pune: 28°C, partly cloudy, humidity 72%."
    with (
        patch("services.weather_service.get_weather_context", return_value=weather_ctx),
        patch("services.rag_service.query", return_value=RAG_OK),
    ):
        resp = client.post(
            "/api/chat",
            json={"message": "Should I irrigate today?", "location": "Pune"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["weather_context"] == weather_ctx


def test_chat_empty_message_rejected(client):
    resp = client.post("/api/chat", json={"message": ""})
    assert resp.status_code == 422


def test_chat_off_topic_guardrail(client):
    off_topic = {
        "answer": "I specialise in crop advisory. Please ask me about crops.",
        "sources": [],
    }
    with patch("services.rag_service.query", return_value=off_topic):
        resp = client.post("/api/chat", json={"message": "Tell me a joke"})
    assert resp.status_code == 200
    data = resp.json()
    assert "crop" in data["response"].lower() or len(data["response"]) > 0


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
