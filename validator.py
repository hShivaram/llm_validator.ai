# validator.py
import argparse
import subprocess
from pathlib import Path
import sys

PROMPTS_DIR = Path("prompts")
MODEL_DIR = Path("model_to_validate")
GENERATED_DIR = Path("generated")
RESULTS_DIR = Path("results")
MANIFEST_FILE = Path("manifest.yaml")

VALIDATION_PROMPT_FILE = PROMPTS_DIR / "qa_unified_prompt.txt"


def load_code_sources(file=None, directory=None, manifest=None):
    code_segments = []

    if file:
        code_segments.append(Path(file).read_text())
    elif directory:
        for file in Path(directory).rglob("*.py"):
            code_segments.append(file.read_text())
    elif manifest and manifest.exists():
        import yaml
        config = yaml.safe_load(manifest.read_text())
        for path in config.get("entry_points", []):
            code_segments.append(Path(path).read_text())
    else:
        print("No valid input source provided.")
        sys.exit(1)

    return code_segments


def estimate_token_count(text):
    words = text.split()
    return int(len(words) * 1.3)  # Approximate conversion to tokens


def run_ollama(prompt_text, model):
    token_estimate = estimate_token_count(prompt_text)
    print(f"🧠 Estimated token size: ~{token_estimate} tokens")
    print(f"🚀 Sending prompt to Ollama model '{model}'... This may take a moment...")
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt_text.encode("utf-8"),
        capture_output=True,
        check=True
    )
    print("✅ Ollama responded. Writing results...")
    return result.stdout.decode("utf-8")


def validate(args):
    prompt_template = VALIDATION_PROMPT_FILE.read_text()
    code = load_code_sources(args.file, args.dir, MANIFEST_FILE if args.manifest else None)
    prompt = f"{prompt_template}\n\n# Codebase:\n" + "\n\n".join(code)
    output = run_ollama(prompt, args.model)
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "validation_report.md").write_text(output)
    print("✅ Validation report saved to results/validation_report.md")


def generate():
    report = (RESULTS_DIR / "validation_report.md").read_text()
    # Split the output into sections
    tests = prompts = drift = ""
    if "--- GENERATED_TESTS ---" in report:
        tests = report.split("--- GENERATED_TESTS ---")[1].split("--- REWRITTEN_PROMPTS ---")[0].strip()
    if "--- REWRITTEN_PROMPTS ---" in report:
        prompts = report.split("--- REWRITTEN_PROMPTS ---")[1].split("--- DRIFT_MONITOR ---")[0].strip()
    if "--- DRIFT_MONITOR ---" in report:
        drift = report.split("--- DRIFT_MONITOR ---")[1].strip()

    GENERATED_DIR.mkdir(exist_ok=True)
    (GENERATED_DIR / "missing_tests.py").write_text(tests)
    (GENERATED_DIR / "improved_prompts.json").write_text(prompts)
    (GENERATED_DIR / "drift_monitor.py").write_text(drift)
    print("✅ Generated missing components in /generated folder")


def main():
    parser = argparse.ArgumentParser(description="LLM QA Validator")
    parser.add_argument("--mode", choices=["validate", "generate"], required=True, help="Run mode")
    parser.add_argument("--file", help="Single file to validate")
    parser.add_argument("--dir", help="Directory to validate")
    parser.add_argument("--manifest", action="store_true", help="Use manifest.yaml")
    parser.add_argument("--model", default="llama3", help="Name of the Ollama model to use (default: llama3)")
    args = parser.parse_args()

    if args.mode == "validate":
        validate(args)
    elif args.mode == "generate":
        generate()


if __name__ == "__main__":
    main()
