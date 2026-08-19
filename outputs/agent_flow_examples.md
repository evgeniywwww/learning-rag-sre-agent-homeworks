# AI SRE Agent Flow Examples

## Use Case

A controlled AI SRE chatbot workflow that routes user questions either to static SRE knowledge, dynamic service monitoring data, or clarification.

## Workflow

```text
User question
    ↓
Router
    ├── policy_rag
    │      ↓
    │ search_sre_knowledge
    │      ↓
    │ observation
    │      ↓
    │ final answer
    │
    ├── service_status
    │      ↓
    │ get_service_status
    │      ↓
    │ observation
    │      ↓
    │ final answer
    │
    └── clarification
           ↓
       ask user to clarify
           ↓
       final answer
```

## Routes

- `policy_rag` — static SRE policies and runbooks
- `service_status` — current service health and monitoring data
- `clarification` — unclear or unsupported requests

## Mock Tools

- `search_sre_knowledge(question)`
- `get_service_status(service_name)`

## State

The workflow stores:

- `user_goal`
- `selected_route`
- `current_step`
- `completed_steps`
- `tool_calls`
- `observations`
- `intermediate_results`
- `final_answer`

## Examples

### Example 1

**Question:** What is our SEV1 incident response policy?

**Route:** `policy_rag`

**Tool called:**

- `search_sre_knowledge` with `{'question': 'What is our SEV1 incident response policy?'}`

**Observations:**

- `router`: `{'selected_route': 'policy_rag'}`
- `search_sre_knowledge`: `{'found': True, 'chunk_id': 'incident_response_policy_chunk_001', 'source_file': 'data/raw/incident_response_policy.md', 'content': 'SEV1 incidents require immediate response, coordination with the SRE team, incident tracking, root cause analysis and corrective actions.'}`

**State after workflow:**

```python
{'user_goal': 'What is our SEV1 incident response policy?', 'selected_route': 'policy_rag', 'current_step': 'final_answer', 'completed_steps': ['route_request', 'search_sre_knowledge', 'final_answer'], 'tool_calls': [{'tool_name': 'search_sre_knowledge', 'arguments': {'question': 'What is our SEV1 incident response policy?'}}], 'observations': [{'source': 'router', 'data': {'selected_route': 'policy_rag'}}, {'source': 'search_sre_knowledge', 'data': {'found': True, 'chunk_id': 'incident_response_policy_chunk_001', 'source_file': 'data/raw/incident_response_policy.md', 'content': 'SEV1 incidents require immediate response, coordination with the SRE team, incident tracking, root cause analysis and corrective actions.'}}], 'final_answer': 'SEV1 incidents require immediate response, coordination with the SRE team, incident tracking, root cause analysis and corrective actions. Source: incident_response_policy_chunk_001 (data/raw/incident_response_policy.md).'}
```

**Final answer:**

SEV1 incidents require immediate response, coordination with the SRE team, incident tracking, root cause analysis and corrective actions. Source: incident_response_policy_chunk_001 (data/raw/incident_response_policy.md).

---

### Example 2

**Question:** What should I check when a Kubernetes pod restarts repeatedly?

**Route:** `policy_rag`

**Tool called:**

- `search_sre_knowledge` with `{'question': 'What should I check when a Kubernetes pod restarts repeatedly?'}`

**Observations:**

- `router`: `{'selected_route': 'policy_rag'}`
- `search_sre_knowledge`: `{'found': True, 'chunk_id': 'kubernetes_operations_runbook_chunk_001', 'source_file': 'data/raw/kubernetes_operations_runbook.md', 'content': 'When a Kubernetes pod restarts repeatedly, check pod events, restart count, container status, application logs and recent configuration changes.'}`

**State after workflow:**

```python
{'user_goal': 'What should I check when a Kubernetes pod restarts repeatedly?', 'selected_route': 'policy_rag', 'current_step': 'final_answer', 'completed_steps': ['route_request', 'search_sre_knowledge', 'final_answer'], 'tool_calls': [{'tool_name': 'search_sre_knowledge', 'arguments': {'question': 'What should I check when a Kubernetes pod restarts repeatedly?'}}], 'observations': [{'source': 'router', 'data': {'selected_route': 'policy_rag'}}, {'source': 'search_sre_knowledge', 'data': {'found': True, 'chunk_id': 'kubernetes_operations_runbook_chunk_001', 'source_file': 'data/raw/kubernetes_operations_runbook.md', 'content': 'When a Kubernetes pod restarts repeatedly, check pod events, restart count, container status, application logs and recent configuration changes.'}}], 'final_answer': 'When a Kubernetes pod restarts repeatedly, check pod events, restart count, container status, application logs and recent configuration changes. Source: kubernetes_operations_runbook_chunk_001 (data/raw/kubernetes_operations_runbook.md).'}
```

**Final answer:**

When a Kubernetes pod restarts repeatedly, check pod events, restart count, container status, application logs and recent configuration changes. Source: kubernetes_operations_runbook_chunk_001 (data/raw/kubernetes_operations_runbook.md).

---

### Example 3

**Question:** What is the current status of payment-service?

**Route:** `service_status`

**Tool called:**

- `get_service_status` with `{'service_name': 'payment-service'}`

**Observations:**

- `router`: `{'selected_route': 'service_status'}`
- `get_service_status`: `{'found': True, 'service_name': 'payment-service', 'environment': 'production', 'status': 'degraded', 'replicas_ready': 2, 'replicas_desired': 3, 'p95_latency_ms': 1850, 'error_rate_percent': 4.7}`

**State after workflow:**

```python
{'user_goal': 'What is the current status of payment-service?', 'selected_route': 'service_status', 'current_step': 'final_answer', 'completed_steps': ['route_request', 'get_service_status', 'final_answer'], 'tool_calls': [{'tool_name': 'get_service_status', 'arguments': {'service_name': 'payment-service'}}], 'observations': [{'source': 'router', 'data': {'selected_route': 'service_status'}}, {'source': 'get_service_status', 'data': {'found': True, 'service_name': 'payment-service', 'environment': 'production', 'status': 'degraded', 'replicas_ready': 2, 'replicas_desired': 3, 'p95_latency_ms': 1850, 'error_rate_percent': 4.7}}], 'final_answer': 'Service payment-service in production is currently degraded. Ready replicas: 2/3. p95 latency: 1850 ms. Error rate: 4.7%.'}
```

**Final answer:**

Service payment-service in production is currently degraded. Ready replicas: 2/3. p95 latency: 1850 ms. Error rate: 4.7%.

---

### Example 4

**Question:** What is the current latency of auth-service?

**Route:** `service_status`

**Tool called:**

- `get_service_status` with `{'service_name': 'auth-service'}`

**Observations:**

- `router`: `{'selected_route': 'service_status'}`
- `get_service_status`: `{'found': True, 'service_name': 'auth-service', 'environment': 'production', 'status': 'healthy', 'replicas_ready': 3, 'replicas_desired': 3, 'p95_latency_ms': 180, 'error_rate_percent': 0.2}`

**State after workflow:**

```python
{'user_goal': 'What is the current latency of auth-service?', 'selected_route': 'service_status', 'current_step': 'final_answer', 'completed_steps': ['route_request', 'get_service_status', 'final_answer'], 'tool_calls': [{'tool_name': 'get_service_status', 'arguments': {'service_name': 'auth-service'}}], 'observations': [{'source': 'router', 'data': {'selected_route': 'service_status'}}, {'source': 'get_service_status', 'data': {'found': True, 'service_name': 'auth-service', 'environment': 'production', 'status': 'healthy', 'replicas_ready': 3, 'replicas_desired': 3, 'p95_latency_ms': 180, 'error_rate_percent': 0.2}}], 'final_answer': 'Service auth-service in production is currently healthy. Ready replicas: 3/3. p95 latency: 180 ms. Error rate: 0.2%.'}
```

**Final answer:**

Service auth-service in production is currently healthy. Ready replicas: 3/3. p95 latency: 180 ms. Error rate: 0.2%.

---

### Example 5

**Question:** Tell me something interesting.

**Route:** `clarification`

**Tool called:**

- No external/mock tool called.

**Observations:**

- `router`: `{'selected_route': 'clarification'}`
- `clarification`: `{'message': 'The request does not clearly match a policy/runbook question or a current service-status question.'}`

**State after workflow:**

```python
{'user_goal': 'Tell me something interesting.', 'selected_route': 'clarification', 'current_step': 'final_answer', 'completed_steps': ['route_request', 'clarification', 'final_answer'], 'tool_calls': [], 'observations': [{'source': 'router', 'data': {'selected_route': 'clarification'}}, {'source': 'clarification', 'data': {'message': 'The request does not clearly match a policy/runbook question or a current service-status question.'}}], 'final_answer': 'Could you please clarify your request? Are you asking about an SRE policy/runbook or the current status of a specific service?'}
```

**Final answer:**

Could you please clarify your request? Are you asking about an SRE policy/runbook or the current status of a specific service?

---

