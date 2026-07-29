import openai
import json
import os

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_article(topic: str):
    prompt = f"""
    You are writing a detailed UK-focused tool review article for ToolBench UK.

    Topic: {topic}

    Produce the following JSON structure:

    {{
        "title": "...",
        "summary": "...",
        "content": "<h2>...</h2><p>...</p>",
        "faq": [
            {{"question": "...", "answer": "..."}},
            {{"question": "...", "answer": "..."}}
        ],
        "schema": {{
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "...",
            "description": "...",
            "author": "ToolBench UK",
            "mainEntityOfPage": "https://toolbench.uk/article/slug"
        }}
    }}

    Rules:
    - Use UK spelling.
    - Use HTML headings (h2, h3) and paragraphs.
    - Insert [AFFILIATE_LINK] placeholders where appropriate.
    - Make content long, detailed, and structured.
    - Include comparisons, pros/cons, and buying advice.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response["choices"][0]["message"]["content"].strip()

    if not raw:
        raise ValueError("AI returned empty response")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("RAW AI OUTPUT:")
        print(raw)
        raise
