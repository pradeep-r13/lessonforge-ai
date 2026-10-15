from lessonforge.quality import deterministic_checks, apply_deterministic_overrides
from lessonforge.reference_facts import RUBRIC_CHECKS, RAG_KNOWN_FALSE_CLAIMS


def test_rubric_has_six_fixed_checks():
    assert len(RUBRIC_CHECKS) == 6


def test_demo_error_is_detected_as_false_claim():
    result = deterministic_checks("RAG stands for Random Answer Generation")
    assert result["wrong_demo_definition"] is True
    assert RAG_KNOWN_FALSE_CLAIMS[0] in result["known_false_claims"]


def test_missing_sections_fail_key_coverage():
    results = {name: {"status": "PASS", "reason": "ok", "correction": ""} for name in RUBRIC_CHECKS}
    checked = apply_deterministic_overrides(results, "Short lesson")
    assert checked["key_coverage"]["status"] == "FAIL"
