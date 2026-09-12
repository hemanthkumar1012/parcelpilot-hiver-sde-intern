from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvaluationResult:
    example_id: str
    correct: bool
    grounded: bool
    complete: bool
    relevant: bool
    isolated: bool = True
    abstained_correctly: bool = True
    notes: list[str] = field(default_factory=list)


@dataclass
class EvaluationSummary:
    total: int
    accuracy: float
    groundedness: float
    completeness: float
    relevance: float
    isolation: float
    abstention: float


def _rate(values: list[bool]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize(results: list[EvaluationResult]) -> EvaluationSummary:
    return EvaluationSummary(
        total=len(results),
        accuracy=_rate([r.correct for r in results]),
        groundedness=_rate([r.grounded for r in results]),
        completeness=_rate([r.complete for r in results]),
        relevance=_rate([r.relevant for r in results]),
        isolation=_rate([r.isolated for r in results]),
        abstention=_rate([r.abstained_correctly for r in results]),
    )


def category_breakdown(
    examples: list[dict[str, Any]],
    results: list[EvaluationResult],
) -> dict[str, dict[str, float]]:
    result_by_id = {r.example_id: r for r in results}
    buckets: dict[str, list[EvaluationResult]] = {}
    for example in examples:
        result = result_by_id.get(str(example.get("id")))
        if not result:
            continue
        buckets.setdefault(str(example.get("category", "uncategorized")), []).append(result)

    return {
        category: {
            "count": float(len(items)),
            "accuracy": _rate([r.correct for r in items]),
            "groundedness": _rate([r.grounded for r in items]),
            "completeness": _rate([r.complete for r in items]),
            "relevance": _rate([r.relevant for r in items]),
        }
        for category, items in sorted(buckets.items())
    }
