"""
Homework 7: AI SRE workflow implemented with LangGraph.

Framework implementation:
    State
    -> classify_request
    -> conditional route
    -> policy_rag / service_status / clarification
    -> build_answer
    -> END
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "outputs/langgraph_examples.md"

Route = Literal[
    "policy_rag",
    "service_status",
    "clarification",
]


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict, total=False):
    """
    Shared LangGraph workflow state.
    """

    user_question: str
    selected_route: Route

    service_name: str | None

    tool_result: dict[str, Any] | None

    executed_nodes: list[str]

    final_answer: str | None


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

MOCK_SRE_KNOWLEDGE = {
    "sev1": {
        "chunk_id": "incident_response_policy_chunk_001",
        "source_file": "data/raw/incident_response_policy.md",
        "content": (
            "SEV1 incidents require immediate response, "
            "coordination with the SRE team, incident tracking, "
            "root cause analysis and corrective actions."
        ),
    },
    "pod_restart": {
        "chunk_id": "kubernetes_operations_runbook_chunk_001",
        "source_file": "data/raw/kubernetes_operations_runbook.md",
        "content": (
            "When a Kubernetes pod restarts repeatedly, "
            "check pod events, restart count, container status, "
            "application logs and recent configuration changes."
        ),
    },
}


MOCK_SERVICES = {
    "payment-service": {
        "service_name": "payment-service",
        "environment": "production",
        "status": "degraded",
        "replicas_ready": 2,
        "replicas_desired": 3,
        "p95_latency_ms": 1850,
        "error_rate_percent": 4.7,
    },
    "auth-service": {
        "service_name": "auth-service",
        "environment": "production",
        "status": "healthy",
        "replicas_ready": 3,
        "replicas_desired": 3,
        "p95_latency_ms": 180,
        "error_rate_percent": 0.2,
    },
}


# ---------------------------------------------------------------------------
# Mock tools
# ---------------------------------------------------------------------------

def search_sre_knowledge(
    question: str,
) -> dict[str, Any]:
    """
    Mock RAG-like tool for static SRE knowledge.
    """

    text = question.lower()

    if "sev1" in text or "incident" in text:
        return {
            "found": True,
            **MOCK_SRE_KNOWLEDGE["sev1"],
        }

    if any(
        word in text
        for word in [
            "pod",
            "restart",
            "kubernetes",
        ]
    ):
        return {
            "found": True,
            **MOCK_SRE_KNOWLEDGE["pod_restart"],
        }

    return {
        "found": False,
        "reason": "No matching SRE knowledge found.",
    }


def get_service_status(
    service_name: str,
) -> dict[str, Any]:
    """
    Mock monitoring tool for dynamic service state.
    """

    service = MOCK_SERVICES.get(
        service_name
    )

    if service is None:
        return {
            "found": False,
            "reason": (
                f"Service '{service_name}' "
                "was not found in monitoring data."
            ),
        }

    return {
        "found": True,
        **service,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def append_node(
    state: AgentState,
    node_name: str,
) -> list[str]:
    """
    Track executed nodes for homework tracing.
    """

    return [
        *state.get("executed_nodes", []),
        node_name,
    ]


def extract_service_name(
    question: str,
) -> str | None:
    """
    Extract a known service name from user question.
    """

    text = question.lower()

    for service_name in MOCK_SERVICES:
        if service_name in text:
            return service_name

    return None


# ---------------------------------------------------------------------------
# LangGraph nodes
# ---------------------------------------------------------------------------

def classify_request(
    state: AgentState,
) -> dict[str, Any]:
    """
    Node 1:
    Determine which workflow route should be used.
    """

    question = state["user_question"]
    text = question.lower()

    policy_keywords = [
        "policy",
        "sev1",
        "incident",
        "runbook",
        "kubernetes",
        "pod",
        "restart",
    ]

    service_keywords = [
        "status",
        "health",
        "latency",
        "error rate",
        "replicas",
    ]

    if any(
        keyword in text
        for keyword in policy_keywords
    ):
        route: Route = "policy_rag"

    elif any(
        keyword in text
        for keyword in service_keywords
    ):
        route = "service_status"

    else:
        route = "clarification"

    return {
        "selected_route": route,
        "service_name": extract_service_name(
            question
        ),
        "executed_nodes": append_node(
            state,
            "classify_request",
        ),
    }


def run_policy_rag(
    state: AgentState,
) -> dict[str, Any]:
    """
    Node 2A:
    Search static SRE knowledge.
    """

    result = search_sre_knowledge(
        state["user_question"]
    )

    return {
        "tool_result": result,
        "executed_nodes": append_node(
            state,
            "run_policy_rag",
        ),
    }


def run_service_status(
    state: AgentState,
) -> dict[str, Any]:
    """
    Node 2B:
    Query current service monitoring state.
    """

    service_name = state.get(
        "service_name"
    )

    if not service_name:
        result = {
            "found": False,
            "reason": (
                "Service name could not be identified "
                "from the user question."
            ),
        }
    else:
        result = get_service_status(
            service_name
        )

    return {
        "tool_result": result,
        "executed_nodes": append_node(
            state,
            "run_service_status",
        ),
    }


def ask_clarification(
    state: AgentState,
) -> dict[str, Any]:
    """
    Node 2C:
    Fallback route for unclear requests.
    """

    result = {
        "message": (
            "The request does not clearly match "
            "an SRE policy/runbook question or "
            "a current service-status question."
        )
    }

    return {
        "tool_result": result,
        "executed_nodes": append_node(
            state,
            "ask_clarification",
        ),
    }


def build_answer(
    state: AgentState,
) -> dict[str, Any]:
    """
    Final node:
    Build deterministic answer from current state.
    """

    route = state.get(
        "selected_route"
    )

    result = state.get(
        "tool_result"
    ) or {}

    if route == "policy_rag":

        if not result.get("found"):
            answer = (
                "I could not find enough information "
                "in the available SRE knowledge base."
            )

        else:
            answer = (
                f"{result['content']} "
                f"Source: {result['chunk_id']} "
                f"({result['source_file']})."
            )

    elif route == "service_status":

        if not result.get("found"):
            answer = (
                "Unable to retrieve current service status: "
                f"{result.get('reason', 'unknown error')}"
            )

        else:
            answer = (
                f"Service {result['service_name']} in "
                f"{result['environment']} is currently "
                f"{result['status']}. "
                f"Ready replicas: "
                f"{result['replicas_ready']}/"
                f"{result['replicas_desired']}. "
                f"p95 latency: "
                f"{result['p95_latency_ms']} ms. "
                f"Error rate: "
                f"{result['error_rate_percent']}%."
            )

    else:

        answer = (
            "Could you please clarify your request? "
            "Are you asking about an SRE policy/runbook "
            "or the current status of a specific service?"
        )

    return {
        "final_answer": answer,
        "executed_nodes": append_node(
            state,
            "build_answer",
        ),
    }


# ---------------------------------------------------------------------------
# Conditional edge
# ---------------------------------------------------------------------------

def route_after_classification(
    state: AgentState,
) -> str:
    """
    Conditional edge.

    LangGraph equivalent of the if/elif routing
    from the previous custom implementation.
    """

    route = state.get(
        "selected_route"
    )

    if route == "policy_rag":
        return "run_policy_rag"

    if route == "service_status":
        return "run_service_status"

    return "ask_clarification"


# ---------------------------------------------------------------------------
# Build LangGraph workflow
# ---------------------------------------------------------------------------

def build_graph():
    """
    Graph:

                       START
                         ↓
                  classify_request
                    /     |      \
                   /      |       \
                  ↓       ↓        ↓
             policy    status   clarification
                ↓         ↓         ↓
          run_policy   run_status   ask
                \         |        /
                 \        |       /
                     build_answer
                          ↓
                         END
    """

    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "classify_request",
        classify_request,
    )

    graph.add_node(
        "run_policy_rag",
        run_policy_rag,
    )

    graph.add_node(
        "run_service_status",
        run_service_status,
    )

    graph.add_node(
        "ask_clarification",
        ask_clarification,
    )

    graph.add_node(
        "build_answer",
        build_answer,
    )

    # START -> classification
    graph.add_edge(
        START,
        "classify_request",
    )

    # Conditional routing
    graph.add_conditional_edges(
        "classify_request",
        route_after_classification,
        {
            "run_policy_rag": "run_policy_rag",
            "run_service_status": "run_service_status",
            "ask_clarification": "ask_clarification",
        },
    )

    # Every route ends in answer builder
    graph.add_edge(
        "run_policy_rag",
        "build_answer",
    )

    graph.add_edge(
        "run_service_status",
        "build_answer",
    )

    graph.add_edge(
        "ask_clarification",
        "build_answer",
    )

    graph.add_edge(
        "build_answer",
        END,
    )

    return graph.compile()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

TEST_QUESTIONS = [
    "What is our SEV1 incident response policy?",
    "What is the current status of payment-service?",
    "Tell me something interesting.",
]


def run_case(
    compiled_graph: Any,
    question: str,
) -> AgentState:
    """
    Run one test case and return final graph state.
    """

    initial_state: AgentState = {
        "user_question": question,
        "executed_nodes": [],
        "tool_result": None,
        "final_answer": None,
    }

    final_state = compiled_graph.invoke(
        initial_state
    )

    return final_state


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def print_case(
    state: AgentState,
) -> None:

    print("=" * 80)
    print(
        f"Input: {state['user_question']}"
    )
    print("=" * 80)

    print(
        f"Route: {state.get('selected_route')}"
    )

    print()

    print("Executed nodes:")

    for node in state.get(
        "executed_nodes",
        [],
    ):
        print(
            f"- {node}"
        )

    print()

    print("Tool result:")
    print(
        state.get("tool_result")
    )

    print()

    print("Final answer:")
    print(
        state.get("final_answer")
    )

    print()


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def save_report(
    states: list[AgentState],
) -> None:

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "# LangGraph Workflow Examples\n\n"
        )

        file.write(
            "## Framework Choice\n\n"
        )

        file.write(
            "LangGraph was selected because the previous "
            "AI SRE workflow already uses explicit state, "
            "routing and multiple execution branches. "
            "LangGraph represents these concepts directly "
            "through State, Nodes, Edges and Conditional Edges.\n\n"
        )

        file.write(
            "## Workflow\n\n"
        )

        file.write(
            "```text\n"
            "START\n"
            "  ↓\n"
            "classify_request\n"
            "  ├── policy_rag → run_policy_rag ──────┐\n"
            "  ├── service_status → run_service_status ├→ build_answer → END\n"
            "  └── clarification → ask_clarification ┘\n"
            "```\n\n"
        )

        file.write(
            "## State\n\n"
        )

        file.write(
            "The graph state stores:\n\n"
            "- `user_question`\n"
            "- `selected_route`\n"
            "- `service_name`\n"
            "- `tool_result`\n"
            "- `executed_nodes`\n"
            "- `final_answer`\n\n"
        )

        file.write(
            "## Test Examples\n\n"
        )

        for index, state in enumerate(
            states,
            start=1,
        ):

            file.write(
                f"### Example {index}\n\n"
            )

            file.write(
                f"**Input question:** "
                f"{state['user_question']}\n\n"
            )

            file.write(
                f"**Selected route:** "
                f"`{state.get('selected_route')}`\n\n"
            )

            file.write(
                "**Executed nodes:**\n\n"
            )

            for node in state.get(
                "executed_nodes",
                [],
            ):
                file.write(
                    f"- `{node}`\n"
                )

            file.write("\n")

            file.write(
                "**Final state:**\n\n"
            )

            file.write(
                "```python\n"
                f"{state}\n"
                "```\n\n"
            )

            file.write(
                "**Final answer:**\n\n"
            )

            file.write(
                f"{state.get('final_answer')}\n\n"
            )

            file.write(
                "---\n\n"
            )

        file.write(
            "## Custom Flow vs LangGraph\n\n"
        )

        file.write(
            "| Aspect | Custom Python Flow | LangGraph |\n"
            "| --- | --- | --- |\n"
            "| Workflow structure | Implemented with if/else and function calls | Explicit nodes and edges |\n"
            "| State | Managed manually | Shared typed graph state |\n"
            "| Routing | if/elif logic | Conditional edge |\n"
            "| Debugging | Requires reading control flow and logs | Executed graph path is more explicit |\n"
            "| Complexity | Simpler for this small workflow | More boilerplate for a small example |\n"
            "| Scaling | Becomes harder with many branches/retries | Better suited for larger stateful workflows |\n\n"
        )

        file.write(
            "### Conclusion\n\n"
        )

        file.write(
            "For the current small AI SRE workflow, the custom "
            "Python implementation is simpler and requires less code. "
            "LangGraph adds some boilerplate, but makes the workflow "
            "structure, state and conditional routing more explicit. "
            "Its advantages become more significant when the workflow "
            "grows to include additional branches, retries, checkpoints, "
            "human approval or long-running state.\n"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:

    print("=" * 80)
    print("AI SRE: LANGGRAPH WORKFLOW")
    print("=" * 80)
    print()

    compiled_graph = build_graph()

    states = []

    for question in TEST_QUESTIONS:

        state = run_case(
            compiled_graph,
            question,
        )

        states.append(
            state
        )

        print_case(
            state
        )

    save_report(
        states
    )

    print("=" * 80)
    print(
        f"Report saved: {OUTPUT_PATH}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()