# Retrieval Improvement: Metadata Filtering

Baseline semantic retrieval compared with retrieval using metadata filtering.

Metadata filter used: `{'document_type': 'policy'}`

| Query | Expected | Baseline top-1 | Filter top-1 | Baseline score | Filter score | Result |
|---|---|---|---|---|---|---|
| How should I handle a production incident? | incident_response_policy | incident_response_policy | incident_response_policy | 0.4295 | 0.4295 | No change |
| What are Tier 1 service requirements? | service_tiers_and_sla_policy | service_tiers_and_sla_policy | service_tiers_and_sla_policy | 0.7160 | 0.7160 | No change |
| How can SRE improve reliability? | sre_improvement_strategy | sre_improvement_strategy | sre_improvement_strategy | 0.7249 | 0.7249 | No change |
| Who approves production changes? | sre_operations_policy | kubernetes_operations_runbook | kubernetes_operations_runbook | 0.4292 | 0.4292 | No improvement |
| How to troubleshoot Kubernetes pod restart? | kubernetes_operations_runbook | kubernetes_operations_runbook | kubernetes_operations_runbook | 0.8379 | 0.8379 | No change |


## Conclusion

Metadata filtering was evaluated against the same test queries. The goal was to check whether limiting the search space improves retrieval precision.
