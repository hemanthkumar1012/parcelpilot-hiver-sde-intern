from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "evaluation" / "golden_set.schema.json"
GOLDEN_PATH = ROOT / "evaluation" / "golden_set.json"


def validate() -> list[str]:
    errors: list[str] = []
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    data = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        return ["Golden set root must be an object."]
    examples = data.get("examples")
    if not isinstance(examples, list):
        return ["Golden set must contain an 'examples' list."]

    required = schema.get("required", [])
    ids: set[str] = set()
    for index, item in enumerate(examples):
        prefix = f"examples[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        for field in required:
            if field not in item:
                errors.append(f"{prefix}: missing required field '{field}'")
        item_id = str(item.get("id", "")).strip()
        if not item_id:
            errors.append(f"{prefix}: id cannot be empty")
        elif item_id in ids:
            errors.append(f"{prefix}: duplicate id '{item_id}'")
        ids.add(item_id)

        question = str(item.get("question", "")).strip()
        if not question:
            errors.append(f"{prefix}: question cannot be empty")
        expected = item.get("expected", {})
        if not isinstance(expected, dict):
            errors.append(f"{prefix}: expected must be an object")
            continue
        points = expected.get("answer_points", [])
        if not isinstance(points, list):
            errors.append(f"{prefix}: expected.answer_points must be a list")
        sources = expected.get("required_sources", [])
        if not isinstance(sources, list):
            errors.append(f"{prefix}: expected.required_sources must be a list")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Golden set validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Golden set validation PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
