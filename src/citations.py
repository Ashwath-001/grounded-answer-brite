import re


def extract_citations(answer_text):
    # Find every §X.X.X-style citation the model claims in its answer
    pattern = r"§(\d+(?:\.\d+)+)"
    return list(dict.fromkeys(re.findall(pattern, answer_text)))  # dedup, keep order


def validate_citations(cited_clauses, retrieved_clauses, all_clauses):
    """ check each cited clause against:
      - all_clauses: does this clause number exist in the manual at all?
      - retrieved_clauses: was this clause actually shown to the model as evidence?
    Returns a report dict per citation."""
    
    all_clause_ids = {c["clause"] for c in all_clauses}
    retrieved_ids = {c["clause"] for c in retrieved_clauses}

    report = []
    for clause_id in cited_clauses:
        report.append({
            "clause": clause_id,
            "exists_in_manual": clause_id in all_clause_ids,
            "was_retrieved": clause_id in retrieved_ids
        })
    return report