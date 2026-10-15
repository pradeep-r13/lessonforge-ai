import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("memory/lessonforge.db")
BASE_STRATEGY = (
    "Use simple English, define technical terms, include a concrete question-answer example, "
    "follow the required headings, and explain benefits and limitations."
)
FAILURE_GUIDANCE = {
    "accuracy": "Check every factual statement against the trusted reference facts; avoid unsupported absolute claims.",
    "beginner_language": "Prefer short sentences and familiar words; explain each new idea before using it.",
    "real_example": "Include one concrete learner question, retrieved information, and the resulting answer.",
    "jargon_explained": "Define RAG, retrieval, chunk, embedding, and language model in everyday language when used.",
    "key_coverage": "Use every required heading and include exactly three quiz questions.",
    "teaching_flow": "Teach in this order: definition, need, steps, example, terms, limitations, summary, quiz.",
}


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY, topic TEXT NOT NULL, created_at TEXT NOT NULL,
            attempt_count INTEGER DEFAULT 0, final_status TEXT DEFAULT 'IN_PROGRESS',
            prompt_version TEXT DEFAULT 'v1'
        );
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, attempt_no INTEGER NOT NULL,
            lesson TEXT NOT NULL, evaluation_json TEXT NOT NULL, failed_checks_json TEXT NOT NULL,
            feedback TEXT NOT NULL, created_at TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES runs(run_id)
        );
        CREATE TABLE IF NOT EXISTS prompt_versions (
            version TEXT PRIMARY KEY, topic TEXT NOT NULL, strategy TEXT NOT NULL,
            source_failures_json TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL
        );
        """)
        # Backward-compatible migration for an earlier database schema.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(prompt_versions)")}
        if "topic" not in columns:
            conn.execute("ALTER TABLE prompt_versions ADD COLUMN topic TEXT NOT NULL DEFAULT '*'")
        if "source_failures_json" not in columns:
            conn.execute("ALTER TABLE prompt_versions ADD COLUMN source_failures_json TEXT NOT NULL DEFAULT '[]'")
        conn.execute("""INSERT OR IGNORE INTO prompt_versions
            (version, topic, strategy, source_failures_json, created_at) VALUES (?, ?, ?, ?, ?)""",
            ("v1", "*", BASE_STRATEGY, "[]", datetime.now(timezone.utc).isoformat()))


def create_run(topic: str) -> str:
    run_id = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute("INSERT INTO runs(run_id, topic, created_at) VALUES (?, ?, ?)",
                     (run_id, topic, datetime.now(timezone.utc).isoformat()))
    return run_id


def save_attempt(run_id: str, attempt_no: int, lesson: str, evaluation: dict, failed_checks: list, feedback: str):
    with _connect() as conn:
        conn.execute("""INSERT INTO attempts(run_id, attempt_no, lesson, evaluation_json,
                     failed_checks_json, feedback, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     (run_id, attempt_no, lesson, json.dumps(evaluation), json.dumps(failed_checks),
                      feedback, datetime.now(timezone.utc).isoformat()))
        conn.execute("UPDATE runs SET attempt_count=? WHERE run_id=?", (attempt_no, run_id))


def finish_run(run_id: str, status: str, attempts: int, prompt_version: str):
    with _connect() as conn:
        conn.execute("UPDATE runs SET final_status=?, attempt_count=?, prompt_version=? WHERE run_id=?",
                     (status, attempts, prompt_version, run_id))


def get_prompt_strategy(topic: str) -> tuple[str, str]:
    """Return the latest topic-specific strategy, falling back to the global base strategy."""
    with _connect() as conn:
        row = conn.execute("SELECT version, strategy FROM prompt_versions WHERE lower(topic)=lower(?) ORDER BY rowid DESC LIMIT 1",
                           (topic,)).fetchone()
        if row:
            return row["version"], row["strategy"]
        row = conn.execute("SELECT version, strategy FROM prompt_versions WHERE topic='*' ORDER BY rowid DESC LIMIT 1").fetchone()
        return (row["version"], row["strategy"]) if row else ("v1", BASE_STRATEGY)


def get_memory_feedback(topic: str) -> str:
    """Summarize failures repeated across distinct past runs (not merely retries in one run)."""
    with _connect() as conn:
        rows = conn.execute("""SELECT r.run_id, a.failed_checks_json FROM attempts a
            JOIN runs r ON r.run_id=a.run_id WHERE lower(r.topic)=lower(?) ORDER BY a.id DESC LIMIT 100""",
            (topic,)).fetchall()
    by_check = {}
    for row in rows:
        for check in json.loads(row["failed_checks_json"]):
            by_check.setdefault(check, set()).add(row["run_id"])
    repeated = sorted(name for name, run_ids in by_check.items() if len(run_ids) >= 2)
    if not repeated:
        return ""
    guidance = [FAILURE_GUIDANCE.get(name, f"Pay extra attention to the {name} check.") for name in repeated]
    return "Recurring failures in earlier runs: " + "; ".join(guidance)


def learn_from_history(topic: str) -> tuple[str, str, list[str]]:
    """Create a versioned, conservative prompt strategy when a failure repeats across runs.

    The rubric is never changed. Only generation guidance is refined.
    """
    feedback = get_memory_feedback(topic)
    current_version, current_strategy = get_prompt_strategy(topic)
    if not feedback:
        return current_version, current_strategy, []
    failures = [name for name, guidance in FAILURE_GUIDANCE.items() if guidance in feedback]
    if not failures:
        return current_version, current_strategy, []
    improved = BASE_STRATEGY + " Additional safeguards from repeated failures: " + " ".join(FAILURE_GUIDANCE[x] for x in failures)
    if improved == current_strategy:
        return current_version, current_strategy, failures
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) AS n FROM prompt_versions").fetchone()["n"]
        version = f"v{count + 1}"
        conn.execute("INSERT INTO prompt_versions(version, topic, strategy, source_failures_json, created_at) VALUES (?, ?, ?, ?, ?)",
                     (version, topic, improved, json.dumps(failures), datetime.now(timezone.utc).isoformat()))
    return version, improved, failures


def database_summary() -> dict:
    """Small read-only summary useful for verification and demos."""
    with _connect() as conn:
        return {
            "runs": conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0],
            "attempts": conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0],
            "prompt_versions": conn.execute("SELECT COUNT(*) FROM prompt_versions").fetchone()[0],
        }
