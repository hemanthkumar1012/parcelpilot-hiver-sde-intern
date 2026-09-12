from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.config import settings
from app.retrieval.twitter_retriever import HistoricalReplyRetriever


SYSTEM_PROMPT = """You are a customer-support copilot for one brand.

Your job has three outputs:
1. classify the customer message into exactly one provided intent;
2. draft a concise reply grounded in retrieved historical resolutions;
3. decide AUTO or ESCALATE and give a concrete reason.

Rules:
- Treat retrieved historical replies as examples, not unquestionable facts.
- Never invent a policy, product capability, refund, repair entitlement, timeline, or account fact.
- If the historical evidence is weak, conflicting, or absent, escalate instead of pretending certainty.
- Do not expose hidden reasoning. Return only the requested structured fields.
- A reply should sound like a support agent, not a research report.
- Escalate when the issue requires account-specific verification, sensitive/security handling, high-impact billing decisions, unclear identity, or evidence is insufficient.
"""


class TwitterSupportAgent:
    def __init__(self, retriever: HistoricalReplyRetriever, intents: list[dict[str, Any]]):
        self.retriever = retriever
        self.intents = intents
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def answer(self, message: str) -> dict[str, Any]:
        evidence = self.retriever.search(message, settings.top_k)
        if not self.client:
            return {
                "intent": "unknown",
                "reply": "I’m sorry, but I don’t have enough information to answer this safely. A human support agent should review it.",
                "decision": "ESCALATE",
                "reason": "LLM is not configured.",
                "evidence": evidence,
            }

        prompt = {
            "brand": settings.brand,
            "customer_message": message,
            "intent_taxonomy": self.intents,
            "historical_examples": evidence,
            "output_schema": {
                "intent": "one taxonomy id",
                "reply": "draft support reply",
                "decision": "AUTO or ESCALATE",
                "reason": "short evidence-based reason",
                "confidence": "number from 0 to 1"
            },
        }
        response = self.client.responses.create(
            model=settings.model,
            instructions=SYSTEM_PROMPT,
            input=json.dumps(prompt, ensure_ascii=False),
        )
        text = response.output_text.strip()
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            result = {
                "intent": "unknown",
                "reply": text,
                "decision": "ESCALATE",
                "reason": "Model did not return the required structured output.",
                "confidence": 0.0,
            }
        result["evidence"] = evidence
        return result
