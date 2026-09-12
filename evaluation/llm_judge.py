from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.agent.prompts import JUDGE_PROMPT
from app.config import settings


JUDGE_SCHEMA = {
    'type': 'object',
    'properties': {
        'correctness': {'type': 'integer'},
        'groundedness': {'type': 'integer'},
        'completeness': {'type': 'integer'},
        'relevance': {'type': 'integer'},
        'policy_compliance': {'type': 'integer'},
        'isolation': {'type': 'integer'},
        'reason': {'type': 'string'},
    },
    'required': ['correctness','groundedness','completeness','relevance','policy_compliance','isolation','reason'],
    'additionalProperties': False,
}


def judge(question: str, answer: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    if not settings.openai_api_key:
        raise RuntimeError('OPENAI_API_KEY is required for LLM-as-judge')
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.model,
        instructions=JUDGE_PROMPT,
        input=json.dumps({'question': question, 'answer': answer, 'evidence': evidence}, ensure_ascii=False, default=str),
        text={'format': {'type': 'json_schema', 'name': 'support_judge', 'schema': JUDGE_SCHEMA, 'strict': True}},
    )
    return json.loads(response.output_text)
