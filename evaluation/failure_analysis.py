from __future__ import annotations

from collections import Counter
from typing import Any

FAILURE_CATEGORIES = {
    'wrong_intent', 'entity_resolution', 'retrieval_miss', 'authority_conflict',
    'tool_selection', 'tool_interpretation', 'hallucination', 'incomplete',
    'policy_error', 'isolation', 'ambiguity', 'adversarial', 'unsafe_action'
}


def validate_category(category: str) -> str:
    if category not in FAILURE_CATEGORIES:
        raise ValueError(f'Unknown failure category: {category}')
    return category


def summarize_failures(rows: list[dict[str, Any]]) -> dict[str, Any]:
    failures = [row for row in rows if not bool(row.get('passed', False))]
    categories = Counter(validate_category(str(row['failure_category'])) for row in failures if row.get('failure_category'))
    return {
        'total_failures': len(failures),
        'by_category': dict(categories),
        'priority_order': [name for name, _ in categories.most_common()],
    }
