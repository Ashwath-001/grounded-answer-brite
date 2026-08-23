import os
from dotenv import load_dotenv
from groq import Groq

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


def generate_contradiction_answer(question, dates, group, resolved_group_clauses):
    context = build_context(resolved_group_clauses)
    system_prompt = (
        "You are a policy assistant. The policy manual contains a genuine, "
        "unresolved internal contradiction between the clauses below "
        f"regarding {group['topic']}, for the dates given. Do NOT silently "
        "pick one clause as correct. Explicitly state that the manual gives "
        "two different answers, quote both figures, cite both clause "
        "numbers, and advise the user to contact a district office for a "
        "determination.\n\n"
        f"Change of circumstance date: {dates['change_of_circumstance']}\n"
        f"Determination date: {dates['determination']}\n\n"
        f"POLICY EVIDENCE:\n\n{context}"
    )
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=700,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content