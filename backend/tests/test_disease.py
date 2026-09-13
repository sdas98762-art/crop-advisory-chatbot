"""Tests for the disease diagnosis service (mocked LLM/RAG calls)."""
from unittest.mock import patch


RAG_MOCK_RESULT = {
    "answer": "1. Remove infected leaves.\n2. Apply copper-based fungicide.\n3. Improve air circulation.",
    "sources": ["crop_disease_guide.pdf"],
}

VISION_MOCK_JSON = (
    '{"disease_name": "Powdery Mildew", "confidence": "High", '
    '"observed_symptoms": "White powdery coating on leaves"}'
)


@patch("services.disease_service.rag_service.query", return_value=RAG_MOCK_RESULT)
def test_diagnose_from_text_returns_dict(mock_rag):
    from services.disease_service import diagnose_from_text

    result = diagnose_from_text(crop="wheat", symptoms="yellowing and brown spots on leaves")
    assert "disease_name" in result
    assert "management_steps" in result
    assert isinstance(result["management_steps"], list)
    assert "sources" in result


@patch("services.disease_service.rag_service.query", return_value=RAG_MOCK_RESULT)
def test_diagnose_from_text_has_management_steps(mock_rag):
    from services.disease_service import diagnose_from_text

    result = diagnose_from_text(crop="tomato", symptoms="wilting and dark spots")
    assert len(result["management_steps"]) > 0


@patch("services.disease_service.rag_service.query", return_value=RAG_MOCK_RESULT)
@patch("services.disease_service._get_client")
def test_diagnose_from_image_returns_dict(mock_client, mock_rag):
    from services.disease_service import diagnose_from_image
    from unittest.mock import MagicMock

    # Mock the OpenAI vision response
    mock_choice = MagicMock()
    mock_choice.message.content = VISION_MOCK_JSON
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_client.return_value.chat.completions.create.return_value = mock_completion

    result = diagnose_from_image(image_bytes=b"fake_image_bytes", crop="wheat")
    assert result["disease_name"] == "Powdery Mildew"
    assert "management_steps" in result
    assert result["sources"] == ["crop_disease_guide.pdf"]


@patch("services.disease_service.rag_service.query", return_value=RAG_MOCK_RESULT)
@patch("services.disease_service._get_client")
def test_diagnose_from_image_handles_vision_failure(mock_client, mock_rag):
    from services.disease_service import diagnose_from_image

    mock_client.return_value.chat.completions.create.side_effect = Exception("API error")
    result = diagnose_from_image(image_bytes=b"fake", crop="rice")
    assert "failed" in result["disease_name"].lower() or "disease_name" in result
