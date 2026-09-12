from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = {
    "tweet_id",
    "author_id",
    "inbound",
    "created_at",
    "text",
    "response_tweet_id",
    "in_response_to_tweet_id",
}


class TwitterSupportDataset:
    """Loader and lightweight conversation utilities for the Hiver TWCS task."""

    def __init__(self, csv_path: Path, brand: str = "AppleSupport") -> None:
        self.csv_path = csv_path
        self.brand = brand
        self.df = self._load()
        self.by_id = self.df.set_index("tweet_id", drop=False)

    def _load(self) -> pd.DataFrame:
        if not self.csv_path.exists():
            return pd.DataFrame(columns=sorted(REQUIRED_COLUMNS))
        df = pd.read_csv(self.csv_path)
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
        df = df.copy()
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
        df["tweet_id"] = df["tweet_id"].astype(str)
        df["text"] = df["text"].fillna("").astype(str).str.strip()
        df["author_id"] = df["author_id"].astype(str)
        df["inbound"] = df["inbound"].astype(bool)
        return df.drop_duplicates("tweet_id").sort_values("created_at")

    def brand_tweets(self) -> pd.DataFrame:
        return self.df[self.df["author_id"].eq(self.brand)].copy()

    def customer_messages(self) -> pd.DataFrame:
        """Customer turns that directly precede a reply from the selected brand."""
        brand = self.brand_tweets()
        if brand.empty:
            return pd.DataFrame()
        parent_ids = brand["in_response_to_tweet_id"].dropna().astype(str)
        customer = self.df[self.df["tweet_id"].isin(parent_ids) & self.df["inbound"]].copy()
        customer["brand"] = self.brand
        customer["historical_reply"] = customer["tweet_id"].map(
            brand.set_index("in_response_to_tweet_id")["text"]
        )
        return customer.dropna(subset=["historical_reply"])

    def sample_pairs(self, n: int = 250, random_state: int = 42) -> pd.DataFrame:
        pairs = self.customer_messages()
        if pairs.empty:
            return pairs
        pairs = pairs[pairs["text"].str.len().between(3, 1000)]
        return pairs.sample(min(n, len(pairs)), random_state=random_state)

    def describe(self) -> dict[str, Any]:
        brand_df = self.brand_tweets()
        pairs = self.customer_messages()
        return {
            "rows": int(len(self.df)),
            "brands_or_authors": int(self.df["author_id"].nunique()),
            "selected_brand": self.brand,
            "brand_rows": int(len(brand_df)),
            "customer_reply_pairs": int(len(pairs)),
            "date_min": self.df["created_at"].min().isoformat() if not self.df.empty else None,
            "date_max": self.df["created_at"].max().isoformat() if not self.df.empty else None,
        }
