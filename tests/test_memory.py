import json
import lessonforge.memory as memory


def test_database_persists_runs_attempts_and_prompt_versions(tmp_path, monkeypatch):
    monkeypatch.setattr(memory, "DB_PATH", tmp_path / "lessonforge.db")
    memory.init_db()
    run_id = memory.create_run("Introduction to RAG")
    memory.save_attempt(run_id, 1, "draft", {"overall_status": "FAIL"}, ["jargon_explained"], "Define terms")
    memory.finish_run(run_id, "REJECTED", 1, "v1")
    assert memory.database_summary() == {"runs": 1, "attempts": 1, "prompt_versions": 1}
    version, strategy = memory.get_prompt_strategy("Introduction to RAG")
    assert version == "v1"
    assert "technical terms" in strategy


def test_repeated_failures_across_runs_create_versioned_strategy(tmp_path, monkeypatch):
    monkeypatch.setattr(memory, "DB_PATH", tmp_path / "lessonforge.db")
    memory.init_db()
    for i in range(2):
        run_id = memory.create_run("Introduction to RAG")
        memory.save_attempt(run_id, 1, "draft", {}, ["jargon_explained"], "Define terms simply")
        memory.finish_run(run_id, "REJECTED", 1, "v1")
    version, strategy, failures = memory.learn_from_history("Introduction to RAG")
    assert version != "v1"
    assert "jargon_explained" in failures
    assert "Define RAG" in strategy
    loaded_version, loaded_strategy = memory.get_prompt_strategy("Introduction to RAG")
    assert loaded_version == version
    assert loaded_strategy == strategy
