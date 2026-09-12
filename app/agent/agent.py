from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import SupportTools
from app.config import settings


class SupportAgent:
    def __init__(self, tools: SupportTools):
        self.tools = tools
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def retrieve(self, question: str, account_id: str | None = None) -> dict[str, Any]:
        docs = self.tools.search_documents(question, settings.top_k).data
        trace: list[dict[str, Any]] = [{'tool': 'document_search', 'count': len(docs)}]
        if account_id:
            trace.append({'account_scope': account_id})
        return {'documents': docs, 'tool_trace': trace}

    def answer(self, question: str, account_id: str | None = None, role: str = 'customer') -> dict[str, Any]:
        context = self.retrieve(question, account_id)
        evidence = context['documents']
        if not self.client:
            return {
                'answer': 'LLM is not configured. The retrieval layer found no safe generated answer.',
                'sources': evidence,
                'tool_trace': context['tool_trace'],
                'requires_confirmation': False,
            }

        evidence_text = json.dumps(evidence, ensure_ascii=False, default=str)[:24000]
        user_input = (
            f'Customer role: {role}\n'
            f'Account ID: {account_id or "not provided"}\n'
            f'Question: {question}\n\n'
            f'Retrieved evidence:\n{evidence_text}'
        )
        response = self.client.responses.create(
            model=settings.model,
            instructions=SYSTEM_PROMPT,
            input=user_input,
        )
        return {
            'answer': response.output_text,
            'sources': evidence,
            'tool_trace': context['tool_trace'],
            'requires_confirmation': False,
        }
