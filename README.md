# Hiver SDE Intern — AI Support Agent

A reproducible AI customer-support system for the Hiver take-home assignment. The implementation uses the **Customer Support on Twitter (TWCS)** dataset and currently focuses on **AmazonHelp**, selected after auditing brand support volume.

## What the system must prove

For an incoming customer message, the system should:

1. classify the message into a small intent taxonomy derived from the selected brand's data;
2. retrieve historically similar customer issues and the support responses used for them;
3. draft a grounded support reply rather than inventing policy;
4. decide **AUTO** vs **ESCALATE** and provide a reason;
5. demonstrate performance with a leakage-safe golden set, trivial and simple baselines, automated metrics, LLM-as-judge evaluation, human-vs-judge agreement, and failure analysis.

The assignment values evidence over an impressive-looking headline score. The final report therefore includes explicit limitations and a section titled **What is misleading about my headline number?**

## Architecture

```text
TWCS (~2.8M rows in the audited file)
        │
        ▼
Streaming data audit
        │
        ├── schema / nulls / duplicates
        ├── inbound vs outbound
        └── support-brand volume
        │
        ▼
AmazonHelp
        │
        ▼
Conversation-aware reconstruction
        │
        ├── customer turn
        ├── prior context
        └── historical AmazonHelp reply
        │
        ▼
Leakage-safe train / validation / test split
        │
        ├── Baseline 0: majority / always-escalate
        ├── Baseline 1: TF-IDF retrieval
        └── Agent V1
             ├── intent
             ├── historical retrieval
             ├── grounded draft
             └── AUTO / ESCALATE + reason
        │
        ▼
Golden evaluation set (150–250)
        │
        ├── automated metrics
        ├── LLM-as-judge
        ├── human-vs-judge agreement
        └── failure analysis
        │
        ▼
V2 improvements → re-evaluation
```

## Dataset audit

The local audit found **2,811,774 tweets**, with **1,537,843 inbound customer rows** and **1,273,931 outbound support rows**. Duplicate tweet IDs were not observed. The selected brand is **AmazonHelp**, which had the largest outbound support volume in the audit: **169,840** tweets.

The raw file is intentionally kept local and is never committed to Git.

## Reproducible data pipeline

Expected dataset location:

```text
data/raw/twcs.csv
```

### 1. Audit the source

```bash
python scripts/audit_dataset.py --csv data/raw/twcs.csv
```

### 2. Extract AmazonHelp customer → support pairs

```bash
python scripts/prepare_twcs.py --csv data/raw/twcs.csv
```

The extraction is streaming-based so the full 500+ MB CSV does not need to be loaded into a single pandas DataFrame.

### 3. Profile the extracted corpus

```bash
python scripts/profile_pairs.py
```

### 4. Build deterministic modeling splits

```bash
python scripts/build_dataset.py
```

### 5. Explore candidate intents

```bash
python scripts/discover_intents.py
```

The intent-discovery output is explicitly a **working hypothesis**, not ground-truth labels. Final intent definitions will be human-reviewed and validated on held-out examples.

Generated bulk datasets and evaluation reports remain local during development.

## Evaluation strategy

### Baseline 0 — trivial

A deliberately weak reference system: majority-class intent prediction and always-escalate handling. This establishes the floor without pretending to solve the task.

### Baseline 1 — simple

TF-IDF nearest-neighbour retrieval over historical customer messages, returning the associated historical support response.

### Agent V1

Intent classification + historical retrieval + grounded reply drafting + escalation decision.

### Agent V2

Only changes justified by observed failures, such as better retrieval, conversation context, hard-negative handling, calibrated escalation thresholds, or revised intent boundaries.

## Golden evaluation set

Target: **150–250 hand-labelled examples** sampled from the selected-brand corpus and kept isolated from training/retrieval.

Sampling will deliberately cover common and rare intents, noisy or short messages, ambiguous requests, multi-intent messages, weak historical matches, escalation-worthy cases, and unsupported/adversarial requests.

The repository will not fabricate labels or expected answers. Every benchmark example must come from the actual assessed data and its documented labelling process.

## Required metrics

The final evaluation will report multiple views rather than one aggregate score:

- intent accuracy and macro-F1;
- retrieval quality;
- reply correctness, relevance, completeness, and groundedness;
- AUTO / ESCALATE quality;
- LLM-as-judge score;
- human-vs-judge agreement;
- performance by intent and difficulty bucket;
- top failure modes with real examples.

### What is misleading about my headline number?

The report will explicitly examine whether the aggregate score is inflated by class imbalance, easy/repetitive messages, data leakage across conversation turns, repeated templates, judge preference for fluent answers, weak coverage of rare escalation cases, or disagreement between human labels and the LLM judge.

## Decision log

Every non-obvious engineering decision is recorded with its rationale, alternatives considered, and expected trade-off. This includes dataset/brand selection, filtering, conversation reconstruction, split strategy, retrieval design, escalation policy, evaluation sampling, and model/provider choices.

## Current implementation status

Completed in the working branch:

- streaming TWCS audit;
- AmazonHelp selection based on observed support volume;
- streaming customer → AmazonHelp pair extraction;
- extracted-corpus profiling;
- deterministic modeling split generation;
- data-derived intent discovery;
- repository safeguards for raw and generated datasets;
- AmazonHelp working intent taxonomy.

In progress:

- conversation-level reconstruction and leakage-safe splitting;
- robust historical-reply selection when a customer turn has multiple support replies;
- FastAPI service alignment with the new AmazonHelp dataset;
- retrieval baseline;
- intent baseline;
- golden-set creation;
- automated evaluation and LLM-as-judge agreement study;
- failure analysis and final report.

## Run the service

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload
```

Then open `/docs` and call `/health` or `/chat`.

The final README will include the exact benchmark command and headline results only after the leakage-safe evaluation is actually run.
