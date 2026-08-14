"""
Lesson 6 - AI SRE RAG: Grounded QA pipeline.

Pipeline:
question -> retrieval -> prompt -> LLM -> grounded answer

"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import faiss
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_LLM_MODEL = "gpt-4.1-mini"

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHUNKS_PATH = PROJECT_ROOT / "data/processed/chunks_for_retrieval.jsonl"
INDEX_PATH = PROJECT_ROOT / "index/faiss.index"

OUTPUT_PATH = PROJECT_ROOT / "outputs/rag_answers_examples.md"

TOP_K = 3


TEST_CASES = [
    {
        "question": "What should I check when a Kubernetes pod restarts repeatedly?",
        "comment": "Direct question. Expected answer exists in the Kubernetes runbook.",
    },
    {
        "question": "What are the requirements for Tier 1 services?",
        "comment": "Direct policy question.",
    },
    {
        "question": "What steps should an engineer take during a serious production incident?",
        "comment": "Paraphrased incident-response question.",
    },
    {
        "question": "What should the SRE team improve to make systems more reliable?",
        "comment": "Paraphrased reliability-improvement question.",
    },
    {
        "question": "Who approves production changes?",
        "comment": "Known weak retrieval case.",
    },
    {
        "question": "What is our AWS disaster recovery policy?",
        "comment": "Fallback test. Knowledge base does not contain this information.",
    },
    {
        "question": "How many vacation days do SRE engineers receive?",
        "comment": "Fallback test. Question is outside the SRE knowledge base.",
    },
]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def require_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. "
            "Create a .env file or export OPENAI_API_KEY before running the script."
        )


def normalize_embedding(embedding):
    embedding = embedding.astype("float32")
    faiss.normalize_L2(embedding)
    return embedding


# ---------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------

def retrieve(
    question: str,
    embedding_model: SentenceTransformer,
    index: faiss.Index,
    chunks: list[dict[str, Any]],
    top_k: int = TOP_K,
) -> list[dict[str, Any]]:

    query_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True,
    )

    query_embedding = normalize_embedding(query_embedding)

    scores, indices = index.search(
        query_embedding,
        top_k,
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        chunk = chunks[int(idx)]

        results.append(
            {
                "score": float(score),
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": chunk.get("metadata", {}),
            }
        )

    return results


# ---------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------

def build_context(
    retrieved_chunks: list[dict[str, Any]],
) -> str:

    context_parts = []

    for result in retrieved_chunks:

        metadata = result["metadata"]

        context_parts.append(
            "\n".join(
                [
                    f"Source chunk ID: {result['chunk_id']}",
                    f"Source file: {metadata.get('source_file', 'unknown')}",
                    f"Title: {metadata.get('title', 'unknown')}",
                    f"Content:",
                    result["text"],
                ]
            )
        )

    return "\n\n---\n\n".join(context_parts)


# ---------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------

def build_grounded_prompt(
    question: str,
    context: str,
) -> str:

    return f"""
You are an AI SRE knowledge assistant.

Your task is to answer the user's question using only the provided context.

Rules:
- Answer only using information explicitly supported by the provided context.
- Do not use external knowledge.
- Do not invent missing information or make unsupported assumptions.
- Answer only what the user asked. Do not add unrelated information from retrieved chunks.
- Cite only the chunk IDs or source files that directly support your answer.
- Do not cite retrieved chunks that were not actually used.
- If the context does not contain enough information to answer the question, say exactly:
  "I do not have enough information in the available SRE documents to answer this question."
- When using the fallback response, do not present unrelated retrieved chunks as evidence.
- Keep the answer concise and practical.

Context:
{context}

User question:
{question}

Answer:
""".strip()


# ---------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------

def call_llm(
    client: OpenAI,
    model: str,
    prompt: str,
) -> str:

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    return response.output_text


# ---------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------

def save_report(
    rows: list[dict[str, Any]],
) -> None:

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write("# RAG Answer Examples\n\n")

        file.write(
            "Grounded QA examples using FAISS retrieval and an LLM prompt.\n\n"
        )

        for number, row in enumerate(rows, start=1):

            file.write(f"## Example {number}\n\n")

            file.write(
                f"**Question:** {row['question']}\n\n"
            )

            file.write("**Retrieved chunks:**\n\n")

            for result in row["retrieved"]:

                file.write(
                    f"- `{result['chunk_id']}` "
                    f"(score: {result['score']:.4f})\n"
                )

            file.write("\n")

            file.write("**Answer:**\n\n")
            file.write(row["answer"])
            file.write("\n\n")

            file.write("**Sources:**\n\n")

            for result in row["retrieved"]:

                file.write(
                    f"- `{result['metadata'].get('source_file', 'unknown')}`\n"
                )

            file.write("\n")

            file.write(
                f"**Comment:** {row['comment']}\n\n"
            )

            file.write("---\n\n")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:

    load_dotenv()
    require_api_key()

    llm_model = os.getenv(
        "OPENAI_MODEL",
        DEFAULT_LLM_MODEL,
    )

    print("=" * 80)
    print("AI SRE RAG: GROUNDED QA")
    print("=" * 80)

    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"LLM model: {llm_model}")
    print()

    chunks = load_jsonl(
        CHUNKS_PATH
    )

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    client = OpenAI()

    rows = []

    for test_case in TEST_CASES:

        question = test_case["question"]

        print()
        print("-" * 80)
        print(f"QUESTION: {question}")
        print("-" * 80)

        retrieved = retrieve(
            question=question,
            embedding_model=embedding_model,
            index=index,
            chunks=chunks,
        )

        context = build_context(
            retrieved
        )

        prompt = build_grounded_prompt(
            question=question,
            context=context,
        )

        answer = call_llm(
            client=client,
            model=llm_model,
            prompt=prompt,
        )

        print("\nRetrieved:")

        for result in retrieved:
            print(
                f"- {result['chunk_id']} "
                f"| score={result['score']:.4f}"
            )

        print("\nAnswer:")
        print(answer)

        rows.append(
            {
                "question": question,
                "retrieved": retrieved,
                "answer": answer,
                "comment": test_case["comment"],
            }
        )

    save_report(rows)

    print()
    print("=" * 80)
    print(f"Report saved: {OUTPUT_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()