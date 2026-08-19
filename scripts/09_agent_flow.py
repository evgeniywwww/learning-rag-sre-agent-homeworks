"""
Homework 6: First controlled agentic workflow for AI SRE Assistant.

Pipeline:
user goal
-> route
-> workflow step
-> tool call
-> observation
-> state update
-> next step
-> final answer

"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "outputs/agent_flow_examples.md"


RouteName = Literal[
    "policy_rag",
    "service_status",
    "clarification",
]

StepName = Literal[
    "route_request",
    "search_sre_knowledge",
    "get_service_status",
    "clarification",
    "final_answer",
]


# ---------------------------------------------------------------------------
# State models
# ---------------------------------------------------------------------------

@dataclass
class ToolCall:
    tool_name: str
    arguments: dict[str, Any]


@dataclass
class Observation:
    source: str
    data: dict[str, Any]


@dataclass
class AgentState:
    """
    Explicit state for the controlled SRE workflow.
    """

    user_goal: str

    selected_route: RouteName | None = None
    current_step: StepName | None = None

    completed_steps: list[StepName] = field(
        default_factory=list
    )

    tool_calls: list[ToolCall] = field(
        default_factory=list
    )

    observations: list[Observation] = field(
        default_factory=list
    )

    intermediate_results: dict[str, Any] = field(
        default_factory=dict
    )

    final_answer: str | None = None


# ---------------------------------------------------------------------------
# Mock knowledge source
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


# ---------------------------------------------------------------------------
# Mock monitoring source
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
    Mock RAG-like tool.

    Used for static SRE knowledge:
    policies, procedures and runbooks.
    """

    text = question.lower()

    if "sev1" in text or "incident" in text:
        return {
            "found": True,
            **MOCK_SRE_KNOWLEDGE["sev1"],
        }

    if (
        "pod" in text
        or "restart" in text
        or "kubernetes" in text
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
    Mock monitoring tool.

    Used for dynamic runtime data:
    health, latency, replicas and error rate.
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
# Routing
# ---------------------------------------------------------------------------

def route_request(
    question: str,
) -> RouteName:
    """
    Deterministic rule-based router.
    """

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
        return "policy_rag"

    if any(
        keyword in text
        for keyword in service_keywords
    ):
        return "service_status"

    return "clarification"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def record_tool_call(
    state: AgentState,
    tool_name: str,
    arguments: dict[str, Any],
) -> None:

    state.tool_calls.append(
        ToolCall(
            tool_name=tool_name,
            arguments=arguments,
        )
    )


def record_observation(
    state: AgentState,
    source: str,
    data: dict[str, Any],
) -> None:

    state.observations.append(
        Observation(
            source=source,
            data=data,
        )
    )


def mark_step_completed(
    state: AgentState,
    step: StepName,
) -> None:

    state.completed_steps.append(
        step
    )


def extract_service_name(
    question: str,
) -> str | None:
    """
    Extract known service name from user question.
    """

    text = question.lower()

    for service_name in MOCK_SERVICES:
        if service_name in text:
            return service_name

    return None


# ---------------------------------------------------------------------------
# Workflow steps
# ---------------------------------------------------------------------------

def run_policy_workflow(
    state: AgentState,
) -> None:

    state.current_step = "search_sre_knowledge"

    record_tool_call(
        state,
        "search_sre_knowledge",
        {
            "question": state.user_goal,
        },
    )

    result = search_sre_knowledge(
        state.user_goal
    )

    record_observation(
        state,
        "search_sre_knowledge",
        result,
    )

    state.intermediate_results[
        "policy_result"
    ] = result

    mark_step_completed(
        state,
        "search_sre_knowledge",
    )


def run_service_status_workflow(
    state: AgentState,
) -> None:

    state.current_step = "get_service_status"

    service_name = extract_service_name(
        state.user_goal
    )

    if service_name is None:
        observation = {
            "found": False,
            "reason": (
                "Service name could not be identified "
                "from the user request."
            ),
        }

        record_observation(
            state,
            "get_service_status",
            observation,
        )

        state.intermediate_results[
            "service_result"
        ] = observation

        mark_step_completed(
            state,
            "get_service_status",
        )

        return

    record_tool_call(
        state,
        "get_service_status",
        {
            "service_name": service_name,
        },
    )

    result = get_service_status(
        service_name
    )

    record_observation(
        state,
        "get_service_status",
        result,
    )

    state.intermediate_results[
        "service_result"
    ] = result

    mark_step_completed(
        state,
        "get_service_status",
    )


def run_clarification_workflow(
    state: AgentState,
) -> None:

    state.current_step = "clarification"

    observation = {
        "message": (
            "The request does not clearly match "
            "a policy/runbook question or a current "
            "service-status question."
        )
    }

    record_observation(
        state,
        "clarification",
        observation,
    )

    mark_step_completed(
        state,
        "clarification",
    )


# ---------------------------------------------------------------------------
# Final answer
# ---------------------------------------------------------------------------

def build_final_answer(
    state: AgentState,
) -> str:

    if state.selected_route == "policy_rag":

        result = state.intermediate_results.get(
            "policy_result",
            {},
        )

        if not result.get("found"):
            return (
                "I could not find enough information "
                "in the available SRE knowledge base."
            )

        return (
            f"{result['content']} "
            f"Source: {result['chunk_id']} "
            f"({result['source_file']})."
        )

    if state.selected_route == "service_status":

        result = state.intermediate_results.get(
            "service_result",
            {},
        )

        if not result.get("found"):
            return (
                "Unable to retrieve current service status: "
                f"{result.get('reason', 'unknown error')}."
            )

        return (
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

    return (
        "Could you please clarify your request? "
        "Are you asking about an SRE policy/runbook "
        "or the current status of a specific service?"
    )


# ---------------------------------------------------------------------------
# Conductor / orchestration
# ---------------------------------------------------------------------------

def run_agent_flow(
    user_goal: str,
) -> AgentState:
    """
    Controlled agentic workflow.

    The conductor controls:
    1. routing
    2. workflow execution
    3. state updates
    4. final answer generation
    """

    state = AgentState(
        user_goal=user_goal
    )

    # Step 1: route
    state.current_step = "route_request"

    state.selected_route = route_request(
        user_goal
    )

    record_observation(
        state,
        "router",
        {
            "selected_route": (
                state.selected_route
            )
        },
    )

    mark_step_completed(
        state,
        "route_request",
    )

    # Step 2: execute selected workflow
    if state.selected_route == "policy_rag":

        run_policy_workflow(
            state
        )

    elif state.selected_route == "service_status":

        run_service_status_workflow(
            state
        )

    else:

        run_clarification_workflow(
            state
        )

    # Step 3: final answer
    state.current_step = "final_answer"

    state.final_answer = build_final_answer(
        state
    )

    mark_step_completed(
        state,
        "final_answer",
    )

    return state


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

TEST_QUESTIONS = [
    "What is our SEV1 incident response policy?",
    "What should I check when a Kubernetes pod restarts repeatedly?",
    "What is the current status of payment-service?",
    "What is the current latency of auth-service?",
    "Tell me something interesting.",
]


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def state_to_dict(
    state: AgentState,
) -> dict[str, Any]:

    return {
        "user_goal": state.user_goal,
        "selected_route": state.selected_route,
        "current_step": state.current_step,
        "completed_steps": state.completed_steps,
        "tool_calls": [
            {
                "tool_name": call.tool_name,
                "arguments": call.arguments,
            }
            for call in state.tool_calls
        ],
        "observations": [
            {
                "source": observation.source,
                "data": observation.data,
            }
            for observation in state.observations
        ],
        "final_answer": state.final_answer,
    }


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
            "# AI SRE Agent Flow Examples\n\n"
        )

        file.write(
            "## Use Case\n\n"
        )

        file.write(
            "A controlled AI SRE chatbot workflow that routes "
            "user questions either to static SRE knowledge, "
            "dynamic service monitoring data, or clarification.\n\n"
        )

        file.write(
            "## Workflow\n\n"
        )

        file.write(
            "```text\n"
            "User question\n"
            "    ↓\n"
            "Router\n"
            "    ├── policy_rag\n"
            "    │      ↓\n"
            "    │ search_sre_knowledge\n"
            "    │      ↓\n"
            "    │ observation\n"
            "    │      ↓\n"
            "    │ final answer\n"
            "    │\n"
            "    ├── service_status\n"
            "    │      ↓\n"
            "    │ get_service_status\n"
            "    │      ↓\n"
            "    │ observation\n"
            "    │      ↓\n"
            "    │ final answer\n"
            "    │\n"
            "    └── clarification\n"
            "           ↓\n"
            "       ask user to clarify\n"
            "           ↓\n"
            "       final answer\n"
            "```\n\n"
        )

        file.write(
            "## Routes\n\n"
        )

        file.write(
            "- `policy_rag` — static SRE policies and runbooks\n"
            "- `service_status` — current service health and monitoring data\n"
            "- `clarification` — unclear or unsupported requests\n\n"
        )

        file.write(
            "## Mock Tools\n\n"
        )

        file.write(
            "- `search_sre_knowledge(question)`\n"
            "- `get_service_status(service_name)`\n\n"
        )

        file.write(
            "## State\n\n"
        )

        file.write(
            "The workflow stores:\n\n"
        )

        file.write(
            "- `user_goal`\n"
            "- `selected_route`\n"
            "- `current_step`\n"
            "- `completed_steps`\n"
            "- `tool_calls`\n"
            "- `observations`\n"
            "- `intermediate_results`\n"
            "- `final_answer`\n\n"
        )

        file.write(
            "## Examples\n\n"
        )

        for index, state in enumerate(
            states,
            start=1,
        ):

            file.write(
                f"### Example {index}\n\n"
            )

            file.write(
                f"**Question:** {state.user_goal}\n\n"
            )

            file.write(
                f"**Route:** `{state.selected_route}`\n\n"
            )

            file.write(
                "**Tool called:**\n\n"
            )

            if state.tool_calls:
                for call in state.tool_calls:
                    file.write(
                        f"- `{call.tool_name}` "
                        f"with `{call.arguments}`\n"
                    )
            else:
                file.write(
                    "- No external/mock tool called.\n"
                )

            file.write("\n")

            file.write(
                "**Observations:**\n\n"
            )

            for observation in state.observations:
                file.write(
                    f"- `{observation.source}`: "
                    f"`{observation.data}`\n"
                )

            file.write("\n")

            file.write(
                "**State after workflow:**\n\n"
            )

            file.write(
                "```python\n"
                f"{state_to_dict(state)}\n"
                "```\n\n"
            )

            file.write(
                "**Final answer:**\n\n"
            )

            file.write(
                f"{state.final_answer}\n\n"
            )

            file.write(
                "---\n\n"
            )


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def print_state_summary(
    state: AgentState,
) -> None:

    print("=" * 80)
    print(f"Question: {state.user_goal}")
    print("=" * 80)

    print(
        f"Route: {state.selected_route}"
    )

    print(
        f"Completed steps: "
        f"{state.completed_steps}"
    )

    print()

    print("Tool calls:")

    if not state.tool_calls:
        print("- none")

    for call in state.tool_calls:
        print(
            f"- {call.tool_name}: "
            f"{call.arguments}"
        )

    print()

    print("Observations:")

    for observation in state.observations:
        print(
            f"- {observation.source}: "
            f"{observation.data}"
        )

    print()

    print("Final answer:")
    print(
        state.final_answer
    )

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:

    states = []

    print("=" * 80)
    print("AI SRE: CONTROLLED AGENT FLOW")
    print("=" * 80)
    print()

    for question in TEST_QUESTIONS:

        state = run_agent_flow(
            question
        )

        states.append(
            state
        )

        print_state_summary(
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