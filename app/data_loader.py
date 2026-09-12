from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any
import pandas as pd
from pypdf import PdfReader


def load_workbook(path: Path) -> dict[str, pd.DataFrame]:
    if not path.exists():
        return {}
    return pd.read_excel(path, sheet_name=None)


def load_pdfs(directory: Path) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not directory.exists():
        return []
    for path in sorted(directory.rglob('*.pdf')):
        try:
            reader = PdfReader(str(path))
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ''
                if text.strip():
                    grouped[path.name].append({'page': page_number, 'text': text.strip()})
        except Exception as exc:
            grouped[path.name].append({'page': 0, 'text': '', 'error': str(exc)})
    return [{'filename': filename, 'pages': pages} for filename, pages in grouped.items()]


def discover_assets(data_dir: Path, knowledge_dir: Path) -> dict[str, Any]:
    workbooks = sorted(data_dir.rglob('*.xlsx')) + sorted(data_dir.rglob('*.xls')) if data_dir.exists() else []
    return {
        'workbooks': workbooks,
        'pdfs': sorted(knowledge_dir.rglob('*.pdf')) if knowledge_dir.exists() else [],
        'data_dir_exists': data_dir.exists(),
        'knowledge_dir_exists': knowledge_dir.exists(),
    }
