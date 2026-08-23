REFUSAL_THRESHOLD = 0.65

REFUSAL_MESSAGE = (
    "I don't have a clear answer to this in the policy manual. The retrieved "
    "clauses don't directly establish a rule for this situation, and I'm not "
    "going to guess based on related-sounding clauses.\n\n"
    "Please contact your district office (Calder Central, Northgate, "
    "Weybridge, or Ash Hill) or your caseworker for a determination on this."
)


def is_answerable(retrieved_clauses, threshold=REFUSAL_THRESHOLD):
    """
    Decide whether the retrieved evidence is strong enough to answer from.
    Uses the top retrieval score as a proxy for 'does this evidence actually
    address the question' - not perfect, but a first pass.
    """
    if not retrieved_clauses:
        return False

    top_score = retrieved_clauses[0]["score"]
    return top_score >= threshold