from evaluation.leakage import inspect_examples
from evaluation.metrics import EvaluationResult, EvaluationSummary


def test_leakage_detects_exact_duplicates():
    examples = [
        {"id": "a", "question": "Where is order 123?"},
        {"id": "b", "question": " where is order 123? "},
    ]
    report = inspect_examples(examples)
    assert ("a", "b") in report.exact_duplicate_pairs


def test_summary_computes_means():
    results = [
        EvaluationResult("a", True, 1.0, 1.0, 0.5, 1.0, True),
        EvaluationResult("b", False, 0.0, 0.0, 1.0, 0.0, False),
    ]
    summary = EvaluationSummary.from_results(results)
    assert summary.total == 2
    assert summary.accuracy == 0.5
    assert summary.groundedness == 0.5
    assert summary.completeness == 0.75
