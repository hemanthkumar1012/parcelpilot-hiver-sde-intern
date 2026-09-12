# Hiver SDE Intern Implementation Plan

## 1. Objective

Transform the ParcelPilot support-agent foundation into a small, measurable customer-support agent submission centered on:

1. understanding the supplied support data;
2. establishing a reproducible baseline;
3. improving answer quality with grounded retrieval and tool use;
4. creating a representative golden set;
5. evaluating with deterministic checks and an LLM judge;
6. performing failure analysis;
7. re-running evaluation after each meaningful change.

## 2. Source projects reviewed

### parcelpilot-ai-agent

Reusable components:
- FastAPI support-agent service.
- Account/order/ticket lookup tools.
- Document retrieval over supplied PDFs.
- Source-authority handling.
- Account-scope enforcement.
- Confirmation-gated state-changing actions.
- Frontend chat UI.
- Assessment workbook and support-policy/operations PDFs.
- Existing regression tests.

Current weakness to address:
- The main `app/agent.py` is heavily deterministic/regex/rule-driven. It contains useful domain logic, but the project needs a clearer model-driven reasoning layer and a first-class evaluation harness rather than relying mainly on hand-authored decision paths.

### parcelpilot-platform

Reusable components:
- FastAPI application structure.
- SQLAlchemy/Alembic database foundation.
- Authentication and tenant isolation.
- Integrated authenticated chat endpoint.
- Operational shipment/support domain models.

The Hiver submission should not inherit unnecessary product surface area simply for completeness. Evaluation and correctness are higher priority.

## 3. Target architecture

```text
                 +----------------------+
                 |  Support data pack   |
                 | xlsx + PDFs + cases  |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Data preparation      |
                 | schema / provenance   |
                 +----------+-----------+
                            |
                +-----------+------------+
                |                        |
                v                        v
        +---------------+        +---------------+
        | Deterministic |        | Agent         |
        | baseline      |        | v1            |
        +-------+-------+        +-------+-------+
                |                        |
                +-----------+------------+
                            v
                 +----------------------+
                 | Golden-set evaluator  |
                 +----------+-----------+
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
       correctness     groundedness    completeness
             |              |              |
             +--------------+--------------+
                            v
                 +----------------------+
                 | Failure analysis      |
                 | category + examples   |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Agent v2 + re-run     |
                 +----------------------+
```

## 4. Evaluation dimensions

Minimum dimensions:
- answer correctness;
- groundedness / unsupported-claim rate;
- relevance;
- completeness against required answer points;
- instruction following;
- correct account/customer isolation;
- correct tool selection where tools are required;
- abstention/escalation when evidence is insufficient.

The report should include:
- overall score;
- per-category score;
- hard-case score;
- failure counts by category;
- representative failure examples;
- baseline versus improved-agent comparison.

## 5. Failure taxonomy

Use explicit categories instead of generic "wrong answer":

- intent classification failure;
- missing or incorrect entity resolution;
- retrieval miss;
- stale/low-authority source used;
- conflicting-source resolution failure;
- tool-selection failure;
- tool-result interpretation failure;
- unsupported claim / hallucination;
- incomplete answer;
- policy misunderstanding;
- customer/account isolation failure;
- ambiguity handling failure;
- adversarial or prompt-injection failure;
- unsafe action execution path.

## 6. Golden-set design

The golden set should be intentionally stratified rather than sampled only from easy examples.

Target buckets:
- straightforward factual lookups;
- policy questions;
- multi-step policy + operational-data questions;
- multi-intent questions;
- missing-context questions;
- contradictory-source questions;
- stale-policy traps;
- customer-isolation cases;
- unsupported-request cases;
- escalation/action cases;
- adversarial/prompt-injection-like cases.

Avoid train/evaluation leakage through exact or near duplicates.

## 7. Experiment loop

1. Freeze the baseline.
2. Run the golden set.
3. Inspect failed cases.
4. Group failures.
5. Make one coherent improvement.
6. Re-run the same golden set.
7. Record the metric delta and qualitative trade-offs.
8. Repeat only where the evidence justifies another change.

## 8. Non-negotiable engineering constraints

- Original ParcelPilot repositories are not the submission repository.
- No secrets in git.
- Tenant/account authorization remains enforced outside the LLM.
- State-changing operations remain confirmation-gated.
- Evaluation artifacts are reproducible from committed scripts and data.
- The README must explain both what works and what still fails.
