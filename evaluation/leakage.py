from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class LeakageReport:
    exact_duplicate_pairs: list[tuple[str, str]]
    near_duplicate_pairs: list[tuple[str, str, float]]


def _normalized(text: str) -> str:
    return " ".join(str(text).casefold().split())


def inspect_examples(examples: list[dict[str, Any]], threshold: float = 0.92) -> LeakageReport:
    exact: list[tuple[str, str]] = []
    near: list[tuple[str, str, float]] = []
    normalized = [_normalized(item.get("question", "")) for item in examples]

    for i in range(len(examples)):
        for j in range(i + 1, len(examples)):
            if normalized[i] and normalized[i] == normalized[j]:
                exact.append((str(examples[i].get("id")), str(examples[j].get("id"))))

    non_empty = [text if text else "<empty>" for text in normalized]
    if len(non_empty) >= 2:
        matrix = TfidfVectorizer(ngram_range=(1, 2), stop_words="english").fit_transform(non_empty)
        scores = cosine_similarity(matrix)
        for i in range(len(examples)):
            for j in range(i + 1, len(examples)):
                score = float(scores[i, j])
                if score >= threshold and normalized[i] != normalized[j]:
                    near.append((str(examples[i].get("id")), str(examples[j].get("id")), round(score, 4)))

    return LeakageReport(exact, near)
