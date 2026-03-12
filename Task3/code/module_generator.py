"""
module_generator.py — Convert analysis results into a structured list of system modules.

Each module represents an independently deployable service or component.
"""

import os
import json
from google import genai
from google.genai import types

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

SYSTEM_PROMPT = """You are a senior software architect designing microservices.
Given the analysis of a business requirement, generate system modules.
Return ONLY valid JSON — a list of module objects:
[
  {
    "name": "Module Name",
    "description": "One-line description of what this module does",
    "responsibilities": ["Responsibility 1", "Responsibility 2", "Responsibility 3"]
  }
]
Generate 4-6 modules. Keep descriptions concise and practical."""


def generate_modules(analysis: dict) -> list[dict]:
    """
    Generate system modules from requirement analysis.

    Args:
        analysis: Dict with entities, features, non_functional keys.

    Returns:
        List of module dicts.
    """
    if _client:
        modules = _generate_with_ai(analysis)
        if modules:
            return modules

    return _fallback_modules(analysis)


def _generate_with_ai(analysis: dict) -> list[dict]:
    """Use Gemini to generate modules."""
    user_prompt = (
        f"Based on this requirement analysis, design the system modules:\n"
        f"Entities: {', '.join(analysis.get('entities', []))}\n"
        f"Features: {', '.join(analysis.get('features', []))}\n"
        f"Non-functional: {', '.join(analysis.get('non_functional', []))}"
    )
    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
        return data if isinstance(data, list) else data.get("modules", [])
    except (Exception, json.JSONDecodeError) as e:
        print(f"  [Error] Module generation failed: {e}")
        return []


def _fallback_modules(analysis: dict) -> list[dict]:
    """Generate sensible default modules based on common entities."""
    entities = [e.lower() for e in analysis.get("entities", [])]

    base_modules = [
        {
            "name": "Auth Service",
            "description": "Handles user authentication, registration, and JWT token management.",
            "responsibilities": [
                "User registration and login",
                "Password hashing and validation",
                "JWT token issuance and refresh",
                "Role-based access control (RBAC)",
            ],
        },
        {
            "name": "User Service",
            "description": "Manages user profiles and preferences.",
            "responsibilities": [
                "CRUD operations for user profiles",
                "Address book management",
                "Account settings and preferences",
            ],
        },
        {
            "name": "Product/Catalog Service",
            "description": "Manages product/item listings and categories.",
            "responsibilities": [
                "CRUD for products and categories",
                "Search and filter functionality",
                "Image and media management",
            ],
        },
        {
            "name": "Order Service",
            "description": "Handles order lifecycle from placement to completion.",
            "responsibilities": [
                "Order creation and validation",
                "Order status tracking and updates",
                "Order history and reporting",
            ],
        },
        {
            "name": "Payment Service",
            "description": "Processes payments and manages transaction records.",
            "responsibilities": [
                "Payment gateway integration (Stripe / Razorpay)",
                "Transaction recording and receipts",
                "Refund and dispute management",
            ],
        },
        {
            "name": "Notification Service",
            "description": "Sends real-time alerts via email, SMS, and push notifications.",
            "responsibilities": [
                "Email notification dispatch",
                "SMS alerts via Twilio / SNS",
                "In-app push notifications",
            ],
        },
    ]

    # Filter/add based on detected entities
    if "delivery" in entities or "agent" in entities:
        base_modules.append(
            {
                "name": "Delivery Service",
                "description": "Assigns and tracks delivery agents for orders.",
                "responsibilities": [
                    "Agent assignment algorithm",
                    "Real-time GPS tracking",
                    "Delivery status updates",
                ],
            }
        )

    return base_modules[:6]
