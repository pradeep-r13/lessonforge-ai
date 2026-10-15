import argparse
import json
import os
from pathlib import Path
from dotenv import load_dotenv

from lessonforge.graph import build_graph
from lessonforge.memory import (
    init_db, create_run, get_memory_feedback, get_prompt_strategy,
    finish_run, learn_from_history, database_summary,
)

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="LessonForge AI: self-evaluating lesson generator")
    parser.add_argument("--topic", default="Introduction to RAG", help="Lesson topic")
    parser.add_argument("--demo-error", action="store_true", help="Inject a known mistake into attempt 1")
    parser.add_argument("--show-memory", action="store_true", help="Print SQLite persistence summary and exit")
    args = parser.parse_args()

    init_db()
    if args.show_memory:
        print(json.dumps(database_summary(), indent=2))
        return
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit("Missing GROQ_API_KEY. Add your Groq API key to .env.")

    run_id = create_run(args.topic)
    memory_feedback = get_memory_feedback(args.topic)
    prompt_version, prompt_strategy = get_prompt_strategy(args.topic)
    graph = build_graph()
    result = graph.invoke({
        "run_id": run_id, "topic": args.topic, "lesson": "", "attempt_count": 0,
        "evaluation_results": {}, "failed_checks": [], "rejection_log": [],
        "final_status": "IN_PROGRESS", "memory_feedback": memory_feedback,
        "prompt_strategy": prompt_strategy, "demo_error": args.demo_error,
        "prompt_version": prompt_version, "feedback": "",
    })

    finish_run(run_id, result["final_status"], result["attempt_count"], prompt_version)
    # Learn only from repeated failures across distinct runs; this affects a future run.
    new_version, _, learned_failures = learn_from_history(args.topic)
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    if result["final_status"] == "APPROVED":
        (output_dir / "final_lesson.md").write_text(result["lesson"], encoding="utf-8")
        print(f"\n✅ Lesson approved. Saved to {output_dir / 'final_lesson.md'}")
    else:
        (output_dir / "final_lesson.md").unlink(missing_ok=True)
        print("\n❌ Lesson rejected after retry limit. No approved lesson was published.")

    log = {
        "run_id": run_id, "topic": args.topic, "final_status": result["final_status"],
        "attempt_count": result["attempt_count"], "prompt_version_used": prompt_version,
        "rejection_log": result["rejection_log"], "evaluation_results": result["evaluation_results"],
        "prompt_learning": {"next_version": new_version, "repeated_failure_categories": learned_failures},
    }
    (output_dir / "rejection_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Run ID: {run_id} | Status: {result['final_status']} | Attempts: {result['attempt_count']}")
    print(f"Prompt version used: {prompt_version} | Latest version: {new_version}")
    print(f"Logs saved to {output_dir / 'rejection_log.json'}")

if __name__ == "__main__":
    main()
