from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.agent.agent import SupportAgent


def run_baseline(agent: SupportAgent, questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run a fixed baseline over a question set without changing the data or prompts."""
    outputs: list[dict[str, Any]] = []
    for item in questions:
        result = agent.answer(
            question=str(item["question"]),
            account_id=item.get("account_id"),
            role=str(item.get("user_role", "customer")),
        )
        outputs.append({
            "id": str(item.get("id", len(outputs))),
            "question": item["question"],
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "tool_trace": result.get("tool_trace", []),
        })
    return outputs


if __name__ == "__main__":
    from app.main import agent

    path = Path(__file__).with_name("golden_set.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    examples = payload.get("examples", [])
    if not examples:
        raise SystemExit("golden_set.json is empty; load the assessment data before running the baseline.")
    print(json.dumps(run_baseline(agent, examples), indent=2, ensure_ascii=False, default=str))
