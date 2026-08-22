# Engineering Decisions

- Each numbered clause (e.g. §4.3.2) is treated as one retrieval unit. This makes citations simple and precise.

- We use semantic search with `all-MiniLM-L6-v2` instead of only keyword search, so similar questions can find relevant clauses even when the wording is different.

- The LLM answers only using the retrieved policy clauses. It should not use outside knowledge or guess missing information.

- Citations are checked to make sure the cited clause exists and was included in the retrieved evidence.

- Retrieval, generation, and citation checking are separate modules. This keeps the code simple and makes future changes easier.

- We do not hard-code the known trap questions. The system should handle them using general grounding and refusal logic.