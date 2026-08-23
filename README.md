# Grounded Answer - Policy Assistant

A CLI tool that answers plain-language questions about the Calder County Household Support Program policy manual. It answers only from the manual, cites the exact clauses and refuses when the manual doesn't clearly cover something. It also explicitly flags cases where the manual contradicts itself, instead of silently picking one side.

*Built for Brite Spark 2026, Problem 1 ("The Grounded Answer").*

## What it does

- Retrieves relevant policy clauses (source: policy-manual.md) for a question using semantic search.
- Generates an answer grounded only in those clauses.
- Applies **Amendment No. 2026-01** where relevant, resolving each amended clause against the correct date basis (date of the change of circumstances, or date of determination — the amendment specifies which applies per clause).
- Detects when a question hits a known contradiction in the manual (the §4.3.2 / §9.1.4 reporting-deadline conflict) and surfaces both sides instead of guessing
- Refuses to answer when retrieval confidence is too low to support a grounded answer (e.g. the manual's full-time-education gap), and points the user to a district office instead of inventing a rule.
- Validates every citation the model produces which doesnt exist in the actual manual, flagging hallucinated or unsupported clause references.

## Project structure
grounded-answer-brite/
│
├── data/
│   ├── policy-manual.md
│   └── Amendment No. 2026-01.md
│
├── src/
│   ├── parser.py
│   ├── retriever.py
│   ├── amendments.py
│   ├── contradictions.py
│   ├── citations.py
│   ├── grounding.py
│   ├── generation.py
│   ├── pipeline.py
│   └── main.py
│
├── tests/
│   └── evaluation.py
│
├── requirements.txt
├── DECISIONS.md
├── AI-USAGE.md
└── README.md

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/Ashwath-001/grounded-answer-brite.git
cd grounded-answer-brite
pip install -r requirements.txt
```

Create a `.env` file in the project root with a free [Groq](https://console.groq.com) API key:

GROQ_API_KEY=your-key-here


## Running it

From the project root:

```bash
python src/main.py
```

You'll be prompted for:
1. **Question** — a plain-language question about the policy.
2. **Date the change of circumstances occurred** (`YYYY-MM-DD`) — the date the underlying event happened.
3. **Date the determination is being made** (`YYYY-MM-DD`) — the date the case is being decided.

These two dates matter because Amendment No. 2026-01 ties different provisions to different dates — for example, the reporting deadline depends on when the change occurred, while the earnings-disregard figure depends on the determination date. If both dates are the same, just enter the same value for both.

### Example Input and Output

Question: How long does a recipient have to report a change of circumstances?
Date the change of circumstances occurred (YYYY-MM-DD): 2026-02-15
Date the determination is being made (YYYY-MM-DD): 2026-03-01

Top retrieval score: 0.831

[Contradiction detected for this date - surfacing both clauses instead of picking one]

Answer:

The policy manual contains two different rules for this situation...
§4.3.2 requires reporting within 10 calendar days...
§9.1.4 refers to a 30 calendar day period under §4.3...
This is an unresolved inconsistency. Please contact a district office
(Calder Central, Northgate, Weybridge, or Ash Hill) for a determination.

Clauses in conflict:
§4.3.2
§9.1.4


## Running the evaluation set

```bash
python tests/evaluation.py
```

This runs 10 self-created test questions (covering a normal answer, the live contradiction, the resolved-post-amendment case, the full-time-education refusal case, both amended and pre-amendment figures, and a fully out-of-scope refusal), prints pass/fail to the console, and writes a full report to `tests/evaluation_results.md`.

## Known Limitations

- Refusal currently uses a retrieval-score threshold tuned on a small evaluation set.
- Amendment clauses are added to the context when their date conditions are active.
- The current contradiction detection handles the known §4.3.2 / §9.1.4 conflict explicitly; it does not automatically discover new contradictions.
- The evaluation set is self-created and relatively small.