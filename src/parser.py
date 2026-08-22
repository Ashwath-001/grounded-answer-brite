import re
from pathlib import Path


def parse_policy(file_path: str):
    text = Path(file_path).read_text(encoding="utf-8")

    pattern = r"(?m)^\*\*(\d+(?:\.\d+)+)\*\*\s*(.*?)(?=^\*\*\d+(?:\.\d+)+\*\*|\Z)"

    matches = re.findall(pattern, text, re.DOTALL)

    clauses = []

    for clause_id, content in matches:
        clauses.append({
            "clause": clause_id,
            "text": content.strip()
        })

    return clauses


if __name__ == "__main__":
    clauses = parse_policy("data/policy-manual.md")

    print(f"Total clauses: {len(clauses)}")

    for clause in clauses[:5]: #just for printing first 5 clauses for verification
        print(f"\n§{clause['clause']}")
        print(clause["text"][:200])