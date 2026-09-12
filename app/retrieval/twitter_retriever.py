from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class HistoricalReplyRetriever:
    """Retrieve historically resolved customer issues from the selected brand."""

    def __init__(self, pairs: pd.DataFrame):
        self.pairs = pairs.copy()
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        if not self.pairs.empty:
            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                min_df=2,
            )
            self.matrix = self.vectorizer.fit_transform(self.pairs["text"].fillna(""))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if not query.strip() or self.vectorizer is None or self.matrix is None:
            return []
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix).ravel()
        ranked = scores.argsort()[::-1][:top_k]
        results = []
        for index in ranked:
            score = float(scores[index])
            if score <= 0:
                continue
            row = self.pairs.iloc[int(index)]
            results.append(
                {
                    "score": round(score, 4),
                    "tweet_id": str(row.get("tweet_id", "")),
                    "customer_message": str(row.get("text", "")),
                    "historical_reply": str(row.get("historical_reply", "")),
                    "created_at": str(row.get("created_at", "")),
                    "brand": str(row.get("brand", "")),
                }
            )
        return results
