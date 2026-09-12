from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.twitter_data import TwitterSupportDataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a reproducible TWCS brand sample.")
    parser.add_argument("--csv", type=Path, default=Path("data/raw/twcs.csv"))
    parser.add_argument("--brand", default="AppleSupport")
    parser.add_argument("--sample", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    dataset = TwitterSupportDataset(args.csv, args.brand)
    pairs = dataset.customer_messages()
    if pairs.empty:
        print(json.dumps({"status": "missing_or_empty", "summary": dataset.describe()}, indent=2))
        return 1

    # Chronological holdout prevents near-identical future conversations leaking into evaluation.
    pairs = pairs.sort_values("created_at")
    cutoff = int(len(pairs) * 0.8)
    train = pairs.iloc[:cutoff]
    holdout = pairs.iloc[cutoff:]
    if len(train) > args.sample:
        train = train.sample(args.sample, random_state=args.seed)

    out = Path("data/processed")
    out.mkdir(parents=True, exist_ok=True)
    train[["tweet_id", "created_at", "text", "historical_reply", "brand"]].to_json(
        out / "support_pairs_train.jsonl", orient="records", lines=True, force_ascii=False
    )
    holdout[["tweet_id", "created_at", "text", "historical_reply", "brand"]].to_json(
        out / "support_pairs_holdout.jsonl", orient="records", lines=True, force_ascii=False
    )

    summary = {
        "dataset": "thoughtvector/customer-support-on-twitter",
        "brand": args.brand,
        "all_rows": len(dataset.df),
        "paired_customer_messages": len(pairs),
        "train_rows": len(train),
        "holdout_rows": len(holdout),
        "split": "chronological 80/20 before train subsampling",
        "seed": args.seed,
    }
    (out / "dataset_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
