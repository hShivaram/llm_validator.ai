# app.py
from transformers import pipeline

# Load a sentiment analysis pipeline using DistilBERT
sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    """
    Analyze sentiment of given text using an LLM pipeline.
    Returns: {'label': 'POSITIVE'/'NEGATIVE', 'score': float}
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input must be a non-empty string.")
    return sentiment_pipeline(text)[0]

def create_prompt(name, task):
    """
    Dynamically creates a prompt for the LLM to execute the desired task.
    """
    return f"You are an expert assistant. Help the user '{name}' to perform the task: {task}"

def generate_response(prompt):
    """
    Simulates sending the prompt to an LLM for response generation.
    (Placeholder for a real API call like OpenAI, Ollama, etc.)
    """
    return f"[LLM RESPONSE for prompt]: {prompt}"
