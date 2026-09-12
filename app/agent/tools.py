from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import pandas as pd


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
        terms = {_norm(t) for t in query.split() if len(t) > 2}
        scored = []
        for doc in self.documents:
            text = _norm(doc.get('text', ''))
            score = sum(term in text for term in terms)
            if score:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return ToolResult('document_search', True, [doc for _, doc in scored[:limit]], f'{min(limit, len(scored))} documents')

    def available_tools(self) -> list[str]:
        return ['table_lookup', 'document_search']
