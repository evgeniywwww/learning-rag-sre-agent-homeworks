# Retrieval Examples

## Query 1

Query:
How should I handle a SEV1 incident?

Top-1:
sre_operations_policy_chunk_003 | score: 0.4731

Text preview:
SEV1:
- Production outage
- Immediate response required
- On-call engineer must be involved

Top-2:
sre_operations_policy_chunk_002 | score: 0.4370

Text preview:
All technical requests, incidents and infrastructure changes must be created through the official ticketing system.

Top-3:
incident_response_policy_chunk_001 | score: 0.3817

Text preview:
This document describes how engineering teams respond to production incidents.

Comment:
Partially relevant. Retrieval found SEV severity information, but incident_response_policy contains a more complete incident handling workflow.


---

## Query 2

Query:
What should I check when Kubernetes pod restarts?

Top-1:
kubernetes_operations_runbook_chunk_001 | score: 0.8786

Text preview:
When a Kubernetes pod restarts repeatedly, engineers should check:
- Pod events
- Restart count
- Container status

Top-2:
incident_response_policy_chunk_001 | score: 0.5109

Text preview:
Incidents can be detected through monitoring alerts, customer reports and automated health checks.

Top-3:
incident_response_policy_chunk_002 | score: 0.5050

Text preview:
Engineers should analyze application logs, infrastructure metrics, Kubernetes events and recent deployments.

Comment:
Highly relevant. The first result contains the expected Kubernetes troubleshooting procedure.


---

## Query 3

Query:
What are requirements for Tier 1 services?

Top-1:
service_tiers_and_sla_policy_chunk_001 | score: 0.6851

Text preview:
Tier 1 - Critical Services:
Payment systems, authentication services and core customer-facing APIs.

Top-2:
service_tiers_and_sla_policy_chunk_002 | score: 0.5552

Text preview:
Requirements:
- Business hours monitoring
- Defined support ownership
- Regular backups

Top-3:
sre_operations_policy_chunk_002 | score: 0.3641

Text preview:
All technical requests, incidents and infrastructure changes must be created through the official ticketing system.

Comment:
Relevant. Retrieval correctly identified the service classification document.


---

## Query 4

Query:
How can SRE improve reliability?

Top-1:
sre_improvement_strategy_chunk_001 | score: 0.7249

Text preview:
The SRE team continuously improves metrics coverage, logging quality, distributed tracing and alert quality.

Top-2:
sre_operations_policy_chunk_001 | score: 0.5502

Text preview:
The goal of SRE is to maintain reliable, scalable and observable systems.

Top-3:
sre_operations_policy_chunk_003 | score: 0.4796

Text preview:
Every major incident must have root cause analysis, timeline, corrective actions and prevention tasks.

Comment:
Relevant. The retrieval layer found the reliability improvement strategy document.


---

## Query 5

Query:
Who is responsible for production changes?

Top-1:
kubernetes_operations_runbook_chunk_002 | score: 0.5267

Text preview:
All production changes must be documented.

Top-2:
sre_operations_policy_chunk_003 | score: 0.4271

Text preview:
Production changes must follow change management principles.

Top-3:
service_tiers_and_sla_policy_chunk_002 | score: 0.3534

Text preview:
Defined support ownership and regular backups.

Comment:
Partially relevant. The current retrieval finds production change related information, but it does not identify ownership correctly. Metadata filtering or reranking could improve the result.