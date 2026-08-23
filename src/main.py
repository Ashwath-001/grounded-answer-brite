import os
from dotenv import load_dotenv
from groq import Groq

from retriever import PolicyRetriever
from parser import parse_policy
from citations import extract_citations, validate_citations
from grounding import is_answerable, REFUSAL_MESSAGE

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def build_context(clauses):
    parts = []
    for c in clauses:
        parts.append(f"§{c['clause']}\n{c['text']}")
    return "\n\n---\n\n".join(parts)


def generate_answer(question, clauses):
    context = build_context(clauses)

    system_prompt = (
        "You are a policy assistant. Answer the user's question using ONLY "
        "the policy clauses provided below as evidence. Do not use any "
        "outside knowledge. Cite the clause number(s) you used at the end "
        "of your answer, in the form '§X.X.X'.\n\n"
        f"POLICY EVIDENCE:\n\n{context}"
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=600,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    all_clauses = parse_policy("data/policy-manual.md")
    retriever = PolicyRetriever("data/policy-manual.md")

    question = input("Question: ")

    top_clauses = retriever.search(question, top_k=3)

    print(f"\nTop retrieval score: {top_clauses[0]['score']:.3f}")

    if not is_answerable(top_clauses):
        print("\nAnswer:\n")
        print(REFUSAL_MESSAGE)
        print("\nRetrieved clauses (insufficient to answer):")
        for c in top_clauses:
            print(f"  §{c['clause']} (score: {c['score']:.3f})")
    else:
        answer = generate_answer(question, top_clauses)

        print("\nAnswer:\n")
        print(answer)

        print("\nRetrieved clauses used as evidence:")
        for c in top_clauses:
            print(f"  §{c['clause']} (score: {c['score']:.3f})")

        cited = extract_citations(answer)
        report = validate_citations(cited, top_clauses, all_clauses)

        print("\nCitation validation:")
        if not report:
            print("  No citations found in the answer.")
        for r in report:
            if r["was_retrieved"]:
                status = "OK - matches retrieved evidence"
            elif r["exists_in_manual"]:
                status = "WARNING - real clause, but was NOT part of retrieved evidence"
            else:
                status = "ERROR - this clause does not exist in the manual (hallucinated)"
            print(f"  §{r['clause']}: {status}")