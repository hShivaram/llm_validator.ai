# Example LLM Applications

This folder contains small example projects that you can run through the validator.
Each subfolder represents a separate application with its own prompts and code.

- `sentiment_analysis/` – uses the HuggingFace `transformers` pipeline to analyse
  sentiment.
- `sumarrizer/` – a miniature RAG style summarizer that embeds text with
  `sentence-transformers` and retrieves similar documents.

Run the validator against all apps:

```bash
python validator.py --mode=validate --dir model_to_validate/ --model llama3
```
