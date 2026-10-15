# LessonForge AI architecture

## Request lifecycle
1. `app.py` loads `.env`, initializes SQLite, selects the latest prompt strategy and creates a run record.
2. LangGraph invokes `generate_lesson`, which calls Groq and supplies fixed reference facts, historical memory guidance, and the current prompt strategy.
3. `evaluate_lesson` asks Groq for a Pydantic-structured six-check rubric evaluation.
4. `quality.py` applies deterministic overrides: required headings, exactly three quiz questions, and known false claims.
5. The graph approves if all six checks pass; otherwise it feeds evaluator feedback into another generation. Three total attempts maximum.
6. Each attempt is saved to SQLite. The final lesson is written only when approved; the JSON log includes all rejected attempts.
7. After the run, repeated failure categories across distinct runs may create a new prompt version for a future run. The rubric and reference facts are not automatically changed.

## Persistent memory and controlled improvement
SQLite stores run metadata, every attempt, evaluation JSON, failed check names, feedback, and prompt versions. A failure category must recur across at least two distinct runs before the strategy is strengthened. Improvement guidance is rule-based and versioned, so behavior is inspectable. It does not claim autonomous model training.

## Grounding
The evaluator and generator receive a small reviewed RAG reference-fact set in `lessonforge/reference_facts.py`. Deterministic checks reject several known false claims. This improves traceability but is not equivalent to retrieving from a large external corpus or verifying every sentence.

## Retry policy
Two retries means three total generations. If attempt 3 still fails, the run is marked `REJECTED`, and no approved lesson is published.
