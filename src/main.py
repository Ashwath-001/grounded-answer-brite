import os
from dotenv import load_dotenv
from groq import Groq

from retriever import PolicyRetriever

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
        max_tokens=2048,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    retriever = PolicyRetriever("data/policy-manual.md")

    question = input("Question: ")

    top_clauses = retriever.search(question, top_k=3)

    answer = generate_answer(question, top_clauses)

    print("\nAnswer:\n")
    print(answer)

    print("\nRetrieved clauses used as evidence:")
    for c in top_clauses:
        print(f"  §{c['clause']} (score: {c['score']:.3f})")