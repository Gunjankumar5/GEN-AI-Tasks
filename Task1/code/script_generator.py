"""
script_generator.py — Generate a short video narration script using Google Gemini.
"""

import os
from google import genai
from google.genai import types

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

SYSTEM_PROMPT = """You are a professional short-video scriptwriter. 
Your scripts are engaging, clear, and designed for 30-60 second videos.
Always write in a conversational tone suitable for text-to-speech narration.
Structure: Hook → Key facts (2-3 points) → Strong closing line.
Keep the total word count between 80–120 words."""


def generate_script(title: str, summary: str) -> str:
    """
    Generate a 30-60 second video script based on the article title and summary.

    Args:
        title: Article headline / topic.
        summary: Brief description or body text of the article.

    Returns:
        A narration script as a plain string.
    """
    if not _client:
        print("  [Warning] GOOGLE_API_KEY not set. Using fallback script.")
        return _fallback_script(title)

    user_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Create a 30-60 second video script for the following news topic.\n\n"
        f"Title: {title}\n"
        f"Summary: {summary}\n\n"
        f"Script:"
    )

    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
            ),
        )
        return response.text.strip()

    except Exception as e:
        print(f"  [Error] Gemini API call failed: {e}")
        return _fallback_script(title)


def _fallback_script(title: str) -> str:
    """Return a generic script when the API is unavailable."""
    return (
        f"Did you know? {title}. "
        "This is one of the most talked-about stories right now. "
        "Experts say this development could change the way we live and work. "
        "The implications are massive — and they're happening faster than anyone expected. "
        "Stay informed, stay ahead. Follow us for daily updates on the stories that matter most."
    )
