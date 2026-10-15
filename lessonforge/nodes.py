import os
from typing import TypedDict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from .schemas import LessonEvaluation
from .memory import save_attempt
from .reference_facts import RAG_REFERENCE_FACTS, RUBRIC_CHECKS
from .quality import apply_deterministic_overrides
from .routing import MAX_RETRIES, MAX_ATTEMPTS, route_after_evaluation


class LessonState(TypedDict, total=False):
    run_id: str
    topic: str
    lesson: str
    attempt_count: int
    evaluation_results: dict[str, Any]
    failed_checks: list[str]
    rejection_log: list[dict[str, Any]]
    final_status: str
    memory_feedback: str
    prompt_strategy: str
    demo_error: bool
    prompt_version: str
    feedback: str


def _llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY missing. Check your .env file.")
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        temperature=0,
        api_key=api_key,
    )


def generate_lesson(state: LessonState) -> dict:
    attempt = state.get("attempt_count", 0) + 1
    system = """You are a careful instructional writer. Create a standalone lesson for an Indian learner who has completed Class 12 and is new to AI. Use simple English, short sentences, and familiar examples.
Use these exact Markdown sections:
# {topic}
## What is it?
## Why do we need it?
## How does it work?
## Practical example
## Important terms
## Benefits and limitations
## Summary
## Quick quiz
Explain technical terms in plain words. Include one practical question and its answer. Include exactly three numbered quiz questions.
Use the trusted reference facts supplied below. Do not add unsupported claims. Address evaluator feedback. Never weaken the fixed rubric."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Topic: {topic}\nTrusted reference facts:\n{reference_facts}\nPrompt strategy: {prompt_strategy}\nPrevious evaluation feedback: {feedback}\nHistorical memory guidance: {memory_feedback}\nWrite the complete improved lesson.")
    ])
    chain = prompt | _llm()
    lesson = chain.invoke({
        "topic": state["topic"],
        "reference_facts": "\n".join(f"- {fact}" for fact in RAG_REFERENCE_FACTS),
        "prompt_strategy": state.get("prompt_strategy", "Use simple English and explain technical terms."),
        "feedback": state.get("feedback", "") if attempt > 1 else "",
        "memory_feedback": state.get("memory_feedback", ""),
    }).content
    if not isinstance(lesson, str):
        lesson = str(lesson)
    # Reproducible demo: the deterministic validator must catch this false statement.
    if state.get("demo_error") and attempt == 1:
        lesson += "\n\nDemo mistake: RAG stands for Random Answer Generation.\n"
    return {"lesson": lesson, "attempt_count": attempt}


def evaluate_lesson(state: LessonState) -> dict:
    lesson = state["lesson"]
    evaluator = _llm().with_structured_output(LessonEvaluation)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Evaluate the lesson using the six fixed pass/fail checks. Be strict and evidence-based.
accuracy: compare factual statements with the trusted reference facts; RAG is Retrieval-Augmented Generation, retrieval finds relevant source information, and generation uses that context to answer. RAG does not guarantee correctness.
beginner_language: simple English, short sentences, familiar words.
real_example: a practical question-to-answer example.
jargon_explained: important terms are explained simply.
key_coverage: what, why, how, workflow, benefits, limitations and exactly three quiz questions.
teaching_flow: logical progression from introduction through example to summary.
Every check must be PASS or FAIL with a reason and correction. Do not give partial credit. The rubric is fixed and cannot be relaxed.
Trusted reference facts:\n{reference_facts}
The phrase 'RAG stands for Random Answer Generation' is factually wrong and must fail accuracy."""),
        ("human", "Topic: {topic}\nLesson:\n{lesson}")
    ])
    llm_result = (prompt | evaluator).invoke({
        "topic": state["topic"], "lesson": lesson,
        "reference_facts": "\n".join(f"- {fact}" for fact in RAG_REFERENCE_FACTS),
    })
    results = llm_result.as_dict()
    results = apply_deterministic_overrides(results, lesson)
    statuses = [results[k]["status"] for k in RUBRIC_CHECKS]
    results["overall_status"] = "PASS" if all(s == "PASS" for s in statuses) else "FAIL"
    failed = [k for k in RUBRIC_CHECKS if results[k]["status"] == "FAIL"]
    feedback = "\n".join(
        f"- {name}: {results[name].get('reason', '')} Fix: {results[name].get('correction', '')}"
        for name in failed
    )
    rejection_log = list(state.get("rejection_log", []))
    if failed:
        rejection_log.append({
            "attempt": state["attempt_count"], "failed_checks": failed,
            "evaluation": results, "feedback": feedback,
        })
    save_attempt(state["run_id"], state["attempt_count"], lesson, results, failed, feedback)
    return {
        "evaluation_results": results, "failed_checks": failed, "feedback": feedback,
        "rejection_log": rejection_log,
        "final_status": "APPROVED" if not failed else "IN_PROGRESS",
    }


def mark_approved(state: LessonState) -> dict:
    return {"final_status": "APPROVED"}


def mark_rejected(state: LessonState) -> dict:
    return {"final_status": "REJECTED"}
