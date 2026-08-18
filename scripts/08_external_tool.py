"""
Homework 5: External Tool Integration for AI SRE Assistant.

Pipeline:
user request
-> orchestration / routing
-> structured tool request
-> validation
-> external source (mock monitoring system)
-> normalized observation
-> final answer
-> markdown report

Run from project root:

    python scripts/08_external_tool.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "outputs/tool_examples.md"

ToolType = Literal["read"]


# ---------------------------------------------------------------------------
# Tool contracts
# ---------------------------------------------------------------------------

@dataclass
class ToolRequest:
    """
    Structured request from orchestration layer to the tool layer.
    """

    tool_name: str
    tool_type: ToolType
    payload: dict[str, Any]


@dataclass
class ToolObservation:
    """
    Normalized result returned from tool layer.
    """

    tool_name: str
    success: bool
    data: dict[str, Any]
    error: str | None = None


# ---------------------------------------------------------------------------
# Mock external monitoring source
# ---------------------------------------------------------------------------

MOCK_SERVICES = {
    "payment-service": {
        "service_name": "payment-service",
        "environment": "production",
        "status": "degraded",
        "replicas_ready": 2,
        "replicas_desired": 3,
        "p95_latency_ms": 1850,
        "error_rate_percent": 4.7,
        "last_updated": "2026-08-18T10:00:00Z",
    },
    "auth-service": {
        "service_name": "auth-service",
        "environment": "production",
        "status": "healthy",
        "replicas_ready": 3,
        "replicas_desired": 3,
        "p95_latency_ms": 180,
        "error_rate_percent": 0.2,
        "last_updated": "2026-08-18T10:00:00Z",
    },
    "reporting-service": {
        "service_name": "reporting-service",
        "environment": "stage",
        "status": "healthy",
        "replicas_ready": 1,
        "replicas_desired": 1,
        "p95_latency_ms": 420,
        "error_rate_percent": 0.5,
        "last_updated": "2026-08-18T10:00:00Z",
    },
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

ALLOWED_ENVIRONMENTS = {
    "development",
    "stage",
    "production",
}


def validate_service_name(service_name: Any) -> str | None:
    """
    Validate service name before tool execution.
    """

    if not isinstance(service_name, str):
        return "service_name must be a string."

    service_name = service_name.strip()

    if not service_name:
        return "service_name is required."

    if len(service_name) > 100:
        return "service_name is too long."

    allowed_characters = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789-_"
    )

    if any(
        char not in allowed_characters
        for char in service_name
    ):
        return (
            "service_name contains invalid characters. "
            "Only letters, numbers, '-' and '_' are allowed."
        )

    return None


def validate_environment(environment: Any) -> str | None:
    """
    Validate environment.
    """

    if not isinstance(environment, str):
        return "environment must be a string."

    if environment not in ALLOWED_ENVIRONMENTS:
        return (
            "Invalid environment. "
            "Allowed values: development, stage, production."
        )

    return None


def validate_tool_request(
    request: ToolRequest,
) -> str | None:
    """
    Validate structured tool request before execution.
    """

    if request.tool_name != "get_service_status":
        return "Unknown tool."

    service_name_error = validate_service_name(
        request.payload.get("service_name")
    )

    if service_name_error:
        return service_name_error

    environment_error = validate_environment(
        request.payload.get("environment")
    )

    if environment_error:
        return environment_error

    return None


# ---------------------------------------------------------------------------
# Tool implementation
# ---------------------------------------------------------------------------

def get_service_status(
    service_name: str,
    environment: str,
) -> ToolObservation:
    """
    Tool: get_service_status

    Type:
        Read tool.

    Purpose:
        Return current operational status and monitoring metrics
        for a specific service.

    Source:
        Mock monitoring system.

    When useful:
        Questions about current service health, latency,
        error rate, replica availability or environment status.

    When NOT useful:
        General SRE policies, incident procedures,
        service tier definitions or static documentation.
        Those questions should use RAG retrieval instead.
    """

    service = MOCK_SERVICES.get(
        service_name
    )

    if service is None:
        return ToolObservation(
            tool_name="get_service_status",
            success=False,
            data={},
            error=(
                f"Service '{service_name}' "
                "was not found in monitoring data."
            ),
        )

    if service["environment"] != environment:
        return ToolObservation(
            tool_name="get_service_status",
            success=False,
            data={},
            error=(
                f"Service '{service_name}' exists, "
                f"but not in environment '{environment}'."
            ),
        )

    return ToolObservation(
        tool_name="get_service_status",
        success=True,
        data=service,
    )


# ---------------------------------------------------------------------------
# Integration layer
# ---------------------------------------------------------------------------

def execute_tool_request(
    request: ToolRequest,
) -> ToolObservation:
    """
    Validate request and execute the external tool.
    """

    validation_error = validate_tool_request(
        request
    )

    if validation_error:
        return ToolObservation(
            tool_name=request.tool_name,
            success=False,
            data={},
            error=validation_error,
        )

    return get_service_status(
        service_name=request.payload["service_name"],
        environment=request.payload["environment"],
    )


# ---------------------------------------------------------------------------
# Simple orchestration layer
# ---------------------------------------------------------------------------

def route_user_request(
    user_question: str,
) -> ToolRequest | None:
    """
    Simple deterministic router.

    In a real agent this decision could be made by an LLM
    or orchestration framework.
    """

    text = user_question.lower()

    if (
        "payment-service" in text
        and (
            "status" in text
            or "health" in text
            or "latency" in text
            or "error" in text
        )
    ):
        return ToolRequest(
            tool_name="get_service_status",
            tool_type="read",
            payload={
                "service_name": "payment-service",
                "environment": "production",
            },
        )

    if (
        "auth-service" in text
        and (
            "status" in text
            or "health" in text
            or "latency" in text
            or "error" in text
        )
    ):
        return ToolRequest(
            tool_name="get_service_status",
            tool_type="read",
            payload={
                "service_name": "auth-service",
                "environment": "production",
            },
        )

    if (
        "reporting-service" in text
        and (
            "status" in text
            or "health" in text
            or "latency" in text
        )
    ):
        return ToolRequest(
            tool_name="get_service_status",
            tool_type="read",
            payload={
                "service_name": "reporting-service",
                "environment": "stage",
            },
        )

    return None


# ---------------------------------------------------------------------------
# Final answer
# ---------------------------------------------------------------------------

def build_final_answer(
    observation: ToolObservation,
) -> str:
    """
    Build deterministic user-facing answer from normalized observation.
    """

    if not observation.success:
        return (
            f"Unable to retrieve service status: "
            f"{observation.error}"
        )

    data = observation.data

    return (
        f"Service {data['service_name']} in "
        f"{data['environment']} is currently "
        f"{data['status']}. "
        f"Ready replicas: "
        f"{data['replicas_ready']}/"
        f"{data['replicas_desired']}. "
        f"p95 latency: {data['p95_latency_ms']} ms. "
        f"Error rate: "
        f"{data['error_rate_percent']}%. "
        f"Last updated: {data['last_updated']}."
    )


# ---------------------------------------------------------------------------
# Demo test cases
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "user_question": (
            "What is the current status "
            "of payment-service?"
        ),
        "manual_request": None,
        "why_tool": (
            "Service health is dynamic monitoring data. "
            "A static RAG knowledge base cannot reliably provide "
            "the current status, latency or error rate."
        ),
    },
    {
        "user_question": (
            "What is the current latency "
            "of auth-service?"
        ),
        "manual_request": None,
        "why_tool": (
            "Latency changes continuously and must come "
            "from a monitoring source rather than static documents."
        ),
    },
    {
        "user_question": (
            "What is the status of reporting-service "
            "in stage?"
        ),
        "manual_request": None,
        "why_tool": (
            "Environment-specific runtime state is dynamic data "
            "and should be read through a tool."
        ),
    },
    {
        "user_question": (
            "What is the current status "
            "of billing-service?"
        ),
        "manual_request": ToolRequest(
            tool_name="get_service_status",
            tool_type="read",
            payload={
                "service_name": "billing-service",
                "environment": "production",
            },
        ),
        "why_tool": (
            "The tool can verify whether the service currently "
            "exists in the monitoring source and return a safe error."
        ),
    },
    {
        "user_question": (
            "What is our SEV1 incident response policy?"
        ),
        "manual_request": None,
        "why_tool": (
            "This is static policy knowledge, so the external "
            "status tool is not appropriate. RAG retrieval should "
            "be used instead."
        ),
    },
]


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def format_result(
    observation: ToolObservation | None,
) -> str:
    if observation is None:
        return "Tool not called."

    if observation.success:
        return str(observation.data)

    return str(
        {
            "success": False,
            "error": observation.error,
        }
    )


def save_report(
    rows: list[dict[str, Any]],
) -> None:
    """
    Save homework examples in Markdown format.
    """

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "# External Tool Integration Examples\n\n"
        )

        file.write(
            "## Tool Description\n\n"
        )

        file.write(
            "**Name:** `get_service_status`\n\n"
        )

        file.write(
            "**Type:** read tool\n\n"
        )

        file.write(
            "**Purpose:** Returns current service health "
            "and monitoring metrics from a mock monitoring source.\n\n"
        )

        file.write(
            "**When to use:** For current service status, "
            "latency, error rate and replica health.\n\n"
        )

        file.write(
            "**When NOT to use:** For static SRE policies, "
            "runbooks or service definitions. "
            "Use RAG retrieval for those questions.\n\n"
        )

        file.write(
            "## Input Contract\n\n"
        )

        file.write(
            "```json\n"
            "{\n"
            '  "service_name": "payment-service",\n'
            '  "environment": "production"\n'
            "}\n"
            "```\n\n"
        )

        file.write(
            "## Output Contract\n\n"
        )

        file.write(
            "```json\n"
            "{\n"
            '  "service_name": "payment-service",\n'
            '  "environment": "production",\n'
            '  "status": "degraded",\n'
            '  "replicas_ready": 2,\n'
            '  "replicas_desired": 3,\n'
            '  "p95_latency_ms": 1850,\n'
            '  "error_rate_percent": 4.7,\n'
            '  "last_updated": "2026-08-18T10:00:00Z"\n'
            "}\n"
            "```\n\n"
        )

        file.write(
            "## Validation\n\n"
        )

        file.write(
            "- `service_name` is required.\n"
            "- Only letters, numbers, `-` and `_` are allowed.\n"
            "- `environment` must be one of: "
            "`development`, `stage`, `production`.\n"
            "- Unknown tools are rejected.\n"
            "- The tool is read-only and does not accept raw SQL "
            "or write actions.\n\n"
        )

        file.write(
            "## Examples\n\n"
        )

        for index, row in enumerate(
            rows,
            start=1,
        ):

            file.write(
                f"### Example {index}\n\n"
            )

            file.write(
                f"**User question:** "
                f"{row['user_question']}\n\n"
            )

            file.write(
                f"**Tool called:** "
                f"{row['tool_called']}\n\n"
            )

            file.write(
                f"**Input:** "
                f"`{row['tool_input']}`\n\n"
            )

            file.write(
                f"**Result:** "
                f"`{row['result']}`\n\n"
            )

            file.write(
                "**Final answer:**\n\n"
            )

            file.write(
                f"{row['final_answer']}\n\n"
            )

            file.write(
                "**Why tool is better than retrieval:**\n\n"
            )

            file.write(
                f"{row['why_tool']}\n\n"
            )

            file.write(
                "---\n\n"
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:

    report_rows = []

    print("=" * 80)
    print("AI SRE: EXTERNAL TOOL INTEGRATION")
    print("=" * 80)

    for test_case in TEST_CASES:

        user_question = test_case[
            "user_question"
        ]

        print()
        print("-" * 80)
        print(
            f"User question: {user_question}"
        )

        request = test_case[
            "manual_request"
        ]

        if request is None:
            request = route_user_request(
                user_question
            )

        if request is None:
            tool_called = "not called"
            tool_input = {}
            observation = None

            final_answer = (
                "This question should use RAG retrieval "
                "because it asks about static SRE knowledge."
            )

        else:
            tool_called = request.tool_name
            tool_input = request.payload

            observation = execute_tool_request(
                request
            )

            final_answer = build_final_answer(
                observation
            )

        print(
            f"Tool called: {tool_called}"
        )

        print(
            f"Input: {tool_input}"
        )

        print(
            f"Result: {format_result(observation)}"
        )

        print(
            f"Final answer: {final_answer}"
        )

        report_rows.append(
            {
                "user_question": user_question,
                "tool_called": tool_called,
                "tool_input": tool_input,
                "result": format_result(
                    observation
                ),
                "final_answer": final_answer,
                "why_tool": test_case[
                    "why_tool"
                ],
            }
        )

    save_report(
        report_rows
    )

    print()
    print("=" * 80)
    print(
        f"Report saved: {OUTPUT_PATH}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()