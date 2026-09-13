"""Tests for the RAG service (mocked ChromaDB and LangChain chain)."""
from unittest.mock import patch, MagicMock
import pytest


def _make_mock_doc(content: str, source: str):
    doc = MagicMock()
    doc.page_content = content
    doc.metadata = {"source_file": source}
    return doc


MOCK_DOCS = [
    _make_mock_doc("Wheat rust is caused by Puccinia fungi. Apply propiconazole.", "fao_wheat.pdf"),
    _make_mock_doc("Rice blast management: use resistant varieties and fungicide.", "icar_rice.pdf"),
]


@patch("services.rag_service._get_vectorstore")
@patch("services.rag_service._get_chain")
def test_query_returns_answer_and_sources(mock_chain, mock_vs):
    from services.rag_service import query

    # Mock vectorstore
    vs = MagicMock()
    vs._collection.count.return_value = 100
    vs.similarity_search_with_score.return_value = [(MOCK_DOCS[0], 0.2)]
    mock_vs.return_value = vs

    # Mock chain
    chain = MagicMock()
    chain.invoke.return_value = {"answer": "Apply fungicide for rust.", "context": MOCK_DOCS}
    mock_chain.return_value = chain

    result = query("How to treat wheat rust?")
    assert result["answer"] != ""
    assert isinstance(result["sources"], list)
    assert len(result["sources"]) > 0


@patch("services.rag_service._get_vectorstore")
def test_query_returns_message_when_kb_empty(mock_vs):
    from services.rag_service import query

    vs = MagicMock()
    vs._collection.count.return_value = 0
    mock_vs.return_value = vs

    result = query("What fertilizer for rice?")
    assert "not yet populated" in result["answer"].lower() or "ingestion" in result["answer"].lower()
    assert result["sources"] == []


@patch("services.rag_service._get_vectorstore")
@patch("services.rag_service._get_chain")
def test_query_off_topic_returns_guardrail(mock_chain, mock_vs):
    from services.rag_service import query

    vs = MagicMock()
    vs._collection.count.return_value = 100
    vs.similarity_search_with_score.return_value = [(MOCK_DOCS[0], 0.2)]
    mock_vs.return_value = vs

    chain = MagicMock()
    chain.invoke.return_value = {
        "answer": "I specialise in crop advisory. Please ask me about crops.",
        "context": [],
    }
    mock_chain.return_value = chain

    result = query("What is the capital of France?")
    assert "crop advisory" in result["answer"].lower()


@patch("services.rag_service._get_vectorstore")
@patch("services.rag_service._get_chain")
def test_query_appends_pesticide_disclaimer(mock_chain, mock_vs):
    from services.rag_service import query

    vs = MagicMock()
    vs._collection.count.return_value = 100
    vs.similarity_search_with_score.return_value = [(MOCK_DOCS[0], 0.2)]
    mock_vs.return_value = vs

    chain = MagicMock()
    chain.invoke.return_value = {
        "answer": "Use propiconazole fungicide to control rust.",
        "context": MOCK_DOCS[:1],
    }
    mock_chain.return_value = chain

    result = query("What fungicide to use for wheat rust?")
    assert "⚠️" in result["answer"] or "pesticide" in result["answer"].lower()
