from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SOURCE_PRIORITY = {
    "signed_agreement": 100,
    "current_policy": 90,
    "current_sop": 85,
    "current_product": 80,
    "historical_context": 30,
    "deprecated": 0,
}


def classify_source(filename: str) -> tuple[str, int]:
    name = filename.casefold()
    if "northstar" in name or "lumenworks" in name:
        return "signed_agreement", SOURCE_PRIORITY["signed_agreement"]
    if "deprecated" in name:
        return "deprecated", 0
    if "support_policy_v3_current" in name:
        return "current_policy", SOURCE_PRIORITY["current_policy"]
    if "cancellation_and_service_credit_sop" in name:
        return "current_sop", SOURCE_PRIORITY["current_sop"]
    if "product_operations_guide" in name:
        return "current_product", SOURCE_PRIORITY["current_product"]
    return "historical_context", SOURCE_PRIORITY["historical_context"]


class SupportRetriever:
    """Lightweight, reproducible retrieval over supplied support documents.

    Retrieval score is kept separate from source authority. Authority determines
    which source wins when documents conflict; similarity determines relevance.
    """

    def __init__(
        self,
        documents: list[dict[str, Any]] | None = None,
        tables: dict[str, pd.DataFrame] | None = None,
    ) -> None:
        self.documents = documents or []
        self.tables = tables or {}
        self._chunks: list[dict[str, Any]] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._build_index()

    def _build_index(self) -> None:
        chunks: list[dict[str, Any]] = []
        for document in self.documents:
            authority, priority = classify_source(str(document.get("filename", "")))
            for page in document.get("pages", []):
                text = str(page.get("text", "")).strip()
                if not text:
                    continue
                chunks.append(
                    {
                        "filename": document.get("filename", ""),
                        "page": page.get("page"),
                        "text": text,
                        "authority": authority,
                        "priority": priority,
                    }
                )

        self._chunks = chunks
        if not chunks:
            return

        self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self._matrix = self._vectorizer.fit_transform([x["text"] for x in chunks])

    def search_documents(
        self,
        query: str,
        top_k: int = 5,
        include_deprecated: bool = False,
    ) -> list[dict[str, Any]]:
        if not query.strip() or not self._chunks or self._vectorizer is None:
            return []

        scores = cosine_similarity(
            self._vectorizer.transform([query]), self._matrix
        ).ravel()

        ranked: list[dict[str, Any]] = []
        for index, score in enumerate(scores):
            chunk = self._chunks[index].copy()
            if chunk["authority"] == "deprecated" and not include_deprecated:
                continue
            chunk["score"] = float(score)
            ranked.append(chunk)

        ranked.sort(key=lambda x: (-x["priority"], -x["score"]))
        return [item for item in ranked[:top_k] if item["score"] > 0]

    def table_lookup(self, table: str, key_column: str, key_value: str) -> dict[str, Any]:
        dataframe = self.tables.get(table)
        if dataframe is None or dataframe.empty or key_column not in dataframe.columns:
            return {"found": False, "table": table, "key": key_value}

        matches = dataframe.loc[
            dataframe[key_column].astype(str).str.casefold()
            == str(key_value).casefold()
        ]
        if matches.empty:
            return {"found": False, "table": table, "key": key_value}
        return {"found": True, "table": table, "key": key_value, "row": matches.iloc[0].to_dict()}
