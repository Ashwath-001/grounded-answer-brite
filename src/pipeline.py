from retriever import PolicyRetriever
from parser import parse_policy
from citations import extract_citations, validate_citations
from grounding import is_answerable, REFUSAL_MESSAGE
from amendments import apply_amendments, get_applicable_insertions, all_known_clause_ids
from contradictions import find_contradiction_group, resolve_contradiction_group
from generation import generate_answer, generate_contradiction_answer


def answer_question(question, dates, all_clauses, retriever):
    top_clauses = retriever.search(question, top_k=3)
    result = {"question": question, "dates": dates, "top_score": top_clauses[0]["score"]}

    if not is_answerable(top_clauses):
        result["mode"] = "refusal"
        result["answer"] = REFUSAL_MESSAGE
        return result

    retrieved_ids = [c["clause"] for c in top_clauses]
    group = find_contradiction_group(retrieved_ids)
    is_live, resolved_group_clauses = (False, None)
    if group:
        is_live, resolved_group_clauses = resolve_contradiction_group(group, all_clauses, dates)

    if group and is_live:
        answer = generate_contradiction_answer(question, dates, group, resolved_group_clauses)
        result["mode"] = "contradiction"
        result["answer"] = answer
        result["clauses"] = [c["clause"] for c in resolved_group_clauses]
        return result

    resolved_clauses = [apply_amendments(c, dates) for c in top_clauses]
    resolved_clauses += get_applicable_insertions(dates)

    answer = generate_answer(question, dates, resolved_clauses)
    cited = extract_citations(answer)
    if not cited:
        answer = generate_answer(question, dates, resolved_clauses, force_citation_retry=True)
        cited = extract_citations(answer)

    known_ids = {c["clause"] for c in all_clauses} | all_known_clause_ids(dates)
    report = validate_citations(cited, resolved_clauses, [{"clause": cid} for cid in known_ids])

    result["mode"] = "answer"
    result["answer"] = answer
    result["clauses"] = [c["clause"] for c in resolved_clauses]
    result["cited"] = cited
    result["citation_report"] = report
    return result