# External Tool Integration Examples

## Tool Description

**Name:** `get_service_status`

**Type:** read tool

**Purpose:** Returns current service health and monitoring metrics from a mock monitoring source.

**When to use:** For current service status, latency, error rate and replica health.

**When NOT to use:** For static SRE policies, runbooks or service definitions. Use RAG retrieval for those questions.

## Input Contract

```json
{
  "service_name": "payment-service",
  "environment": "production"
}
```

## Output Contract

```json
{
  "service_name": "payment-service",
  "environment": "production",
  "status": "degraded",
  "replicas_ready": 2,
  "replicas_desired": 3,
  "p95_latency_ms": 1850,
  "error_rate_percent": 4.7,
  "last_updated": "2026-08-18T10:00:00Z"
}
```

## Validation

- `service_name` is required.
- Only letters, numbers, `-` and `_` are allowed.
- `environment` must be one of: `development`, `stage`, `production`.
- Unknown tools are rejected.
- The tool is read-only and does not accept raw SQL or write actions.

## Examples

### Example 1

**User question:** What is the current status of payment-service?

**Tool called:** get_service_status

**Input:** `{'service_name': 'payment-service', 'environment': 'production'}`

**Result:** `{'service_name': 'payment-service', 'environment': 'production', 'status': 'degraded', 'replicas_ready': 2, 'replicas_desired': 3, 'p95_latency_ms': 1850, 'error_rate_percent': 4.7, 'last_updated': '2026-08-18T10:00:00Z'}`

**Final answer:**

Service payment-service in production is currently degraded. Ready replicas: 2/3. p95 latency: 1850 ms. Error rate: 4.7%. Last updated: 2026-08-18T10:00:00Z.

**Why tool is better than retrieval:**

Service health is dynamic monitoring data. A static RAG knowledge base cannot reliably provide the current status, latency or error rate.

---

### Example 2

**User question:** What is the current latency of auth-service?

**Tool called:** get_service_status

**Input:** `{'service_name': 'auth-service', 'environment': 'production'}`

**Result:** `{'service_name': 'auth-service', 'environment': 'production', 'status': 'healthy', 'replicas_ready': 3, 'replicas_desired': 3, 'p95_latency_ms': 180, 'error_rate_percent': 0.2, 'last_updated': '2026-08-18T10:00:00Z'}`

**Final answer:**

Service auth-service in production is currently healthy. Ready replicas: 3/3. p95 latency: 180 ms. Error rate: 0.2%. Last updated: 2026-08-18T10:00:00Z.

**Why tool is better than retrieval:**

Latency changes continuously and must come from a monitoring source rather than static documents.

---

### Example 3

**User question:** What is the status of reporting-service in stage?

**Tool called:** get_service_status

**Input:** `{'service_name': 'reporting-service', 'environment': 'stage'}`

**Result:** `{'service_name': 'reporting-service', 'environment': 'stage', 'status': 'healthy', 'replicas_ready': 1, 'replicas_desired': 1, 'p95_latency_ms': 420, 'error_rate_percent': 0.5, 'last_updated': '2026-08-18T10:00:00Z'}`

**Final answer:**

Service reporting-service in stage is currently healthy. Ready replicas: 1/1. p95 latency: 420 ms. Error rate: 0.5%. Last updated: 2026-08-18T10:00:00Z.

**Why tool is better than retrieval:**

Environment-specific runtime state is dynamic data and should be read through a tool.

---

### Example 4

**User question:** What is the current status of billing-service?

**Tool called:** get_service_status

**Input:** `{'service_name': 'billing-service', 'environment': 'production'}`

**Result:** `{'success': False, 'error': "Service 'billing-service' was not found in monitoring data."}`

**Final answer:**

Unable to retrieve service status: Service 'billing-service' was not found in monitoring data.

**Why tool is better than retrieval:**

The tool can verify whether the service currently exists in the monitoring source and return a safe error.

---

### Example 5

**User question:** What is our SEV1 incident response policy?

**Tool called:** not called

**Input:** `{}`

**Result:** `Tool not called.`

**Final answer:**

This question should use RAG retrieval because it asks about static SRE knowledge.

**Why tool is better than retrieval:**

This is static policy knowledge, so the external status tool is not appropriate. RAG retrieval should be used instead.

---

