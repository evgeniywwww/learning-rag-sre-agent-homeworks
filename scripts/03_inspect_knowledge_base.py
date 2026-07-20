"""
Lesson 3 Demo 3: Inspect prepared knowledge base.

Run from the project root:
    python scripts/lesson_03/03_inspect_knowledge_base.py

Purpose:
    Show why chunks should be inspected before embeddings.

This script reads:
    data/lesson_03/processed/chunks.jsonl
"""

import json
from collections import Counter
from pathlib import Path
from typing import Any

CHUNKS_PATH = Path("data/lesson_03/processed/chunks.jsonl")
MIN_REASONABLE_CHUNK_LENGTH = 80
MAX_REASONABLE_CHUNK_LENGTH = 1200
REQUIRED_METADATA_FIELDS = [
    "document_id",
    "source_file",
    "source_type",
    "title",
    "chunk_index",
]


def load_jsonl(input_path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as input_file:
        for line in input_file:
            stripped_line = line.strip()
            if stripped_line:
                records.append(json.loads(stripped_line))
    return records


def check_metadata_coverage(chunks: list[dict[str, Any]]) -> dict[str, int]:
    """Count chunks that have each required metadata field."""
    coverage: dict[str, int] = {}
    for field in REQUIRED_METADATA_FIELDS:
        coverage[field] = sum(
            1
            for chunk in chunks
            if chunk.get("metadata", {}).get(field) not in (None, "")
        )
    return coverage


def find_suspicious_chunks(chunks: list[dict[str, Any]]) -> list[str]:
    """
    Produce simple warnings for chunk quality checks.
    """
    warnings: list[str] = []
    for chunk in chunks:
        chunk_id = chunk.get("chunk_id", "<missing_id>")
        text = chunk.get("text", "")
        text_length = len(text)

        if text_length < MIN_REASONABLE_CHUNK_LENGTH:
            warnings.append(f"{chunk_id}: very short chunk ({text_length} characters)")
        if text_length > MAX_REASONABLE_CHUNK_LENGTH:
            warnings.append(f"{chunk_id}: very long chunk ({text_length} characters)")
        if not chunk.get("metadata"):
            warnings.append(f"{chunk_id}: missing metadata")

        for field in REQUIRED_METADATA_FIELDS:
            if chunk.get("metadata", {}).get(field) in (None, ""):
                warnings.append(f"{chunk_id}: missing metadata field '{field}'")

    return warnings


def main() -> None:
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_PATH}. "
            "Please run 01_normalize_sources.py and 02_chunk_documents.py first."
        )

    chunks = load_jsonl(CHUNKS_PATH)
    if not chunks:
        print("No chunks found.")
        return

    document_ids = [
        chunk["metadata"]["document_id"]
        for chunk in chunks
        if chunk.get("metadata", {}).get("document_id")
    ]
    chunk_lengths = [len(chunk["text"]) for chunk in chunks]
    average_length = sum(chunk_lengths) / len(chunk_lengths)
    source_distribution = Counter(document_ids)
    metadata_coverage = check_metadata_coverage(chunks)
    warnings = find_suspicious_chunks(chunks)

    print("=" * 80)
    print("LESSON 3 DEMO 3: INSPECT KNOWLEDGE BASE")
    print("=" * 80)
    print(f"Chunks file: {CHUNKS_PATH}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Source documents: {len(set(document_ids))}")
    print(f"Average chunk length: {average_length:.1f} characters")
    print()

    print("-" * 80)
    print("Chunks per document")
    print("-" * 80)
    for document_id, count in source_distribution.items():
        print(f"{document_id}: {count}")
    print()

    print("-" * 80)
    print("Metadata coverage")
    print("-" * 80)
    for field, count in metadata_coverage.items():
        print(f"{field}: {count}/{len(chunks)} chunks")
    print()

    print("-" * 80)
    print("Warnings")
    print("-" * 80)
    if warnings:
        for warning in warnings[:10]:
            print(f"WARNING: {warning}")
        if len(warnings) > 10:
            print(f"... and {len(warnings) - 10} more warnings")
    else:
        print("No obvious issues found.")
    print()

    print("-" * 80)
    print("Example chunks")
    print("-" * 80)
    for chunk in chunks[:3]:
        print()
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['metadata']['source_file']}")
        print(f"Title: {chunk['metadata']['title']}")
        print("Text:")
        print(chunk["text"][:500])


if __name__ == "__main__":
    main()
