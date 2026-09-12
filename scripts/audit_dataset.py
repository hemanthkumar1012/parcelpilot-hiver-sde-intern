from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from app.data_loader import discover_assets, load_pdfs, load_workbook


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT = ROOT / "evaluation" / "reports" / "dataset_audit.json"


def profile_dataframe(name: str, df: pd.DataFrame) -> dict[str, Any]:
    columns = []
    for column in df.columns:
        series = df[column]
        non_null = series.dropna()
        samples = [str(x)[:120] for x in non_null.head(3).tolist()]
        columns.append(
            {
                "name": str(column),
                "dtype": str(series.dtype),
                "null_count": int(series.isna().sum()),
                "null_rate": round(float(series.isna().mean()), 4),
                "unique_count": int(series.nunique(dropna=True)),
                "sample_values": samples,
            }
        )

    normalized = df.astype(str).replace("nan", "")
    duplicate_rows = int(normalized.duplicated().sum()) if not df.empty else 0
    likely_ids = [
        str(c) for c in df.columns
        if any(token in str(c).casefold() for token in ("id", "number", "email", "tracking", "ticket", "order"))
    ]
    return {
        "sheet": name,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicate_rows": duplicate_rows,
        "likely_identifier_columns": likely_ids,
        "columns_profile": columns,
    }


def main() -> int:
    assets = discover_assets(DATA_DIR)
    report: dict[str, Any] = {
        "status": "ok",
        "data_directory": str(DATA_DIR),
        "workbooks": [str(p.relative_to(ROOT)) for p in assets["workbooks"]],
        "pdfs": [str(p.relative_to(ROOT)) for p in assets["pdfs"]],
        "workbook_profiles": [],
        "document_profiles": [],
        "notes": [],
    }

    if not assets["workbooks"] and not assets["pdfs"]:
        report["status"] = "assets_missing"
        report["notes"].append("Place the assessment XLSX/XLS in data/raw and support PDFs in knowledge_base before auditing.")
    else:
        for workbook in assets["workbooks"]:
            for sheet, df in load_workbook(workbook).items():
                report["workbook_profiles"].append(profile_dataframe(sheet, df))

        for pdf in assets["pdfs"]:
            pages = load_pdfs([pdf]).get(pdf.name, [])
            report["document_profiles"].append(
                {
                    "filename": pdf.name,
                    "pages": len(pages),
                    "non_empty_pages": sum(bool(str(p.get("text", "")).strip()) for p in pages),
                    "characters": sum(len(str(p.get("text", ""))) for p in pages),
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
