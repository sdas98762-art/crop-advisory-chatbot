"""
Knowledge Base Ingestion Script
================================
Uses a LOCAL embedding model (no API calls, no rate limits, no internet needed).
Runs entirely on your machine using sentence-transformers.

Usage:
    python ingestion/ingest.py          # start or auto-resume
    python ingestion/ingest.py --reset  # wipe and restart fresh
"""

import argparse
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb
from dotenv import load_dotenv
load_dotenv()

from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME

SOURCES_DIR = Path(__file__).parent / "sources"
CHECKPOINT_FILE = Path(__file__).parent / "ingest_checkpoint.json"

# Local model — runs on CPU, no internet, no API key, no rate limits
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"

BATCH_SIZE = 200   # large batches are fine — all local, instant

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "disease": ["disease", "blight", "rust", "mold", "fungal", "bacterial",
                "viral", "pest", "insect", "pathogen", "infection", "symptom", "lesion"],
    "fertilizer": ["fertilizer", "nitrogen", "phosphorus", "potassium", "NPK",
                   "urea", "manure", "micronutrient", "soil nutrient", "deficiency"],
    "irrigation": ["irrigation", "water", "drip", "sprinkler", "moisture",
                   "rainfall", "drought", "flood", "waterlogging"],
    "weather": ["temperature", "humidity", "climate", "rainfall", "frost",
                "heat", "season", "monsoon", "forecast"],
    "crop": ["crop", "variety", "seed", "sowing", "harvest", "yield",
             "planting", "cultivation", "agronomy"],
}


def detect_category(text: str) -> str:
    text_lower = text.lower()
    scores = {cat: sum(1 for kw in kws if kw.lower() in text_lower)
              for cat, kws in CATEGORY_KEYWORDS.items()}
    best = max(scores, key=lambda c: scores[c])
    return best if scores[best] > 0 else "general"


def load_documents() -> list:
    pdf_files = list(SOURCES_DIR.glob("**/*.pdf"))
    if not pdf_files:
        print(f"  ⚠️  No PDFs found in {SOURCES_DIR}")
        return []
    all_docs = []
    for pdf_path in pdf_files:
        print(f"  📄 {pdf_path.name}")
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = pdf_path.name
            all_docs.extend(docs)
        except Exception as e:
            print(f"  ⚠️  Skipped {pdf_path.name}: {e}")
    print(f"  ✅ Loaded {len(all_docs)} pages from {len(pdf_files)} PDF(s)")
    return all_docs


def chunk_documents(docs: list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    for chunk in chunks:
        chunk.metadata["category"] = detect_category(chunk.page_content)
    print(f"  ✅ Created {len(chunks)} chunks")
    return chunks


def save_checkpoint(next_start: int, total: int) -> None:
    CHECKPOINT_FILE.write_text(
        json.dumps({"next_batch_start": next_start, "total_chunks": total}),
        encoding="utf-8",
    )


def load_checkpoint() -> dict | None:
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def clear_checkpoint() -> None:
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


def ingest(reset: bool = False) -> None:
    print("\n🌾 Crop Advisory — Knowledge Base Ingestion (Local Embeddings)")
    print("=" * 58)

    persist_dir = Path(CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)

    if reset:
        print("\n♻️  Resetting collection and checkpoint…")
        clear_checkpoint()
        client = chromadb.PersistentClient(path=str(persist_dir))
        try:
            client.delete_collection(CHROMA_COLLECTION_NAME)
            print("  ✅ Collection deleted")
        except Exception:
            print("  ℹ️  Collection did not exist")

    print("\n[1/3] Loading documents…")
    docs = load_documents()
    if not docs:
        return

    print("\n[2/3] Chunking documents…")
    chunks = chunk_documents(docs)
    total = len(chunks)

    # Check checkpoint
    checkpoint = load_checkpoint()
    if checkpoint and not reset:
        start = checkpoint.get("next_batch_start", 0)
        saved_total = checkpoint.get("total_chunks", total)
        if saved_total != total:
            print(f"\n⚠️  Chunk count changed. Starting fresh.")
            start = 0
            clear_checkpoint()
        elif start >= total:
            print("\n✅ Already fully ingested!")
            clear_checkpoint()
            return
        else:
            done_pct = round(start / total * 100, 1)
            print(f"\n♻️  Resuming from chunk {start}/{total} ({done_pct}% already done)")
    else:
        start = 0

    print("\n[3/3] Embedding with local model (no internet needed)…")
    print(f"  🤖 Model: {LOCAL_EMBED_MODEL}")
    print("  ⏳ Downloading model on first run (~80MB, one time only)…\n")

    embeddings = HuggingFaceEmbeddings(
        model_name=LOCAL_EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print(f"  ✅ Model ready!")
    print(f"  🔢 Total: {total} chunks | Done: {start} | Remaining: {total - start}")
    print(f"  ⚡ No rate limits — running at full speed!\n")

    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    vectorstore = None

    if start > 0:
        try:
            vectorstore = Chroma(
                collection_name=CHROMA_COLLECTION_NAME,
                embedding_function=embeddings,
                persist_directory=str(persist_dir),
            )
        except Exception:
            vectorstore = None

    for i in range(start, total, BATCH_SIZE):
        batch = chunks[i: i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"  📦 Batch {batch_num}/{total_batches} ({len(batch)} chunks)…", end=" ", flush=True)

        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                collection_name=CHROMA_COLLECTION_NAME,
                persist_directory=str(persist_dir),
            )
        else:
            vectorstore.add_documents(batch)

        print("✅")
        save_checkpoint(i + BATCH_SIZE, total)

    clear_checkpoint()
    count = vectorstore._collection.count() if vectorstore else 0
    print(f"\n✅ Ingestion complete! {count} vectors stored in ChromaDB.")
    print("   Run: uvicorn main:app --reload --port 8000")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Wipe and restart fresh")
    args = parser.parse_args()
    ingest(reset=args.reset)
