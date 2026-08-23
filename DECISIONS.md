# Engineering Decisions

- Each numbered clause (e.g. §4.3.2) is treated as one retrieval unit. This makes citations simple and precise.

- We use semantic search with `all-MiniLM-L6-v2` instead of only keyword search, so similar questions can find relevant clauses even when the wording is different.

- The LLM answers only using the retrieved policy clauses. It should not use outside knowledge or guess missing information.

- Citations are checked to make sure the cited clause exists and was included in the retrieved evidence.

- Retrieval, generation, and citation checking are separate modules. This keeps the code simple and makes future changes easier.

- We do not hard-code the known trap questions. The system should handle them using general grounding and refusal logic.

# Day 2 Requirement changes

- Amendment values are parsed from the given amendments file itself during runtime rather than hardcoding it.

- I chose this approach because in real world scenarios, the requirement might change many times not just this one time. So I thought this will be a better approach.

# Evaluation results (10 questions)

- Ran a 10-question evaluation set covering a normal answer, the live contradiction, the same question after the contradiction is resolved, a known refusal case, an out-of-scope refusal, and both amended and pre-amendment figures. 8/10 passed on the first run.

- The 2 failures were both about the earnings disregard amount. Retrieval kept pulling §6.1.1 and §6.4 (which just describe that a disregard exists) instead of §6.4.1 (which has the actual dollar amount). Because of this, the LLM correctly said it did not have the exact figure, instead of making one up. This is a real retrieval limitation, not a prompt or logic bug, and we are noting it honestly instead of hiding it.

- We see this as a good sign in one way: when the right clause is missing, the system says so instead of guessing a number. That is the grounding behavior we wanted, just triggered by a retrieval gap instead of the refusal check.

- Known limitation: retrieval sometimes picks general/definition clauses over the specific clause with the actual number, especially when the question is short. A future improvement would be increasing top_k or improving how clauses are chunked.