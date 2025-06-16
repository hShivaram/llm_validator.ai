# 🤖 LLM QA Validator Tool

A plug-and-play QA automation tool designed to validate and improve LLM, RAG, or model-based pipelines.  
It scans code using a local LLM via [Ollama](https://ollama.com) and provides:
- Test coverage audit
- Prompt risk analysis
- Model/prompt drift detection
- Auto-generated tests, hardened prompts, and monitoring logic

---

## 📁 Folder Structure

```
llm_validator/
├── validator.py
├── requirements.txt
├── prompts/
│   └── qa_unified_prompt.txt
├── model_to_validate/
│   ├── app.py
│   └── prompts_used.json
├── results/
│   └── validation_report.md
├── generated/
│   ├── missing_tests.py
│   ├── improved_prompts.json
│   └── drift_monitor.py
├── manifest.yaml  # Optional
```

---

## ⚙️ Setup Instructions

### 1. Create virtual environment & install dependencies

```bash
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Ollama server

```bash
ollama serve &
```

### 3. Pull the base model

```bash
ollama pull llama3
```

---

## 🚦 How to Use

### ✅ Step 1: Validate Code

#### Validate a single file:
```bash
python3 validator.py --mode=validate --file model_to_validate/app.py
```

#### Validate an entire folder:
```bash
python3 validator.py --mode=validate --dir model_to_validate/
```

#### Validate using a manifest file:
```bash
python3 validator.py --mode=validate --manifest
```

🧾 Output:
```
results/validation_report.md
```

---

### 🛠️ Step 2: Generate Missing QA Artifacts

```bash
python3 validator.py --mode=generate
```

🆕 This will generate:
- `generated/missing_tests.py`
- `generated/improved_prompts.json`
- `generated/drift_monitor.py`

---

## 🧠 QA Standards Followed

- Google ML Test Scorecard ✅
- NIST AI Risk Management ✅
- ISO/IEC 42001 AI Governance ✅
- Prompt injection defense & PEP8 compliance
- Design Patterns: Factory, Strategy, Observer

---

## 🛑 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ollama` not found | Install Ollama CLI and add to PATH |
| Ollama commands fail | Run `ollama serve &` before running the validator |
| No model found | Run `ollama pull llama3` |
| Output empty | Ensure prompt file exists and input code is valid |
| Prompt injection warning | Refactor or use generated prompts |

---

## 🧪 Example Run

```bash
python3 validator.py --mode=validate --dir model_to_validate/
python3 validator.py --mode=generate
```

---

## 🧡 Author
Crafted by QA engineers to empower modern AI pipelines with better quality, faster.