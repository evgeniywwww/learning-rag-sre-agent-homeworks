"""
AI SRE RAG: Metadata Filtering Evaluation

Compare:
1. Baseline semantic retrieval
2. Semantic retrieval with metadata filtering

Generate markdown evaluation report.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNKS_PATH = PROJECT_ROOT / "data/processed/chunks_for_retrieval.jsonl"
INDEX_PATH = PROJECT_ROOT / "index/faiss.index"
OUTPUT_PATH = PROJECT_ROOT / "outputs/retrieval_improvement.md"


TOP_K = 3
CANDIDATE_K = 10


# Improvement we test
METADATA_FILTER = {
    "document_type": "policy",
}


# Same queries for baseline and improved retrieval
TEST_CASES = [
    {
        "query": "How should I handle a production incident?",
        "expected_document": "incident_response_policy",
    },
    {
        "query": "What are Tier 1 service requirements?",
        "expected_document": "service_tiers_and_sla_policy",
    },
    {
        "query": "How can SRE improve reliability?",
        "expected_document": "sre_improvement_strategy",
    },
    {
        "query": "Who approves production changes?",
        "expected_document": "sre_operations_policy",
    },
    {
        "query": "How to troubleshoot Kubernetes pod restart?",
        "expected_document": "kubernetes_operations_runbook",
    },
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def normalize_embedding(embedding):

    embedding = embedding.astype("float32")

    faiss.normalize_L2(
        embedding
    )

    return embedding


def semantic_search(
    query: str,
    model: SentenceTransformer,
    index: faiss.Index,
    chunks: list[dict[str, Any]],
    top_k: int,
):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
    )

    query_embedding = normalize_embedding(
        query_embedding
    )

    scores, indices = index.search(
        query_embedding,
        top_k,
    )

    results = []

    for score, idx in zip(
        scores[0],
        indices[0],
    ):

        if idx == -1:
            continue

        chunk = chunks[int(idx)]

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


def apply_metadata_filter(
    results,
):

    filtered = []

    for result in results:

        metadata = result["metadata"]

        matches = True

        for key, value in METADATA_FILTER.items():

            if metadata.get(key) != value:
                matches = False

        if matches:
            filtered.append(result)

    return filtered[:TOP_K]


def get_document_id(results):

    if not results:
        return "none"

    return results[0]["metadata"].get(
        "document_id",
        "unknown",
    )


def get_score(results):

    if not results:
        return 0.0

    return results[0]["score"]


def evaluate_result(
    expected,
    baseline,
    filtered,
):

    baseline_doc = get_document_id(
        baseline
    )

    filtered_doc = get_document_id(
        filtered
    )

    if (
        baseline_doc != expected
        and filtered_doc == expected
    ):
        return "Improved"

    if (
        baseline_doc == expected
        and filtered_doc == expected
    ):
        return "No change"

    if (
        baseline_doc == expected
        and filtered_doc != expected
    ):
        return "Worse"

    return "No improvement"


def save_markdown_report(rows):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "# Retrieval Improvement: Metadata Filtering\n\n"
        )

        file.write(
            "Baseline semantic retrieval compared with retrieval using metadata filtering.\n\n"
        )

        file.write(
            f"Metadata filter used: `{METADATA_FILTER}`\n\n"
        )

        file.write(
            "| Query | Expected | Baseline top-1 | Filter top-1 | Baseline score | Filter score | Result |\n"
        )

        file.write(
            "|---|---|---|---|---|---|---|\n"
        )

        for row in rows:

            file.write(
                f"| {row['query']} "
                f"| {row['expected']} "
                f"| {row['baseline']} "
                f"| {row['filtered']} "
                f"| {row['baseline_score']:.4f} "
                f"| {row['filtered_score']:.4f} "
                f"| {row['result']} |\n"
            )

        file.write("\n\n")

        file.write(
            "## Conclusion\n\n"
        )

        file.write(
            "Metadata filtering was evaluated against the same test queries. "
            "The goal was to check whether limiting the search space improves retrieval precision.\n"
        )


def main():

    chunks = load_jsonl(
        CHUNKS_PATH
    )

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    rows = []

    print("=" * 80)
    print("AI SRE RAG: METADATA FILTERING EVALUATION")
    print("=" * 80)

    print(
        f"Filter: {METADATA_FILTER}"
    )


    for case in TEST_CASES:

        query = case["query"]
        expected = case["expected_document"]

        print("\n")
        print("-" * 80)

        print(
            f"Query: {query}"
        )

        print(
            f"Expected: {expected}"
        )


        baseline = semantic_search(
            query,
            model,
            index,
            chunks,
            TOP_K,
        )


        candidates = semantic_search(
            query,
            model,
            index,
            chunks,
            CANDIDATE_K,
        )


        filtered = apply_metadata_filter(
            candidates
        )


        result = evaluate_result(
            expected,
            baseline,
            filtered,
        )


        print(
            f"Baseline: {get_document_id(baseline)}"
        )

        print(
            f"Filtered: {get_document_id(filtered)}"
        )

        print(
            f"Result: {result}"
        )


        rows.append(
            {
                "query": query,
                "expected": expected,
                "baseline": get_document_id(baseline),
                "filtered": get_document_id(filtered),
                "baseline_score": get_score(baseline),
                "filtered_score": get_score(filtered),
                "result": result,
            }
        )


    save_markdown_report(
        rows
    )


    print()
    print("=" * 80)
    print(
        f"Report saved: {OUTPUT_PATH}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()