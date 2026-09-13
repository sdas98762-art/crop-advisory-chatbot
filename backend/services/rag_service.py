"""
RAG Service
===========
Retrieves relevant agriculture knowledge from ChromaDB and passes it
to Google Gemini to generate grounded advisory responses.
Uses local HuggingFace embeddings (same model as ingestion).
"""

from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from config import GEMINI_API_KEY, CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from prompts.system_prompt import (
    SYSTEM_PROMPT,
    FALLBACK_RESPONSE,
    OFF_TOPIC_RESPONSE,
)

PESTICIDE_DISCLAIMER = (
    "\n\n⚠️ For pesticide application, follow label instructions carefully "
    "and consult a certified agronomist or local extension officer."
)

PESTICIDE_KEYWORDS: frozenset[str] = frozenset([
    "pesticide", "herbicide", "fungicide", "insecticide",
    "chemical", "spray", "dose", "dosage"
])

AGRICULTURE_KEYWORDS: frozenset[str] = frozenset([
    "crop", "farm", "soil", "plant", "seed", "harvest", "irrigation",
    "fertilizer", "disease", "pest", "weather", "yield", "sow", "grow",
    "wheat", "rice", "maize", "cotton", "vegetable", "fruit", "field",
])

LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"

# Singletons
_vectorstore: Chroma | None = None
_chain = None


def _get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=LOCAL_EMBED_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        _vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
    return _vectorstore


def _format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def _extract_text(response) -> str:
    """Extract plain text from Gemini response regardless of format."""
    if isinstance(response, str):
        return response
    # New Gemini API returns list of content blocks
    if isinstance(response, list):
        parts = []
        for item in response:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    # Fallback: convert to string
    return str(response)


def _get_chain():
    global _chain
    if _chain is None:
        vs = _get_vectorstore()
        retriever = vs.as_retriever(search_kwargs={"k": 5})

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.2,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "Question: {question}"),
        ])

        _chain = (
            {
                "context": retriever | _format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
            | _extract_text
        )
    return _chain


def query(user_input: str) -> dict[str, object]:
    """
    Query the RAG pipeline.
    Returns: {"answer": str, "sources": list[str]}
    """
    lower_input = user_input.lower()

    # Only block very obvious off-topic (greetings, completely unrelated)
    # Let Gemini decide for everything else
    obvious_offtopic = ["hello", "hi", "hey", "joke", "movie", "song", "cricket", "football"]
    is_obvious_offtopic = (
        any(kw == lower_input.strip() for kw in obvious_offtopic)
        or len(user_input.split()) <= 2
    )
    if is_obvious_offtopic:
        return {
            "answer": "Hello! 👋 I'm your Crop Advisory Assistant. Ask me anything about crops, diseases, fertilizers, irrigation, or farming advice!",
            "sources": []
        }

    vs = _get_vectorstore()

    # Check if collection has documents
    try:
        count = vs._collection.count()
    except Exception:
        count = 0

    if count == 0:
        return {
            "answer": (
                "The knowledge base is not yet populated. "
                "Please run `python ingestion/ingest.py` to index the agriculture documents."
            ),
            "sources": [],
        }

    # Get source documents for citation
    try:
        source_docs = vs.similarity_search(user_input, k=5)
        sources: list[str] = []
        seen: set[str] = set()
        for doc in source_docs:
            src = doc.metadata.get("source_file") or doc.metadata.get("source", "")
            if src and src not in seen:
                sources.append(src)
                seen.add(src)
    except Exception:
        source_docs = []
        sources = []

    # Run the chain
    try:
        chain = _get_chain()
        answer: str = chain.invoke(user_input)
    except Exception as e:
        return {"answer": FALLBACK_RESPONSE, "sources": []}

    # Off-topic guard
    if "I specialise in crop advisory" in answer:
        return {"answer": OFF_TOPIC_RESPONSE, "sources": []}

    # Pesticide disclaimer
    needs_disclaimer = (
        any(kw in lower_input for kw in PESTICIDE_KEYWORDS) or
        any(kw in answer.lower() for kw in PESTICIDE_KEYWORDS)
    )
    if needs_disclaimer:
        answer = answer + PESTICIDE_DISCLAIMER

    return {"answer": answer, "sources": sources}
