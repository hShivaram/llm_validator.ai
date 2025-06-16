import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validator


def test_estimate_token_count():
    text = "one two three four"
    assert validator.estimate_token_count(text) == int(4 * 1.3)


def test_load_code_sources_file(tmp_path):
    f = tmp_path / "file.py"
    f.write_text("print('hi')")
    result = validator.load_code_sources(file=str(f))
    assert result == ["print('hi')"]


def test_load_code_sources_dir(tmp_path):
    d = tmp_path / "src"
    d.mkdir()
    (d / "a.py").write_text("a")
    (d / "b.py").write_text("b")
    sources = validator.load_code_sources(directory=str(d))
    assert sorted(sources) == ["a", "b"]


def test_extract_app_name(tmp_path):
    app_dir = tmp_path / "myapp"
    app_dir.mkdir()
    f = app_dir / "main.py"
    f.write_text("pass")
    assert validator.extract_app_name(str(f)) == "myapp"
    assert validator.extract_app_name(str(app_dir)) == "myapp"


def test_validate_creates_report(tmp_path, monkeypatch):
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "qa_unified_prompt.txt"
    prompt_file.write_text("Prompt template")
    results_dir = tmp_path / "results"
    code_file = tmp_path / "app.py"
    code_file.write_text("print('x')")

    monkeypatch.setattr(validator, "PROMPTS_DIR", prompts_dir)
    monkeypatch.setattr(validator, "VALIDATION_PROMPT_FILE", prompt_file)
    monkeypatch.setattr(validator, "RESULTS_DIR", results_dir)

    monkeypatch.setattr(validator, "run_ollama", lambda prompt, model: "output")

    args = argparse.Namespace(file=str(code_file), dir=None, manifest=False, model="demo")
    validator.validate(args)

    files = list(results_dir.iterdir())
    assert len(files) == 1
    assert files[0].name.startswith("validation_report_demo_")
    assert files[0].read_text() == "output"
