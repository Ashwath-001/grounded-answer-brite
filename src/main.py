import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

from retriever import PolicyRetriever
from parser import parse_policy
from citations import extract_citations, validate_citations
from grounding import is_answerable, REFUSAL_MESSAGE
from amendments import apply_amendments, get_applicable_insertions, all_known_clause_ids

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def build_context(clauses):
    return "\n\n---\n\n".join(f"§{c['clause']}\n{c['text']}" for c in clauses)


def generate_answer(question, dates, clauses, force_citation_retry=False):
    context = build_context(clauses)
    citation_rule = (
        "You MUST end your answer with one line, exactly in this format, "
        "listing every clause you relied on:\nCitation: §X.X.X, §Y.Y.Y"
    )
    if force_citation_retry:
        citation_rule = "IMPORTANT - YOU FORGOT LAST TIME: " + citation_rule

    system_prompt = (
        "You are a policy assistant. Answer using ONLY the policy clauses "
        "below. Some are marked amended - if amended, use the amended "
        "figure. Do not use outside knowledge.\n\n"
        f"{citation_rule}\n\n"
        f"Change of circumstance date: {dates['change_of_circumstance']}\n"
        f"Determination date: {dates['determination']}\n\n"
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


def parse_date_input(raw):
    return datetime.strptime(raw.strip(), "%Y-%m-%d").date()


if __name__ == "__main__":
    all_clauses = parse_policy("data/policy-manual.md")
    retriever = PolicyRetriever("data/policy-manual.md")

    question = input("Question: ")
    dates = {
        "change_of_circumstance": parse_date_input(input("Date the change of circumstances occurred (YYYY-MM-DD): ")),
        "determination": parse_date_input(input("Date the determination is being made (YYYY-MM-DD): ")),
    }

    top_clauses = retriever.search(question, top_k=3)
    print(f"\nTop retrieval score: {top_clauses[0]['score']:.3f}")

    if not is_answerable(top_clauses):
        print("\nAnswer:\n")
        print(REFUSAL_MESSAGE)
    else:
        resolved_clauses = [apply_amendments(c, dates) for c in top_clauses]
        resolved_clauses += get_applicable_insertions(dates)

        answer = generate_answer(question, dates, resolved_clauses)
        cited = extract_citations(answer)

        if not cited:
            answer = generate_answer(question, dates, resolved_clauses, force_citation_retry=True)
            cited = extract_citations(answer)

        print("\nAnswer:\n")
        print(answer)

        print("\nRetrieved clauses used as evidence:")
        for c in resolved_clauses:
            tag = " (AMENDED)" if c.get("amended") else ""
            score_str = f"score: {c['score']:.3f}" if c.get("score") is not None else "inserted by amendment"
            print(f"  §{c['clause']}{tag} ({score_str})")

        known_ids = {c["clause"] for c in all_clauses} | all_known_clause_ids(dates)
        report = validate_citations(cited, resolved_clauses, [{"clause": cid} for cid in known_ids])

        print("\nCitation validation:")
        if not report:
            print("  WARNING - model did not produce a machine-readable citation after retry. Verify manually.")
        for r in report:
            if r["was_retrieved"]:
                status = "OK - matches retrieved evidence"
            elif r["exists_in_manual"]:
                status = "WARNING - real clause, not part of retrieved evidence"
            else:
                status = "ERROR - clause does not exist / not in force for this date"
            print(f"  §{r['clause']}: {status}")