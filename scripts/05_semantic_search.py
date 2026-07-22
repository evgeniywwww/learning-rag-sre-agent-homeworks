"""
Semantic search for AI SRE RAG knowledge base.

Run from project root:

    python scripts/05_semantic_search.py
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

# Input artifacts
CHUNKS_PATH = PROJECT_ROOT / "data/processed/chunks_for_retrieval.jsonl"
INDEX_PATH = PROJECT_ROOT / "index/faiss.index"

TOP_K = 3


def path_for_display(path: Path) -> str:
    """Return project-relative path when possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def load_jsonl(
    input_path: Path,
) -> list[dict[str, Any]]:
    """Load JSONL records from disk."""
    records: list[dict[str, Any]] = []

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as input_file:
        for line in input_file:
            stripped_line = line.strip()
            if stripped_line:
                records.append(json.loads(stripped_line))

    return records


def normalize_query_embedding(
    embedding: np.ndarray,
) -> np.ndarray:
    """
    Normalize query vector so IndexFlatIP behaves
    like cosine similarity search.
    """
    embedding = embedding.astype("float32")
    faiss.normalize_L2(embedding)
    return embedding


def search(
    query: str,
    model: SentenceTransformer,
    index: faiss.Index,
    chunks: list[dict[str, Any]],
    top_k: int = TOP_K,
) -> list[dict[str, Any]]:
    """
    Perform semantic search and return matching chunks.
    """

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
    )

    query_embedding = normalize_query_embedding(
        query_embedding
    )

    scores, indices = index.search(
        query_embedding,
        top_k,
    )

    results: list[dict[str, Any]] = []

    for score, chunk_index in zip(
        scores[0],
        indices[0],
    ):
        if chunk_index == -1:
            continue

        chunk = chunks[int(chunk_index)]

        results.append(
            {
                "score": float(score),
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": chunk.get(
                    "metadata",
                    {},
                ),
            }
        )

    return results


def main() -> None:

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_PATH}"
        )

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_PATH}"
        )


    print("=" * 80)
    print("AI SRE RAG: SEMANTIC SEARCH")
    print("=" * 80)

    print(
        f"Embedding model: {MODEL_NAME}"
    )

    print(
        f"FAISS index: {path_for_display(INDEX_PATH)}"
    )

    print(
        f"Chunks file: {path_for_display(CHUNKS_PATH)}"
    )

    print()


    chunks = load_jsonl(
        CHUNKS_PATH
    )

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    model = SentenceTransformer(
        MODEL_NAME
    )


    queries = [
        "How should I handle a SEV1 incident?",
        "What should I check when Kubernetes pod restarts?",
        "What are requirements for Tier 1 services?",
        "How can SRE improve reliability?",
        "Who is responsible for production changes?",
    ]


    for query in queries:

        print("=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        results = search(
            query=query,
            model=model,
            index=index,
            chunks=chunks,
            top_k=TOP_K,
        )


        for rank, result in enumerate(
            results,
            start=1,
        ):
            metadata = result["metadata"]

            print(
                f"\nRank: {rank}"
            )

            print(
                f"Score: {result['score']:.4f}"
            )

            print(
                f"Chunk ID: {result['chunk_id']}"
            )

            print(
                f"Source: {metadata.get('source_file')}"
            )

            print(
                f"Title: {metadata.get('title')}"
            )

            print(
                "Text preview:"
            )

            print(
                result["text"][:300]
            )

        print()


if __name__ == "__main__":
    main()