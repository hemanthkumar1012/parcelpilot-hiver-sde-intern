from evaluation.leakage import inspect_examples
from evaluation.metrics import EvaluationResult, summarize


def test_leakage_detects_exact_duplicates():
    examples = [
        {"id": "a", "question": "Where is order 123?"},
        {"id": "b", "question": " where is order 123? "},
    ]
    report = inspect_examples(examples)
    assert ("a", "b") in report.exact_duplicate_pairs


def test_summary_computes_means():
    results = [
        EvaluationResult("a", True, True, False, True),
        EvaluationResult("b", False, False, True, False),
    ]
    summary = summarize(results)
    assert summary.total == 2
    assert summary.accuracy == 0.5
    assert summary.groundedness == 0.5
    assert summary.completeness == 0.5
