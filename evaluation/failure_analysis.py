from __future__ import annotations

from collections import Counter
from typing import Any

FAILURE_CATEGORIES = {
    'wrong_intent', 'entity_resolution', 'retrieval_miss', 'authority_conflict',
    'tool_selection', 'tool_interpretation', 'hallucination', 'incomplete',
    'policy_error', 'isolation', 'ambiguity', 'adversarial', 'unsafe_action'
}


def summarize_failures(rows: list[dict[str, Any]]) -> dict[str, Any]:
    categories = Counter(row.get('failure_category') for row in rows if row.get('failure_category'))
    invalid = sorted(set(categories) - FAILURE_CATEGORIES)
    return {
        'total_failures': sum(categories.values()),
        'by_category': dict(categories),
        'unknown_categories': invalid,
        'priority_order': [name for name, _ in categories.most_common()],
    }
