# Evaluation

This directory will contain the reproducible evaluation harness for the Hiver submission.

## Planned artifacts

- `golden_set.json` — curated support questions with expected answer properties and metadata.
- `baseline.py` — baseline system runner.
- `evaluate_agent.py` — batch runner for the agent.
- `metrics.py` — deterministic scoring and aggregation.
- `llm_judge.py` — structured judge for semantic criteria.
- `failure_analysis.py` — categorisation and failure report generation.
- `reports/` — committed experiment summaries and score tables.

## Principle

A single aggregate score is not enough. Reports should show what changed, where the system fails, and whether improvements generalize across hard-case buckets.
