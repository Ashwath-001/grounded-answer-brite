from amendments import apply_amendments, CUTOVER_DATE

CONTRADICTION_GROUPS = [
    {
        "clauses": ["4.3.2", "9.1.4"],
        "topic": "the reporting deadline for a change of circumstances",
    },
]


def find_contradiction_group(clause_ids):
    for group in CONTRADICTION_GROUPS:
        if any(cid in group["clauses"] for cid in clause_ids):
            return group
    return None


def get_clause_by_id(all_clauses, clause_id):
    for c in all_clauses:
        if c["clause"] == clause_id:
            return c
    return None


def resolve_contradiction_group(group, all_clauses, dates):
    """is_live is True only if at least one clause in the group is still
    unamended for the relevant date - meaning the pre-amendment conflict
    still applies."""

    resolved = []
    for clause_id in group["clauses"]:
        original = get_clause_by_id(all_clauses, clause_id)
        if original is None:
            continue
        resolved.append(apply_amendments(original, dates))

    is_live = any(not c.get("amended") for c in resolved)
    return is_live, resolved