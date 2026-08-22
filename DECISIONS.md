# Engineering Decisions

## 1. Grounded Retrieval

Treating each numbered policy clause as a retrieval unit so that answers can be traced to exact source.

## 2. Semantic Search

I use semantic retrieval to identify clauses relevant to the user's question. Retrieval will be treated as evidence gathering, not as a proof as the answer exists.

## 3. Answer vs. Refusal

The system answers only when the retrieved evidence sufficiently supports the question. If the policy does not cover the question or is ambiguous, the system refuses instead of guessing.

## 4. Contradictions

When relevant clauses conflict, the system should surface the conflict and cite both clauses rather than silently selecting one interpretation.

## 5. Citations

Every substantive answer includes the specific policy clause used as evidence. Citations are derived from stored clause metadata to keep them verifiable.

## 6. Modularity

Document ingestion, retrieval, answer generation, grounding, and evaluation are kept separate. I think this will be more helpful for managing and also we can easily change the system requiurements if it is more modular.