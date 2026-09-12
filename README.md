# Hiver SDE Intern — AI Support Agent

A reproducible AI customer-support system built for the Hiver take-home assignment.

## Assignment framing

The system uses the **Customer Support on Twitter (TWCS)** dataset and focuses on one brand. The current first-pass choice is **AppleSupport** because the dataset contains substantial support traffic for that brand. The brand choice is a decision, not a ground-truth assumption, and will be revisited after dataset audit.

The assignment asks the system to:

1. classify incoming customer messages into a small intent taxonomy derived from the data;
2. draft a reply grounded in historically resolved similar issues;
3. decide whether to auto-handle or escalate, with a stated reason;
4. prove performance using a 150–250 example golden set, baselines, LLM-as-judge, human agreement evidence, and failure analysis.

The public TWCS dataset contains tweet IDs, anonymized authors, inbound/outbound direction, timestamps, text, and response links, which allow customer/support turns to be reconstructed. citeturn0search3turn0search24

## Current architecture

```text
TWCS CSV
   │
   ├── data audit
   │      ├── quality
   │      ├── duplicates
   │      ├── missingness
   │      └── brand volume
   │
   ▼
Selected brand: AppleSupport
   │
   ▼
Conversation reconstruction
   │
   ├── customer message
   └── historical support reply
   │
   ▼
Chronological train / holdout split
   │
   ▼
Historical-response retrieval
   │
   ▼
LLM support agent
   ├── intent
   ├── grounded reply
   ├── AUTO / ESCALATE
   └── reason + confidence
   │
   ▼
Golden evaluation set
   │
   ├── intent metrics
   ├── reply quality
   ├── escalation quality
   ├── LLM-as-judge
   └── human-vs-judge agreement
   │
   ▼
Failure analysis → V2 → re-evaluation
```

## Why the historical-reply setup matters

We are not training a generic chatbot on arbitrary text. A customer message is matched against previously observed customer issues and their historical brand responses. Those responses are evidence for how the brand handled similar situations, rather than instructions that the model must blindly copy.

The dataset is known to be noisy and conversational: response links reconstruct multi-turn interactions, and the `inbound` field distinguishes customer-directed and company-originated turns. citeturn0search3turn0search9

## Reproducible pipeline

Expected dataset location:

```text
data/raw/twcs.csv
```

Prepare a bounded reproducible sample:

```bash
python scripts/prepare_twcs.py --csv data/raw/twcs.csv --brand AppleSupport --sample 5000 --seed 42
```

This creates:

```text
data/processed/support_pairs_train.jsonl
data/processed/support_pairs_holdout.jsonl
data/processed/dataset_summary.json
```

The split is chronological before train subsampling to reduce temporal leakage.

Run the service:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then use `/docs` or:

```text
POST /chat
{
  "message": "My iPhone keeps freezing after the update"
}
```

## Evaluation plan

### Baseline 0 — trivial

Always predict the most frequent intent and always escalate. This establishes a deliberately weak floor.

### Baseline 1 — simple

TF-IDF nearest-neighbour retrieval over historical customer messages, returning the associated historical response.

### Agent V1

LLM intent classification + historical-response retrieval + grounded reply drafting + escalation decision.

### V2

Improve only after inspecting failures. Possible changes include better retrieval, hard-negative handling, confidence calibration, multi-turn context, and intent-boundary revisions.

## Golden set

Target: **150–250 manually labelled examples**.

Sampling will be stratified across:

- common intents;
- rare intents;
- short/noisy messages;
- multi-intent messages;
- ambiguous requests;
- messages with weak historical matches;
- escalation-worthy cases;
- adversarial or unsupported requests.

The final labels will be created from the actual selected-brand data. The repository will not fabricate benchmark labels.

## Required evaluation

We will report more than one headline number:

- intent accuracy / macro-F1;
- reply correctness;
- groundedness;
- completeness;
- relevance;
- escalation precision/recall where applicable;
- LLM-judge score;
- human-vs-judge agreement;
- performance by intent and difficulty bucket;
- retrieval quality;
- top failure modes.

### Mandatory: What is misleading about my headline number?

The report will explicitly test whether aggregate performance is inflated by:

- dominant easy intents;
- duplicated or near-duplicated conversations;
- temporal leakage;
- repeated customer templates;
- judge bias toward fluent answers;
- weak coverage of rare/escalation cases;
- disagreement between human labels and the LLM judge.

## Decision log

Every non-obvious design choice will be recorded with the reason, alternatives considered, and expected trade-off.

## Data source

Primary dataset: Thought Vector's **Customer Support on Twitter** dataset on Kaggle. The dataset contains more than 3 million tweets/replies across many customer-support brands. citeturn0search0

## Current status

Implemented:

- TWCS data loader;
- AppleSupport selection as an initial hypothesis;
- customer → historical-support reply reconstruction;
- reproducible chronological preparation pipeline;
- historical response retrieval;
- initial intent taxonomy;
- LLM support-agent orchestration;
- FastAPI `/chat` and `/health` service;
- golden-set validation;
- duplicate/near-duplicate leakage checks;
- evaluation framework and failure taxonomy.

Next: run the actual dataset audit, revise the intent taxonomy from observed data, generate the 150–250 example golden set, implement the two required baselines, and produce the first honest V1 benchmark.
