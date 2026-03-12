"""
api_generator.py — Generate a REST API specification based on system modules.

Output: dict with base_url and list of endpoint definitions.
"""

import os
import json
from google import genai
from google.genai import types

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

SYSTEM_PROMPT = """You are a REST API designer. 
Given a list of system modules, design the REST API endpoints.
Return ONLY valid JSON:
{
  "base_url": "/api/v1",
  "endpoints": [
    {
      "method": "GET|POST|PUT|DELETE|PATCH",
      "path": "/resource/{id}",
      "description": "What this endpoint does",
      "auth": "Yes|No",
      "request_body": "JSON schema summary or null",
      "response": "200 OK with {field descriptions} or error codes"
    }
  ]
}
Generate 2-3 endpoints per module. Cover the most important CRUD operations."""


def generate_api_spec(modules: list[dict]) -> dict:
    """
    Generate REST API endpoints for all modules.

    Args:
        modules: List of module dicts.

    Returns:
        Dict with base_url and endpoints list.
    """
    if _client:
        spec = _generate_with_ai(modules)
        if spec:
            return spec

    return _fallback_api_spec(modules)


def _generate_with_ai(modules: list[dict]) -> dict:
    """Use Gemini to design the API."""
    module_summary = "\n".join([f"- {m['name']}: {m['description']}" for m in modules])
    user_prompt = f"Design REST API endpoints for these modules:\n{module_summary}"

    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except (Exception, json.JSONDecodeError) as e:
        print(f"  [Error] API spec generation failed: {e}")
        return {}


def _fallback_api_spec(modules: list[dict]) -> dict:
    """Return hardcoded REST API endpoints for common modules."""
    endpoints = [
        # Auth
        {
            "method": "POST",
            "path": "/auth/register",
            "description": "Register a new user account",
            "auth": "No",
            "request_body": "{ name, email, password, role }",
            "response": "201 Created — { userId, token }",
        },
        {
            "method": "POST",
            "path": "/auth/login",
            "description": "Authenticate user and return JWT token",
            "auth": "No",
            "request_body": "{ email, password }",
            "response": "200 OK — { token, user } | 401 Unauthorized",
        },
        {
            "method": "POST",
            "path": "/auth/logout",
            "description": "Invalidate the current session token",
            "auth": "Yes",
            "request_body": None,
            "response": "200 OK — { message: 'Logged out' }",
        },
        # Users
        {
            "method": "GET",
            "path": "/users/me",
            "description": "Get the authenticated user's profile",
            "auth": "Yes",
            "request_body": None,
            "response": "200 OK — User object",
        },
        {
            "method": "PUT",
            "path": "/users/me",
            "description": "Update the authenticated user's profile",
            "auth": "Yes",
            "request_body": "{ name?, phone?, address? }",
            "response": "200 OK — Updated user object",
        },
        # Products
        {
            "method": "GET",
            "path": "/products",
            "description": "List all products with optional filters and pagination",
            "auth": "No",
            "request_body": None,
            "response": "200 OK — { products: [...], total, page, limit }",
        },
        {
            "method": "GET",
            "path": "/products/{id}",
            "description": "Get a single product by ID",
            "auth": "No",
            "request_body": None,
            "response": "200 OK — Product object | 404 Not Found",
        },
        {
            "method": "POST",
            "path": "/products",
            "description": "Create a new product (admin only)",
            "auth": "Yes (Admin)",
            "request_body": "{ name, description, price, category_id, stock_qty }",
            "response": "201 Created — Product object",
        },
        # Orders
        {
            "method": "POST",
            "path": "/orders",
            "description": "Place a new order",
            "auth": "Yes",
            "request_body": "{ items: [{productId, quantity}], deliveryAddress }",
            "response": "201 Created — Order object with id and status",
        },
        {
            "method": "GET",
            "path": "/orders/{id}",
            "description": "Get order details and current status",
            "auth": "Yes",
            "request_body": None,
            "response": "200 OK — Order object | 403 Forbidden | 404 Not Found",
        },
        {
            "method": "PATCH",
            "path": "/orders/{id}/status",
            "description": "Update order status (admin/agent only)",
            "auth": "Yes (Admin/Agent)",
            "request_body": "{ status }",
            "response": "200 OK — Updated order | 400 Invalid status transition",
        },
        # Payments
        {
            "method": "POST",
            "path": "/payments",
            "description": "Initiate payment for an order",
            "auth": "Yes",
            "request_body": "{ orderId, method, amount }",
            "response": "200 OK — { txnId, status } | 402 Payment Required",
        },
        {
            "method": "GET",
            "path": "/payments/{orderId}",
            "description": "Get payment details for an order",
            "auth": "Yes",
            "request_body": None,
            "response": "200 OK — Payment object",
        },
    ]

    # Trim to 2-3 endpoints per detected module
    module_names = [m["name"].lower() for m in modules]
    filtered = []
    for ep in endpoints:
        path_key = ep["path"].split("/")[1]  # e.g. "auth", "users", "orders"
        if any(path_key in m for m in module_names) or path_key in ["auth", "users"]:
            filtered.append(ep)

    return {
        "base_url": "/api/v1",
        "endpoints": filtered or endpoints[:8],
    }
