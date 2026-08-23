# Engineering Decisions

- Each numbered clause (e.g. §4.3.2) is treated as one retrieval unit. This makes citations simple and precise.

- We use semantic search with `all-MiniLM-L6-v2` instead of only keyword search, so similar questions can find relevant clauses even when the wording is different.

- The LLM answers only using the retrieved policy clauses. It should not use outside knowledge or guess missing information.

- Citations are checked to make sure the cited clause exists and was included in the retrieved evidence.

- Retrieval, generation, and citation checking are each a seperated modules. This keeps the code simple and makes future changes easier.

- We do not hard-code the known trap questions. The system should handle them using general grounding and refusal logic.

# Day 2 Requirement changes

- Amendment values are parsed from the given amendments file itself during runtime rather than hardcoding it.

- I chose this approach because in real world scenarios, the requirement might change many times not just this one time. So I thought this will be a better approach.

# Evaluation results (10 questions)

- I made 10 test questions to check the system. They cover a normal answer, the contradiction that is still active, the same question after the contradiction is fixed by the amendment, a case that should be refused, a completely unrelated question that should be refused, and both the old and new amended numbers. **8 out of 10 passed the first time.**

- Both failures were the same question: (the earnings disregard amount). The model kept picking §6.1.1 & §6.4, which just say a disregard exists, instead of §6.4.1, which has the actual dollar number. So the LLM identified it didn't have the exact figure, instead of guessing one.

- Its still a good sign, because when the right clause was missing, the system said it didn't know instead of making up a number. This is exactly the safe behavior we wanted.

- Limitation: sometimes retrieval picks a general clause over the specific clause that actually has the number, especially for short questions. This can be improved by having more clauses per question or splitting the manual into smaller parts.