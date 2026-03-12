"""
analyzer.py — Analyze a high-level business requirement using OpenAI GPT.

Extracts:
  - Core entities (nouns / data models)
  - Key features (functional requirements)
  - Non-functional requirements (performance, security, scalability)
"""

import os
import json
from google import genai
from google.genai import types

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

SYSTEM_PROMPT = """You are a senior software architect. 
Analyze the given business requirement and extract structured information.
Return ONLY valid JSON with this exact structure:
{
  "entities": ["list of core data entities, e.g. User, Order, Product"],
  "features": ["list of key functional features"],
  "non_functional": ["list of non-functional requirements like scalability, security"]
}
Be concise — 4-6 items per list maximum."""


def analyze_requirements(requirement: str) -> dict:
    """
    Parse a business requirement into entities, features, and NFRs.

    Args:
        requirement: Raw business requirement text.

    Returns:
        Dict with keys: entities, features, non_functional
    """
    if _client:
        result = _analyze_with_ai(requirement)
        if result:
            return result

    print("  [Warning] AI analysis unavailable. Using rule-based fallback.")
    return _rule_based_analysis(requirement)


def _analyze_with_ai(requirement: str) -> dict | None:
    """Use Gemini to extract structured analysis."""
    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nRequirement:\n{requirement}",
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)

    except (Exception, json.JSONDecodeError) as e:
        print(f"  [Error] AI analysis failed: {e}")
        return None


def _rule_based_analysis(requirement: str) -> dict:
    """
    Basic NLP-free extraction using keyword matching.
    Works offline without any API key.
    """
    text_lower = requirement.lower()

    # Common entity keywords
    entity_map = {
        "user": "User",
        "customer": "Customer",
        "order": "Order",
        "product": "Product",
        "payment": "Payment",
        "restaurant": "Restaurant",
        "delivery": "Delivery",
        "agent": "DeliveryAgent",
        "menu": "Menu",
        "cart": "Cart",
        "review": "Review",
        "notification": "Notification",
    }
    entities = list({v for k, v in entity_map.items() if k in text_lower})[:6]

    # Feature keywords
    feature_map = {
        "browse": "Browse and search listings",
        "order": "Place and manage orders",
        "payment": "Online payment processing",
        "track": "Real-time order/delivery tracking",
        "manage": "Admin management dashboard",
        "login": "User authentication & authorization",
        "register": "User registration",
        "notification": "Push/email notifications",
    }
    features = list({v for k, v in feature_map.items() if k in text_lower})[:6]

    return {
        "entities": entities or ["User", "Order", "Product"],
        "features": features or ["User Authentication", "Order Management", "Admin Dashboard"],
        "non_functional": [
            "Scalability (horizontal scaling)",
            "High availability (99.9% uptime)",
            "Data security (encryption at rest and in transit)",
            "Low latency API responses (<200ms)",
        ],
    }
