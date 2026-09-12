from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.agent.agent import SupportAgent
from app.agent.tools import SupportTools
from app.config import settings
from app.data_loader import discover_assets, load_pdfs, load_workbook

app = FastAPI(title='ParcelPilot Hiver SDE Support Agent', version='0.1.0')


def build_agent() -> SupportAgent:
    assets = discover_assets(settings.data_dir, settings.knowledge_dir)
    tables = {}
    if assets['workbooks']:
        tables = load_workbook(assets['workbooks'][0])
    documents = load_pdfs(settings.knowledge_dir)
    return SupportAgent(SupportTools(tables=tables, documents=documents))

agent = build_agent()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    account_id: str | None = None
    user_role: str = 'customer'


@app.get('/health')
def health() -> dict:
    assets = discover_assets(settings.data_dir, settings.knowledge_dir)
    return {'status': 'ok', 'data_assets_present': bool(assets['workbooks'] or assets['pdfs']), 'workbooks': len(assets['workbooks']), 'pdfs': len(assets['pdfs'])}


@app.post('/chat')
def chat(request: ChatRequest) -> dict:
    return agent.answer(request.message, request.account_id, request.user_role)
