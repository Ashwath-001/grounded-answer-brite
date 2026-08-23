from datetime import datetime

from retriever import PolicyRetriever
from parser import parse_policy
from pipeline import answer_question


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

    result = answer_question(question, dates, all_clauses, retriever)

    print(f"\nTop retrieval score: {result['top_score']:.3f}")

    if result["mode"] == "refusal":
        print("\nAnswer:\n")
        print(result["answer"])

    elif result["mode"] == "contradiction":
        print("\n[Contradiction detected for this date - surfacing both clauses instead of picking one]")
        print("\nAnswer:\n")
        print(result["answer"])
        print("\nClauses in conflict:")
        for c in result["clauses"]:
            print(f"  §{c}")

    else:
        print("\nAnswer:\n")
        print(result["answer"])
        print("\nRetrieved/used clauses:", ", ".join(f"§{c}" for c in result["clauses"]))
        print("\nCitation validation:")
        if not result["citation_report"]:
            print("  WARNING - model did not produce a machine-readable citation after retry.")
        for r in result["citation_report"]:
            if r["was_retrieved"]:
                status = "OK - matches retrieved evidence"
            elif r["exists_in_manual"]:
                status = "WARNING - real clause, not part of retrieved evidence"
            else:
                status = "ERROR - clause does not exist / not in force for this date"
            print(f"  §{r['clause']}: {status}")