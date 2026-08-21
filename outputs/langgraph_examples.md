# LangGraph Workflow Examples

## Framework Choice

LangGraph was selected because the previous AI SRE workflow already uses explicit state, routing and multiple execution branches. LangGraph represents these concepts directly through State, Nodes, Edges and Conditional Edges.

## Workflow

```text
START
  ↓
classify_request
  ├── policy_rag → run_policy_rag ──────┐
  ├── service_status → run_service_status ├→ build_answer → END
  └── clarification → ask_clarification ┘
```

## State

The graph state stores:

- `user_question`
- `selected_route`
- `service_name`
- `tool_result`
- `executed_nodes`
- `final_answer`

## Test Examples

### Example 1

**Input question:** What is our SEV1 incident response policy?

**Selected route:** `policy_rag`

**Executed nodes:**

- `classify_request`
- `run_policy_rag`
- `build_answer`

**Final state:**

```python
{'user_question': 'What is our SEV1 incident response policy?', 'selected_route': 'policy_rag', 'service_name': None, 'tool_result': {'found': True, 'chunk_id': 'incident_response_policy_chunk_001', 'source_file': 'data/raw/incident_response_policy.md', 'content': 'SEV1 incidents require immediate response, coordination with the SRE team, incident tracking, root cause analysis and corrective actions.'}, 'executed_nodes': ['classify_request', 'run_policy_rag', 'build_answer'], 'final_answer': 'SEV1 incidents require immediate response, coordination with the SRE team, incident tracking, root cause analysis and corrective actions. Source: incident_response_policy_chunk_001 (data/raw/incident_response_policy.md).'}
```

**Final answer:**

SEV1 incidents require immediate response, coordination with the SRE team, incident tracking, root cause analysis and corrective actions. Source: incident_response_policy_chunk_001 (data/raw/incident_response_policy.md).

---

### Example 2

**Input question:** What is the current status of payment-service?

**Selected route:** `service_status`

**Executed nodes:**

- `classify_request`
- `run_service_status`
- `build_answer`

**Final state:**

```python
{'user_question': 'What is the current status of payment-service?', 'selected_route': 'service_status', 'service_name': 'payment-service', 'tool_result': {'found': True, 'service_name': 'payment-service', 'environment': 'production', 'status': 'degraded', 'replicas_ready': 2, 'replicas_desired': 3, 'p95_latency_ms': 1850, 'error_rate_percent': 4.7}, 'executed_nodes': ['classify_request', 'run_service_status', 'build_answer'], 'final_answer': 'Service payment-service in production is currently degraded. Ready replicas: 2/3. p95 latency: 1850 ms. Error rate: 4.7%.'}
```

**Final answer:**

Service payment-service in production is currently degraded. Ready replicas: 2/3. p95 latency: 1850 ms. Error rate: 4.7%.

---

### Example 3

**Input question:** Tell me something interesting.

**Selected route:** `clarification`

**Executed nodes:**

- `classify_request`
- `ask_clarification`
- `build_answer`

**Final state:**

```python
{'user_question': 'Tell me something interesting.', 'selected_route': 'clarification', 'service_name': None, 'tool_result': {'message': 'The request does not clearly match an SRE policy/runbook question or a current service-status question.'}, 'executed_nodes': ['classify_request', 'ask_clarification', 'build_answer'], 'final_answer': 'Could you please clarify your request? Are you asking about an SRE policy/runbook or the current status of a specific service?'}
```

**Final answer:**

Could you please clarify your request? Are you asking about an SRE policy/runbook or the current status of a specific service?

---

## Custom Flow vs LangGraph

| Aspect | Custom Python Flow | LangGraph |
| --- | --- | --- |
| Workflow structure | Implemented with if/else and function calls | Explicit nodes and edges |
| State | Managed manually | Shared typed graph state |
| Routing | if/elif logic | Conditional edge |
| Debugging | Requires reading control flow and logs | Executed graph path is more explicit |
| Complexity | Simpler for this small workflow | More boilerplate for a small example |
| Scaling | Becomes harder with many branches/retries | Better suited for larger stateful workflows |

### Conclusion

For the current small AI SRE workflow, the custom Python implementation is simpler and requires less code. LangGraph adds some boilerplate, but makes the workflow structure, state and conditional routing more explicit. Its advantages become more significant when the workflow grows to include additional branches, retries, checkpoints, human approval or long-running state.
