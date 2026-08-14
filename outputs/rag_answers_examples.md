# RAG Answer Examples

Grounded QA examples using FAISS retrieval and an LLM prompt.

## Example 1

**Question:** What should I check when a Kubernetes pod restarts repeatedly?

**Retrieved chunks:**

- `kubernetes_operations_runbook_chunk_001` (score: 0.8732)
- `incident_response_policy_chunk_001` (score: 0.4920)
- `incident_response_policy_chunk_002` (score: 0.4808)

**Answer:**

When a Kubernetes pod restarts repeatedly, you should check:

1. Pod Status:
   - Pod events
   - Restart count
   - Container status

2. Application Logs:
   - Application errors
   - Stack traces
   - Connection failures

3. Resource Usage:
   - CPU consumption
   - Memory usage
   - OOMKilled events

4. Recent Changes:
   - Latest deployments
   - Configuration changes
   - Environment variables

Possible actions depend on the root cause and include rollback deployment, increasing resources, fixing configuration, or restarting unhealthy components. All production changes must be documented. 

(Reference: kubernetes_operations_runbook_chunk_001)

**Sources:**

- `data/raw/kubernetes_operations_runbook.md`
- `data/raw/incident_response_policy.md`
- `data/raw/incident_response_policy.md`

**Comment:** Direct question. Expected answer exists in the Kubernetes runbook.

---

## Example 2

**Question:** What are the requirements for Tier 1 services?

**Retrieved chunks:**

- `service_tiers_and_sla_policy_chunk_001` (score: 0.6790)
- `service_tiers_and_sla_policy_chunk_002` (score: 0.5520)
- `sre_operations_policy_chunk_002` (score: 0.3640)

**Answer:**

The requirements for Tier 1 services are:
- 24/7 monitoring
- Defined on-call ownership
- High availability architecture
- Documented disaster recovery procedure

These requirements ensure high reliability for critical services such as payment systems, authentication services, and core customer-facing APIs, with a target SLA of 99.9% availability and incident response within 15 minutes (service_tiers_and_sla_policy_chunk_001).

**Sources:**

- `data/raw/service_tiers_and_sla_policy.md`
- `data/raw/service_tiers_and_sla_policy.md`
- `data/raw/sre_operations_policy.md`

**Comment:** Direct policy question.

---

## Example 3

**Question:** What steps should an engineer take during a serious production incident?

**Retrieved chunks:**

- `sre_operations_policy_chunk_003` (score: 0.5248)
- `incident_response_policy_chunk_001` (score: 0.4863)
- `kubernetes_operations_runbook_chunk_002` (score: 0.4485)

**Answer:**

During a serious production incident, an engineer should:

1. Confirm the incident.
2. Identify affected services.
3. Check recent changes.
4. Review monitoring dashboards.
5. Escalate if required.
6. Analyze application logs, infrastructure metrics, Kubernetes events, database performance, and recent deployments to identify the root cause.
7. Conduct a root cause analysis, create a timeline, determine corrective actions, and define prevention tasks after the incident.

These steps align with first response and investigation processes and the post-incident requirements for major incidents (SEV2 or higher) [incident_response_policy_chunk_001, sre_operations_policy_chunk_003].

**Sources:**

- `data/raw/sre_operations_policy.md`
- `data/raw/incident_response_policy.md`
- `data/raw/kubernetes_operations_runbook.md`

**Comment:** Paraphrased incident-response question.

---

## Example 4

**Question:** What should the SRE team improve to make systems more reliable?

**Retrieved chunks:**

- `sre_improvement_strategy_chunk_001` (score: 0.7189)
- `sre_operations_policy_chunk_001` (score: 0.5956)
- `sre_operations_policy_chunk_003` (score: 0.4898)

**Answer:**

The SRE team should improve metrics coverage, logging quality, distributed tracing, alert quality, reduce manual operations, improve availability, increase deployment safety, and reduce recovery time. They should also focus on infrastructure as code, automated deployments, self-service operations, and automated incident diagnostics to enhance system reliability. (Source: sre_improvement_strategy_chunk_001)

**Sources:**

- `data/raw/sre_improvement_strategy.md`
- `data/raw/sre_operations_policy.md`
- `data/raw/sre_operations_policy.md`

**Comment:** Paraphrased reliability-improvement question.

---

## Example 5

**Question:** Who approves production changes?

**Retrieved chunks:**

- `kubernetes_operations_runbook_chunk_002` (score: 0.4292)
- `sre_operations_policy_chunk_003` (score: 0.3625)
- `service_tiers_and_sla_policy_chunk_002` (score: 0.3104)

**Answer:**

The context does not explicitly state who approves production changes. Therefore:

I do not have enough information in the available SRE documents to answer this question.

**Sources:**

- `data/raw/kubernetes_operations_runbook.md`
- `data/raw/sre_operations_policy.md`
- `data/raw/service_tiers_and_sla_policy.md`

**Comment:** Known weak retrieval case.

---

## Example 6

**Question:** What is our AWS disaster recovery policy?

**Retrieved chunks:**

- `incident_response_policy_chunk_001` (score: 0.4838)
- `incident_response_policy_chunk_002` (score: 0.4523)
- `sre_improvement_strategy_chunk_002` (score: 0.4478)

**Answer:**

I do not have enough information in the available SRE documents to answer this question.

**Sources:**

- `data/raw/incident_response_policy.md`
- `data/raw/incident_response_policy.md`
- `data/raw/sre_improvement_strategy.md`

**Comment:** Fallback test. Knowledge base does not contain this information.

---

## Example 7

**Question:** How many vacation days do SRE engineers receive?

**Retrieved chunks:**

- `sre_improvement_strategy_chunk_001` (score: 0.4126)
- `sre_operations_policy_chunk_003` (score: 0.3887)
- `sre_operations_policy_chunk_001` (score: 0.3736)

**Answer:**

I do not have enough information in the available SRE documents to answer this question.

**Sources:**

- `data/raw/sre_improvement_strategy.md`
- `data/raw/sre_operations_policy.md`
- `data/raw/sre_operations_policy.md`

**Comment:** Fallback test. Question is outside the SRE knowledge base.

---

