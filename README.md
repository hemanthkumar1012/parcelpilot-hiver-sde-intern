# ParcelPilot Hiver SDE Intern

Hiver SDE Intern assignment workspace built from the ParcelPilot support-agent foundation.

## Goal

Build an evidence-first AI customer-support agent and demonstrate that it works through reproducible evaluation, golden-set testing, LLM-as-judge, and failure analysis.

## Repository boundary

This repository is intentionally separate from the original ParcelPilot repositories. Hiver-specific work belongs here; the original ParcelPilot projects remain unchanged.

## Planned system

```text
Support dataset
      |
      v
Data understanding / cleaning
      |
      +--> Baseline
      |
      v
Support agent
  + retrieval
  + operational tools
  + policy precedence
  + grounded answer generation
      |
      v
Golden-set evaluation
      |
      +--> LLM-as-judge
      +--> deterministic checks
      +--> failure categories
      |
      v
Failure analysis --> Agent improvements --> Re-evaluation
```

## Current source assets

The ParcelPilot AI support-agent implementation already provides account-scoped lookup, document retrieval, policy/source precedence, SLA reasoning, action preparation, confirmation gating, a FastAPI service, a browser UI, tests, PDFs, and a workbook. The integrated ParcelPilot platform additionally provides a FastAPI/PostgreSQL application and authenticated chat surface.

The Hiver project will retain the strongest reusable pieces while making evaluation and experimental evidence first-class.

## Data safety

Do not commit real API keys, `.env` files, credentials, or generated secrets. Public assessment/sample data may be included when appropriate.

## Status

Phase 0: repository initialized.

Phase 1: source audit and Hiver architecture underway.
