"""
Build FAISS vector index for AI SRE RAG knowledge base.

Run from project root:

    python scripts/04_build_faiss_index.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Input
INPUT_CHUNKS_PATH = PROJECT_ROOT / "data/processed/chunks.jsonl"

# Output directories
PROCESSED_DIR = PROJECT_ROOT / "data/processed"
INDEX_DIR = PROJECT_ROOT / "index"

# Output files
OUTPUT_CHUNKS_PATH = PROCESSED_DIR / "chunks_for_retrieval.jsonl"
OUTPUT_EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
OUTPUT_INDEX_PATH = INDEX_DIR / "faiss.index"


def path_for_display(path: Path) -> str:
    """Return project-relative path when possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def load_jsonl(input_path: Path) -> list[dict[str, Any]]:
    """Load JSONL records from disk."""
    records: list[dict[str, Any]] = []

    with input_path.open("r", encoding="utf-8") as input_file:
        for line in input_file:
            stripped_line = line.strip()
            if stripped_line:
                records.append(json.loads(stripped_line))

    return records


def save_jsonl(
    records: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Save records as JSONL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as output_file:
        for record in records:
            output_file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )


def normalize_embeddings(
    embeddings: np.ndarray,
) -> np.ndarray:
    """
    Normalize vectors so FAISS IndexFlatIP behaves
    like cosine similarity search.
    """
    embeddings = embeddings.astype("float32")
    faiss.normalize_L2(embeddings)
    return embeddings


def main() -> None:
    if not INPUT_CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Input chunks file not found: {INPUT_CHUNKS_PATH}. "
            "Please run normalization and chunking scripts first."
        )

    print("=" * 80)
    print("AI SRE RAG: BUILD FAISS INDEX")
    print("=" * 80)

    print(
        f"Input chunks: "
        f"{path_for_display(INPUT_CHUNKS_PATH)}"
    )
    print(f"Embedding model: {MODEL_NAME}")
    print()

    print("Loading chunks...")

    chunks = load_jsonl(INPUT_CHUNKS_PATH)

    if not chunks:
        raise ValueError(
            "No chunks found. Please check the input chunks file."
        )

    print(f"Chunks loaded: {len(chunks)}")
    print()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print()
    print("Creating embeddings...")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    print(
        f"Raw embeddings shape: {embeddings.shape}"
    )

    normalized_embeddings = normalize_embeddings(
        embeddings
    )

    embedding_dimension = normalized_embeddings.shape[1]

    print(
        f"Embedding dimension: {embedding_dimension}"
    )

    print()
    print("Building FAISS index with IndexFlatIP...")

    index = faiss.IndexFlatIP(
        embedding_dimension
    )

    index.add(
        normalized_embeddings
    )

    # Create directories
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    INDEX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Save artifacts

    np.save(
        OUTPUT_EMBEDDINGS_PATH,
        normalized_embeddings,
    )

    faiss.write_index(
        index,
        str(OUTPUT_INDEX_PATH),
    )

    save_jsonl(
        chunks,
        OUTPUT_CHUNKS_PATH,
    )

    print()
    print("-" * 80)
    print("Saved outputs")
    print("-" * 80)

    print(
        f"Chunks for retrieval: "
        f"{path_for_display(OUTPUT_CHUNKS_PATH)}"
    )

    print(
        f"Embeddings matrix: "
        f"{path_for_display(OUTPUT_EMBEDDINGS_PATH)}"
    )

    print(
        f"FAISS index: "
        f"{path_for_display(OUTPUT_INDEX_PATH)}"
    )

    print()
    print("-" * 80)
    print("Index summary")
    print("-" * 80)

    print(
        f"Index type: {type(index).__name__}"
    )

    print(
        f"Vectors in index: {index.ntotal}"
    )

    print(
        f"Vector dimension: {embedding_dimension}"
    )

    print()

    print(
        "FAISS stores vectors for similarity search."
    )

    print(
        "Chunk text and metadata are stored separately in JSONL."
    )


if __name__ == "__main__":
    main()