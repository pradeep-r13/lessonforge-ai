# Final submission checklist

- [ ] Run `python app.py` and inspect `outputs/final_lesson.md`.
- [ ] Run `python app.py --demo-error`; inspect `outputs/rejection_log.json` to confirm attempt 1 failed accuracy and its correction was recorded before attempt 2.
- [ ] Run `python app.py --show-memory` before and after another run to demonstrate persistence.
- [ ] Run `pytest -q`; record the exact result in the README or Loom.
- [ ] Run a controlled repeated-failure test across two distinct runs and confirm a new prompt version is stored and used on the next run.
- [ ] Review the generated lesson against `docs/reference_facts.md`.
- [ ] Push the project to GitHub, excluding `.env`, `.venv`, and local database/output files.
- [ ] Copy `submission/final_lesson.md` into Google Docs or Notion and create a shareable link.
- [ ] Record a 15–20 minute Loom walkthrough with face visible, normal run, deliberate-error retry, memory/logs, architecture, and trade-offs.
