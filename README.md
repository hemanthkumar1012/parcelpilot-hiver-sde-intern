# ParcelPilot — Hiver SDE Intern

An evidence-first AI customer-support agent built from the ParcelPilot foundation, with reproducible evaluation as a first-class feature.

## What is implemented

- FastAPI `/chat` and `/health` service
- Workbook and PDF ingestion
- TF-IDF retrieval with explicit source-authority precedence
- Safe operational table lookup
- Evidence passed to the LLM rather than free-form guessing
- Structured OpenAI Responses API generation
- Structured LLM-as-judge schema
- Golden-set evaluator and deterministic checks
- Failure taxonomy and failure-summary utilities
- Data-independent smoke tests
- GitHub Actions CI
- Explicit data boundary so missing assessment assets are never fabricated

The OpenAI implementation uses the Responses API pattern documented by OpenAI. citeturn0search0turn0search1

## Architecture

```text
                    +-------------------+
                    | Support question  |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | FastAPI /chat     |
                    +---------+---------+
                              |
                +-------------+-------------+
                |                           |
                v                           v
       +----------------+          +----------------+
       | Retrieval      |          | Table tools    |
       | TF-IDF         |          | account/order  |
       | authority      |          | ticket data   |
       +-------+--------+          +-------+--------+
               |                           |
               +-------------+-------------+
                             |
                             v
                    +-------------------+
                    | Evidence context  |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | LLM response      |
                    | grounded policy   |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Golden set        |
                    | deterministic     |
                    | LLM-as-judge      |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Failure analysis  |
                    +-------------------+
```

## Evaluation philosophy

A single aggregate score is not enough. The evaluation should expose correctness, groundedness, completeness, relevance, policy compliance, isolation, abstention, retrieval quality, and failure categories. Easy examples must not hide failures on ambiguous, adversarial, conflicting, or unsupported requests.

The golden set is intentionally empty until the actual assessment data and expected answers are available. Do not fabricate benchmark labels.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `/docs` and call `POST /chat`.

For evaluation:

```bash
python -m evaluation.evaluate_agent
```

For tests:

```bash
pytest -q
```

## Environment

Copy `.env.example` to `.env` and provide an API key when running the LLM-backed agent. Never commit `.env`.

## Data

Put authorized assessment assets under `data/` and `knowledge_base/`. The repository does not invent missing customer records or benchmark labels.

## Current limitation

The codebase is ready for the real assessment assets, but final data-dependent results cannot honestly be produced until the actual Hiver/ParcelPilot workbook, PDFs, and assignment-specific benchmark information are supplied. That is deliberate: evaluation numbers without the real dataset would be fabricated.
