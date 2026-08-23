import re
from pathlib import Path
from datetime import datetime, date

DATE_BASIS_PATTERNS = [
    (r"paragraphs?\s+([\d,\s]*\d)(?:\s*(?:and|&)\s*(\d+))?\s+apply to any determination", "determination"),
    (r"paragraphs?\s+(\d+)\s+apply\s+\**\s*only in respect of a change of circumstances", "change_of_circumstance"),
]

AMENDMENT_PATH = "data/Amendment No. 2026-01.md"


def _extract_paragraph_numbers(fragment):
    return [int(n) for n in re.findall(r"\d+", fragment)]


def _table_to_text(table_md):
    rows = [r.strip() for r in table_md.strip().splitlines() if r.strip()]
    data_rows = [r for r in rows if not re.match(r"^\|\s*:?-+:?\s*\|", r) and "Household size" not in r]
    parts = []
    for row in data_rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) == 2:
            parts.append(f"{cells[0]}: {cells[1]}")
    return "Monthly income thresholds — " + "; ".join(parts) + "."


def _parse_written_date(fragment):
    m = re.search(r"(\d+)\s+(\w+)\s+(\d{4})", fragment)
    if not m:
        return None
    return datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %B %Y").date()


def parse_amendment(file_path=AMENDMENT_PATH):
    text = Path(file_path).read_text(encoding="utf-8")

    section_pattern = r"(?m)^##\s+(\d+)\.\s+.*$"
    section_matches = list(re.finditer(section_pattern, text))

    sections = {}
    for i, m in enumerate(section_matches):
        section_num = int(m.group(1))
        start = m.end()
        end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(text)
        sections[section_num] = text[start:end]

    effective_match = re.search(r"\*\*Effective:\*\*\s*(\d+)\s+(\w+)\s+(\d{4})", text)
    cutover_date = _parse_written_date(effective_match.group(0)) if effective_match else None

    basis_by_section = {}
    transitional_text = sections.get(max(sections.keys())) if sections else ""
    for pattern, basis in DATE_BASIS_PATTERNS:
        for m in re.finditer(pattern, transitional_text):
            for num in _extract_paragraph_numbers(m.group(0)):
                basis_by_section[num] = basis

    substitutions = []
    insertions = []

    sub_pattern = re.compile(
        r'In\s+§(\d+(?:\.\d+)+)(?:\([a-z]\))?,\s*for\s+"([^"]+)"[^"]*?substitute\s+"\*\*([^*]+)\*\*"'
    )
    table_pattern = re.compile(
        r'In the table at\s+§(\d+(?:\.\d+)+),\s*substitute the following\s*—\s*\n\n(.*?)(?=\n##|\n---|\Z)',
        re.DOTALL
    )
    insert_pattern = re.compile(
        r'After\s+§(\d+(?:\.\d+)+),\s*insert\s*—\s*\n\n>\s*\*\*(\d+(?:\.\d+)+[A-Z]?)\*\*\s*(.+?)(?=\n\n|\Z)',
        re.DOTALL
    )

    for section_num, body in sections.items():
        basis = basis_by_section.get(section_num)

        for m in sub_pattern.finditer(body):
            substitutions.append({
                "clause": m.group(1), "old_fragment": m.group(2).strip(),
                "new_fragment": m.group(3).strip(), "date_basis": basis,
            })

        for m in table_pattern.finditer(body):
            substitutions.append({
                "clause": m.group(1), "full_replace": True,
                "new_fragment": _table_to_text(m.group(2)), "date_basis": basis,
            })

        for m in insert_pattern.finditer(body):
            insertions.append({
                "clause": m.group(2), "text": m.group(3).strip(), "date_basis": basis,
            })

    return {"cutover_date": cutover_date, "substitutions": substitutions, "insertions": insertions}


_PARSED = parse_amendment()
CUTOVER_DATE = _PARSED["cutover_date"]
CLAUSE_AMENDMENTS = _PARSED["substitutions"]
CLAUSE_INSERTIONS = _PARSED["insertions"]

def _relevant_date(date_basis, dates):
    """dates = {'change_of_circumstance': date, 'determination': date}"""
    if date_basis == "change_of_circumstance":
        return dates["change_of_circumstance"]
    if date_basis == "determination":
        return dates["determination"]
    # date_basis unspecified in the amendment text - fall back to
    # determination date, but this is a genuine ambiguity, not a solved case.
    return dates["determination"]


def apply_amendments(clause, dates):
    for amendment in CLAUSE_AMENDMENTS:
        if amendment["clause"] != clause["clause"]:
            continue

        relevant_date = _relevant_date(amendment["date_basis"], dates)
        if relevant_date is None or relevant_date < CUTOVER_DATE:
            return {**clause, "amended": False}

        if amendment.get("full_replace"):
            new_text = amendment["new_fragment"]
        else:
            new_text = clause["text"].replace(amendment["old_fragment"], amendment["new_fragment"])

        basis_label = (amendment["date_basis"] or "unspecified - defaulted to determination date").replace("_", " ")
        note = (f"[Amended by Amendment No. 2026-01, effective {CUTOVER_DATE.isoformat()} "
                f"({basis_label} basis; relevant date used: {relevant_date.isoformat()})]")
        return {**clause, "text": f"{new_text}\n{note}", "amended": True}

    return {**clause, "amended": False}


def get_applicable_insertions(dates):
    active = []
    for ins in CLAUSE_INSERTIONS:
        relevant_date = _relevant_date(ins["date_basis"], dates)
        if relevant_date and relevant_date >= CUTOVER_DATE:
            active.append({"clause": ins["clause"], "text": ins["text"], "score": None, "amended": True})
    return active


def all_known_clause_ids(dates):
    ids = set()
    for ins in CLAUSE_INSERTIONS:
        relevant_date = _relevant_date(ins["date_basis"], dates)
        if relevant_date and relevant_date >= CUTOVER_DATE:
            ids.add(ins["clause"])
    return ids