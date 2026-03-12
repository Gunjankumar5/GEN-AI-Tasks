import os
import re
from google import genai
from google.genai import types

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

SYSTEM_PROMPT = """You are an expert SEO specialist. 
Given a product name and category, return exactly 4 high-volume SEO keywords.
Rules:
- Focus on buyer-intent keywords (e.g., "best", "buy", "review", "2025")
- Mix short-tail (1-2 words) and long-tail (3-5 words) keywords
- Return ONLY a Python-style comma-separated list, no explanations
Example output: best wireless earbuds 2025, AirPods Pro review, noise cancelling earbuds buy, premium earbuds under $200"""


def get_seo_keywords(product_name: str, category: str = "") -> list[str]:
    if _client:
        keywords = _get_ai_keywords(product_name, category)
        if keywords:
            return keywords

    print("  [Warning] AI keyword research unavailable. Using rule-based fallback.")
    return _rule_based_keywords(product_name, category)


def _get_ai_keywords(product_name: str, category: str) -> list[str]:
    try:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Product: {product_name}\n"
            f"Category: {category or 'General'}\n"
            f"Generate 4 SEO keywords:"
        )
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
            ),
        )
        raw = response.text.strip()
        keywords = [kw.strip().strip('"').strip("'") for kw in raw.split(",")]
        return keywords[:4]

    except Exception as e:
        print(f"  [Error] Gemini keyword research failed: {e}")
        return []


def _rule_based_keywords(product_name: str, category: str) -> list[str]:
    words = re.sub(r"[^a-zA-Z0-9 ]", "", product_name).split()
    brand = words[0] if words else "product"
    short_name = " ".join(words[:3]).lower()

    keywords = [
        f"best {short_name}",
        f"{short_name} review 2025",
        f"buy {short_name} online",
        f"{brand.lower()} {(category or 'product').lower()}",
    ]
    return keywords[:4]
