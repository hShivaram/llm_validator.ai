# validator.py
import argparse
import subprocess
from pathlib import Path
import sys
from datetime import datetime

PROMPTS_DIR = Path("prompts")
MODEL_DIR = Path("model_to_validate")
GENERATED_DIR = Path("generated")
RESULTS_DIR = Path("results")
MANIFEST_FILE = Path("manifest.yaml")

VALIDATION_PROMPT_FILE = PROMPTS_DIR / "qa_unified_prompt.txt"


def load_code_sources(file=None, directory=None, manifest=None):
    code_segments = []

    if file:
        file_path = Path(file)
        if file_path.is_file():
            code_segments.append(file_path.read_text())
        else:
            print(f"❌ Provided path for --file is a directory: {file_path}. Please use --dir instead.")
            sys.exit(1)
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"validation_report_{args.model}_{timestamp}.md"
    (RESULTS_DIR / report_filename).write_text(output)
    print(f"✅ Validation report saved to results/{report_filename}")

def extract_app_name(path):
    """Extract the app name from the provided path."""
    # Get the parent directory name if it's a file, otherwise use the directory name
    path = Path(path)
    if path.is_file():
        return path.parent.name
    return path.name


def generate():
    # Locate the latest validation report
    latest_file = max(RESULTS_DIR.glob("validation_report_*.md"), key=lambda f: f.stat().st_mtime, default=None)
    if not latest_file:
        print("❌ No validation report found in results/. Please run in --mode=validate first.")
        sys.exit(1)

    report = latest_file.read_text()
    tests = prompts = drift = ""
    status = {"tests": False, "prompts": False, "drift": False}

    # Parse sections
    if "--- GENERATED_TESTS ---" in report:
        tests = report.split("--- GENERATED_TESTS ---")[1].split("--- REWRITTEN_PROMPTS ---")[0].strip()
        status["tests"] = True
    if "--- REWRITTEN_PROMPTS ---" in report:
        prompts = report.split("--- REWRITTEN_PROMPTS ---")[1].split("--- DRIFT_MONITOR ---")[0].strip()
        status["prompts"] = True
    if "--- DRIFT_MONITOR ---" in report:
        drift = report.split("--- DRIFT_MONITOR ---")[1].strip()
        status["drift"] = True

    # For each app inside MODEL_DIR, generate fixes
    for app_dir in MODEL_DIR.iterdir():
        if not app_dir.is_dir():
            continue
        app_name = app_dir.name
        for file_path in app_dir.rglob("*.py"):
            # Build output folder based on app and file structure
            relative = file_path.relative_to(app_dir)
            module_folder = GENERATED_DIR / app_name / relative.parent / relative.stem
            module_folder.mkdir(parents=True, exist_ok=True)

            # Write generated artifacts per file
            if status["tests"]:
                (module_folder / "missing_tests.py").write_text(tests)
            if status["prompts"]:
                (module_folder / "improved_prompts.json").write_text(prompts)
            if status["drift"]:
                (module_folder / "drift_monitor.py").write_text(drift)

    print(f"✅ Generated missing components under /generated/ for all apps in '{MODEL_DIR.name}'")
    print("Generation Summary per file:")
    print(f"- Tests: {'✅' if status['tests'] and tests else '❌ (missing or empty)'}")
    print(f"- Prompts: {'✅' if status['prompts'] and prompts else '❌ (missing or empty)'}")
    print(f"- Drift Monitor: {'✅' if status['drift'] and drift else '❌ (missing or empty)'}")


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
