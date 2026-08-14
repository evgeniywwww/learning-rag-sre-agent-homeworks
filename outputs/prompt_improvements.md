# Prompt Improvements

## Improvement 1 — Grounded answers

### Problem

The initial prompt allowed the model to use retrieved context too broadly and sometimes include additional information that was not necessary for the answer.

### Change

Added explicit rules to answer only using information supported by the provided context and not make unsupported assumptions.

### Result

Answers became more focused on information available in the knowledge base.


## Improvement 2 — Source citations

### Problem

The initial prompt required source references but did not clearly specify that only sources actually supporting the answer should be cited.

### Change

Added a rule to cite only chunk IDs or source files that directly support the generated answer.

### Result

The model now references the chunks used to support the answer more precisely.


## Improvement 3 — Fallback behavior

### Problem

For questions where retrieval returned related chunks but the actual answer was not present, the model could still discuss retrieved information before returning a fallback.

### Change

Added a strict fallback rule: if the retrieved context does not contain enough information, the model must explicitly report insufficient information and avoid using unrelated context as evidence.

### Result

For questions about AWS disaster recovery, vacation days and production change approval, the model correctly returned the fallback instead of generating an answer from general knowledge.