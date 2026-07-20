"""
Lesson 3 Demo 2: Chunk normalized documents with metadata.

Run from the project root:
    python scripts/lesson_03/02_chunk_documents.py

Purpose:
    Show how normalized documents can be split into chunks before embeddings.

This script reads:
    data/lesson_03/processed/normalized_documents.jsonl

And produces:
    data/lesson_03/processed/chunks.jsonl
"""

import json
from pathlib import Path
from typing import Any

INPUT_PATH = Path("data/processed/normalized_documents.jsonl")
OUTPUT_PATH = Path("data/processed/chunks.jsonl")
CHUNK_SIZE = 700
CHUNK_OVERLAP = 150


def load_jsonl(input_path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as input_file:
        for line in input_file:
            stripped_line = line.strip()
            if stripped_line:
                records.append(json.loads(stripped_line))
    return records


def save_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output_file:
        for record in records:
            output_file.write(json.dumps(record, ensure_ascii=False) + "\n")


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace while keeping readable section boundaries.
    """
    lines = [line.strip() for line in text.splitlines()]
    non_empty_lines = [line for line in lines if line]
    return "\n".join(non_empty_lines)


def split_text_with_overlap(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into chunks with character overlap.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    clean_text = normalize_whitespace(text)
    chunks: list[str] = []
    start = 0

    while start < len(clean_text):
        end = start + chunk_size
        chunk = clean_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks


def build_chunk_id(document_id: str, chunk_index: int) -> str:
    """Create a stable, predictable chunk ID."""
    return f"{document_id}_chunk_{chunk_index:03d}"


def chunk_document(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Split one normalized document into metadata-rich chunks."""
    text_chunks = split_text_with_overlap(document["text"])
    chunks: list[dict[str, Any]] = []

    for index, chunk_text in enumerate(text_chunks, start=1):
        chunks.append(
            {
                "chunk_id": build_chunk_id(document["document_id"], index),
                "text": chunk_text,
                "metadata": {
                    "document_id": document["document_id"],
                    "source_file": document["source_file"],
                    "source_type": document["source_type"],
                    "title": document["title"],
                    "chunk_index": index,
                    "language": document["metadata"].get("language"),
                    "domain": document["metadata"].get("domain"),
                    "document_type": document["metadata"].get("document_type"),
                },
            }
        )

    return chunks


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}. "
            "Please run 01_normalize_sources.py first."
        )

    documents = load_jsonl(INPUT_PATH)
    all_chunks: list[dict[str, Any]] = []
    for document in documents:
        all_chunks.extend(chunk_document(document))

    save_jsonl(all_chunks, OUTPUT_PATH)

    print("=" * 80)
    print("LESSON 3 DEMO 2: CHUNK DOCUMENTS")
    print("=" * 80)
    print(f"Input documents: {len(documents)}")
    print(f"Output chunks: {len(all_chunks)}")
    print(f"Chunk size: {CHUNK_SIZE} characters")
    print(f"Chunk overlap: {CHUNK_OVERLAP} characters")
    print(f"Output file: {OUTPUT_PATH}")
    print()

    for chunk in all_chunks[:3]:
        print("-" * 80)
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['metadata']['source_file']}")
        print(f"Chunk index: {chunk['metadata']['chunk_index']}")
        preview = chunk["text"][:220].replace("\n", " ")
        print(f"Text preview: {preview}...")


if __name__ == "__main__":
    main()
