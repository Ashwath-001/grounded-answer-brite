import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from retriever import PolicyRetriever
from parser import parse_policy
from pipeline import answer_question

TEST_CASES = [
    {
        "name": "Reporting deadline - contradiction still live (pre-cutover)",
        "question": "How long does a recipient have to report a change of circumstances?",
        "dates": {"change_of_circumstance": date(2026, 2, 15), "determination": date(2026, 3, 1)},
        "expected_mode": "contradiction",
        "expected_substrings": ["10", "30"],
    },
    {
        "name": "Reporting deadline - resolved (post-cutover)",
        "question": "How long does a recipient have to report a change of circumstances?",
        "dates": {"change_of_circumstance": date(2026, 4, 1), "determination": date(2026, 4, 1)},
        "expected_mode": "answer",
        "expected_substrings": ["14"],
    },
    {
        "name": "Full-time education absence - known gap, must refuse",
        "question": "If a recipient leaves Calder County to attend university full-time, how long can they remain eligible?",
        "dates": {"change_of_circumstance": date(2026, 4, 1), "determination": date(2026, 4, 1)},
        "expected_mode": "refusal",
        "expected_substrings": [],
    },
    {
        "name": "Earnings disregard - pre-amendment figure",
        "question": "What is the monthly earnings disregard amount used when calculating a household's countable income?",
        "dates": {"change_of_circumstance": date(2026, 2, 1), "determination": date(2026, 2, 1)},
        "expected_mode": "answer",
        "expected_substrings": ["120"],
    },
    {
        "name": "Earnings disregard - post-amendment figure",
        "question": "What is the monthly earnings disregard amount used when calculating a household's countable income?",
        "dates": {"change_of_circumstance": date(2026, 4, 1), "determination": date(2026, 4, 1)},
        "expected_mode": "answer",
        "expected_substrings": ["175"],
    },
    {
        "name": "First sanction rate - pre-amendment",
        "question": "By what percentage is a recipient's monthly award reduced for a first sanction?",
        "dates": {"change_of_circumstance": date(2026, 2, 1), "determination": date(2026, 2, 1)},
        "expected_mode": "answer",
        "expected_substrings": ["20"],
    },
    {
        "name": "First sanction rate - post-amendment",
        "question": "By what percentage is a recipient's monthly award reduced for a first sanction?",
        "dates": {"change_of_circumstance": date(2026, 4, 1), "determination": date(2026, 4, 1)},
        "expected_mode": "answer",
        "expected_substrings": ["15"],
    },
    {
        "name": "New post-amendment protection (§10.5.3A)",
        "question": "Can a sanction be imposed on a recipient who failed to report a change that would have increased their award?",
        "dates": {"change_of_circumstance": date(2026, 4, 1), "determination": date(2026, 4, 1)},
        "expected_mode": "answer",
        "expected_substrings": ["increased"],
    },
    {
        "name": "Unrelated, clean, answerable clause (appeal deadline)",
        "question": "How many days does a person have to lodge an appeal after a review outcome?",
        "dates": {"change_of_circumstance": date(2026, 4, 1), "determination": date(2026, 4, 1)},
        "expected_mode": "answer",
        "expected_substrings": ["30"],
    },
    {
        "name": "Fully out-of-scope question - must refuse",
        "question": "What is the capital of France?",
        "dates": {"change_of_circumstance": date(2026, 4, 1), "determination": date(2026, 4, 1)},
        "expected_mode": "refusal",
        "expected_substrings": [],
    },
]


def run():
    all_clauses = parse_policy("data/policy-manual.md")
    retriever = PolicyRetriever("data/policy-manual.md")

    results = []
    for case in TEST_CASES:
        result = answer_question(case["question"], case["dates"], all_clauses, retriever)
        answer_lower = result["answer"].lower()

        mode_ok = result["mode"] == case["expected_mode"]
        substrings_ok = all(s.lower() in answer_lower for s in case["expected_substrings"])
        passed = mode_ok and substrings_ok

        results.append({
            "name": case["name"], "passed": passed, "mode_ok": mode_ok,
            "substrings_ok": substrings_ok, "actual_mode": result["mode"],
            "expected_mode": case["expected_mode"], "answer": result["answer"],
        })

    return results


def write_report(results, path="tests/evaluation_results.md"):
    lines = ["# Evaluation Results\n"]
    passed_count = sum(1 for r in results if r["passed"])
    lines.append(f"**{passed_count}/{len(results)} passed**\n")

    for i, r in enumerate(results, 1):
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(f"## {i}. {r['name']} — {status}")
        lines.append(f"- Expected mode: `{r['expected_mode']}`, got: `{r['actual_mode']}`")
        lines.append(f"- Answer:\n  > {r['answer'][:400].replace(chr(10), ' ')}")
        lines.append("")

    Path(path).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    results = run()
    for i, r in enumerate(results, 1):
        status = "PASS" if r["passed"] else "FAIL"
        print(f"{i}. [{status}] {r['name']}")
    passed_count = sum(1 for r in results if r["passed"])
    print(f"\n{passed_count}/{len(results)} passed")
    write_report(results)
    print("Full report written to tests/evaluation_results.md")