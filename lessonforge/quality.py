import re
from .reference_facts import RAG_KNOWN_FALSE_CLAIMS

REQUIRED_SECTIONS = (
    "what is it?", "why do we need it?", "how does it work?",
    "practical example", "important terms", "benefits and limitations",
    "summary", "quick quiz",
)


def deterministic_checks(lesson: str) -> dict:
    lower = lesson.lower()
    missing = [section for section in REQUIRED_SECTIONS if section not in lower]
    known_false_claims = [claim for claim in RAG_KNOWN_FALSE_CLAIMS if claim in lower]
    quiz_section = lower.split("quick quiz", 1)[1] if "quick quiz" in lower else ""
    quiz_question_count = len(re.findall(r"(?:^|\n)\s*(?:\d+[.)]|[-*])\s*", quiz_section))
    word_count = len(re.findall(r"\b[\w'-]+\b", lesson))
    return {
        "missing_sections": missing,
        "known_false_claims": known_false_claims,
        "wrong_demo_definition": "rag stands for random answer generation" in lower,
        "quiz_question_count": quiz_question_count,
        "word_count": word_count,
    }


def apply_deterministic_overrides(results: dict, lesson: str) -> dict:
    """Apply hard, repeatable checks after the LLM evaluation."""
    checks = deterministic_checks(lesson)
    if checks["missing_sections"]:
        results["key_coverage"] = {
            "status": "FAIL",
            "reason": "Missing required sections: " + ", ".join(checks["missing_sections"]),
            "correction": "Add every required section in the requested order.",
        }
    if checks["known_false_claims"]:
        results["accuracy"] = {
            "status": "FAIL",
            "reason": "Known false claim detected: " + "; ".join(checks["known_false_claims"]),
            "correction": "Correct the false claim using the trusted RAG reference facts.",
        }
    if checks["quiz_question_count"] != 3:
        results["key_coverage"] = {
            "status": "FAIL",
            "reason": f"Expected exactly 3 quiz questions; found {checks['quiz_question_count']}.",
            "correction": "Add exactly three numbered quiz questions under Quick quiz.",
        }
    results["deterministic_validation"] = checks
    return results
