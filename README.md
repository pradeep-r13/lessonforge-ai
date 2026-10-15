# LessonForge AI
**Self-Evaluating Agentic Content Generation System** using Python, LangGraph, Groq, Pydantic, and SQLite.

## What it does
1. Generates a beginner-friendly lesson for a topic.
2. Evaluates it against six hard PASS/FAIL criteria: accuracy, beginner language, real example, jargon explained, key coverage, and teaching flow.
3. Combines a structured LLM evaluator with deterministic checks for required headings, exactly three quiz questions, and known false claims.
4. Sends failed-check feedback into the next generation, with a maximum of two retries (three total attempts).
5. Saves each attempt, failed checks, run status, and prompt version to SQLite; writes the final lesson only when approved.
6. Learns conservative prompt guidance from failure categories repeated across distinct runs. The rubric and trusted reference facts remain fixed.

## Requirements
- Python 3.11 (tested target: 3.11.9)
- Groq API key and access to the model configured in `.env`

## Windows PowerShell setup
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env`:
```dotenv
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```
Never commit `.env` or share your API key. Confirm the model ID is currently available to your Groq account.

## Run
```powershell
python app.py
python app.py --topic "Introduction to RAG"
python app.py --demo-error
python app.py --show-memory
```
`--demo-error` appends a deliberately incorrect RAG definition to attempt 1. The deterministic validator must reject that attempt; the graph then retries with feedback. The final run should only be described as a successful retry if `outputs/rejection_log.json` shows the failed first attempt and correction feedback.

## Outputs
- `outputs/final_lesson.md`: created only when the run is approved.
- `outputs/rejection_log.json`: per-run status, attempts, failed checks, evaluation details, prompt version and learning summary.
- `memory/lessonforge.db`: persistent runs, attempts, and prompt versions.

## Tests
```powershell
pytest -q
```
Tests cover retry routing, deterministic quality checks, persistence, and versioned prompt improvements. They do not call Groq and can run without an API key after dependencies are installed.

## Architecture
```text
START -> Generate -> Evaluate (LLM rubric + deterministic grounding/structure checks)
                         | PASS -> Approve -> save lesson/log -> END
                         | FAIL and attempt < 3 -> feedback -> Generate
                         | FAIL and attempt = 3 -> Reject -> save log -> END

Across runs: SQLite failure history -> repeated-category guidance -> versioned prompt strategy
```

## Design choices and limitations
- LangGraph controls explicit routing and bounded retries.
- Pydantic structures evaluator output.
- Deterministic checks override the LLM for known false claims and required structure.
- SQLite provides persistence across process restarts.
- Repeated failure guidance changes generation strategy, not the fixed rubric.
- Grounding uses a small reviewed reference set for the assignment's RAG topic, not a full document-search RAG pipeline. LLM judgments can still be wrong; review the final lesson before submission.
- Before submission, inspect the rejection JSON, run the test suite, review the final lesson, publish a shareable document, and record the required face-visible 15–20 minute Loom walkthrough.
# lessonforge-ai
