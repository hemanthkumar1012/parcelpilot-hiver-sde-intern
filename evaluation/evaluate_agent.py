from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.agent.agent import SupportAgent


def load_golden_set(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    return payload.get('examples', [])


def deterministic_match(answer: str, expected_points: list[str]) -> bool:
    text = answer.lower()
    return all(point.lower() in text for point in expected_points)


def evaluate(agent: SupportAgent, golden_path: Path) -> list[dict[str, Any]]:
    results = []
    for example in load_golden_set(golden_path):
        expected = example.get('expected', {})
        output = agent.answer(example['question'], example.get('account_id'))
        answer = output['answer']
        points = expected.get('answer_points', [])
        results.append({
            'id': example['id'],
            'answer': answer,
            'correct_deterministic': deterministic_match(answer, points),
            'sources_found': len(output.get('sources', [])),
            'tool_trace': output.get('tool_trace', []),
        })
    return results


if __name__ == '__main__':
    from app.main import agent
    path = Path(__file__).with_name('golden_set.json')
    print(json.dumps(evaluate(agent, path), indent=2, ensure_ascii=False))
