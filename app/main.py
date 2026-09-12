from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.agent.twitter_agent import TwitterSupportAgent
from app.config import settings
from app.retrieval.twitter_retriever import HistoricalReplyRetriever
from app.twitter_data import TwitterSupportDataset

app = FastAPI(title="Hiver SDE Intern - AI Support Agent", version="1.0.0")


ROOT = Path(__file__).resolve().parents[1]
INTENT_PATH = ROOT / "evaluation" / "intent_taxonomy_v0.json"
TRAIN_PATH = ROOT / "data" / "processed" / "support_pairs_train.jsonl"


def load_intents() -> list[dict]:
    data = json.loads(INTENT_PATH.read_text(encoding="utf-8"))
    return data.get("intents", [])


def load_pairs() -> pd.DataFrame:
    if TRAIN_PATH.exists():
        return pd.read_json(TRAIN_PATH, lines=True)
    dataset = TwitterSupportDataset(settings.twcs_csv, settings.brand)
    return dataset.customer_messages()


_pairs = load_pairs()
_agent = TwitterSupportAgent(HistoricalReplyRetriever(_pairs), load_intents())


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "brand": settings.brand,
        "dataset_present": settings.twcs_csv.exists(),
        "historical_pairs_loaded": len(_pairs),
        "model": settings.model,
    }


@app.post("/chat")
def chat(request: ChatRequest) -> dict:
    return _agent.answer(request.message)
