from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import pandas as pd

from app.retrieval.retriever import SupportRetriever


@dataclass
class ToolResult:
    name: str
    ok: bool
    data: Any
    note: str = ''


def _norm(value: Any) -> str:
    return str(value).strip().lower()


class SupportTools:
    def __init__(self, tables: dict[str, pd.DataFrame] | None = None, documents: list[dict[str, Any]] | None = None):
        self.tables = tables or {}
        self.documents = documents or []
        self.retriever = SupportRetriever(self.documents, self.tables)

    def table_lookup(self, sheet: str, field: str, value: str) -> ToolResult:
        df = self.tables.get(sheet)
        if df is None:
            return ToolResult('table_lookup', False, None, f'Unknown sheet: {sheet}')
        if field not in df.columns:
            return ToolResult('table_lookup', False, None, f'Unknown field: {field}')
        mask = df[field].map(_norm) == _norm(value)
        rows = df.loc[mask].head(10).to_dict(orient='records')
        return ToolResult('table_lookup', True, rows, f'{len(rows)} matching rows')

    def search_documents(self, query: str, limit: int = 5) -> ToolResult:
        hits = self.retriever.search_documents(query, top_k=limit)
        return ToolResult('document_search', True, hits, f'{len(hits)} ranked evidence chunks')

    def available_tools(self) -> list[str]:
        return ['table_lookup', 'document_search']
