"""
schema_generator.py — Generate relational database schemas for each identified entity.

Output format: list of table dicts, each with columns (name, type, constraints).
"""

import os
import json
from google import genai
from google.genai import types

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

SYSTEM_PROMPT = """You are a database architect. Generate SQL table schemas.
Return ONLY valid JSON — a list of table objects:
[
  {
    "table": "table_name",
    "columns": [
      {"name": "column_name", "type": "SQL_TYPE", "constraints": "PRIMARY KEY / NOT NULL / etc."}
    ]
  }
]
Include id, created_at, updated_at columns in every table.
Keep schemas practical and normalised (3NF)."""


def generate_schemas(modules: list[dict], entities: list[str]) -> list[dict]:
    """
    Generate DB schemas for the given entities.

    Args:
        modules: List of module dicts.
        entities: List of entity names from requirement analysis.

    Returns:
        List of table schema dicts.
    """
    if _client:
        schemas = _generate_with_ai(entities, modules)
        if schemas:
            return schemas

    return _fallback_schemas(entities)


def _generate_with_ai(entities: list[str], modules: list[dict]) -> list[dict]:
    """Use Gemini to design schemas."""
    module_names = [m["name"] for m in modules]
    user_prompt = (
        f"Design database schemas for these entities: {', '.join(entities)}\n"
        f"System modules for context: {', '.join(module_names)}\n"
        f"Generate one table per entity."
    )
    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
        return data if isinstance(data, list) else data.get("tables", [])
    except (Exception, json.JSONDecodeError) as e:
        print(f"  [Error] Schema generation failed: {e}")
        return []


def _fallback_schemas(entities: list[str]) -> list[dict]:
    """Return hardcoded schemas for common entities."""
    entity_lower = [e.lower() for e in entities]
    schemas = []

    if any(e in entity_lower for e in ["user", "customer"]):
        schemas.append({
            "table": "users",
            "columns": [
                {"name": "id", "type": "UUID", "constraints": "PRIMARY KEY DEFAULT gen_random_uuid()"},
                {"name": "name", "type": "VARCHAR(100)", "constraints": "NOT NULL"},
                {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                {"name": "password_hash", "type": "TEXT", "constraints": "NOT NULL"},
                {"name": "role", "type": "ENUM('customer','admin','agent')", "constraints": "DEFAULT 'customer'"},
                {"name": "phone", "type": "VARCHAR(20)", "constraints": ""},
                {"name": "is_active", "type": "BOOLEAN", "constraints": "DEFAULT TRUE"},
                {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
                {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
            ],
        })

    if any(e in entity_lower for e in ["product", "menu", "item"]):
        schemas.append({
            "table": "products",
            "columns": [
                {"name": "id", "type": "UUID", "constraints": "PRIMARY KEY DEFAULT gen_random_uuid()"},
                {"name": "name", "type": "VARCHAR(200)", "constraints": "NOT NULL"},
                {"name": "description", "type": "TEXT", "constraints": ""},
                {"name": "price", "type": "DECIMAL(10,2)", "constraints": "NOT NULL"},
                {"name": "category_id", "type": "UUID", "constraints": "REFERENCES categories(id)"},
                {"name": "stock_qty", "type": "INTEGER", "constraints": "DEFAULT 0"},
                {"name": "image_url", "type": "TEXT", "constraints": ""},
                {"name": "is_available", "type": "BOOLEAN", "constraints": "DEFAULT TRUE"},
                {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
                {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
            ],
        })

    if any(e in entity_lower for e in ["order"]):
        schemas.append({
            "table": "orders",
            "columns": [
                {"name": "id", "type": "UUID", "constraints": "PRIMARY KEY DEFAULT gen_random_uuid()"},
                {"name": "user_id", "type": "UUID", "constraints": "REFERENCES users(id) NOT NULL"},
                {"name": "status", "type": "ENUM('pending','confirmed','preparing','out_for_delivery','delivered','cancelled')", "constraints": "DEFAULT 'pending'"},
                {"name": "total_amount", "type": "DECIMAL(10,2)", "constraints": "NOT NULL"},
                {"name": "delivery_address", "type": "TEXT", "constraints": "NOT NULL"},
                {"name": "payment_status", "type": "ENUM('unpaid','paid','refunded')", "constraints": "DEFAULT 'unpaid'"},
                {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
                {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
            ],
        })

    if any(e in entity_lower for e in ["payment"]):
        schemas.append({
            "table": "payments",
            "columns": [
                {"name": "id", "type": "UUID", "constraints": "PRIMARY KEY DEFAULT gen_random_uuid()"},
                {"name": "order_id", "type": "UUID", "constraints": "REFERENCES orders(id) NOT NULL"},
                {"name": "amount", "type": "DECIMAL(10,2)", "constraints": "NOT NULL"},
                {"name": "method", "type": "ENUM('card','upi','wallet','cod')", "constraints": "NOT NULL"},
                {"name": "gateway_txn_id", "type": "VARCHAR(100)", "constraints": "UNIQUE"},
                {"name": "status", "type": "ENUM('initiated','success','failed','refunded')", "constraints": "DEFAULT 'initiated'"},
                {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
                {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
            ],
        })

    if not schemas:
        # Generic fallback
        schemas.append({
            "table": "entities",
            "columns": [
                {"name": "id", "type": "UUID", "constraints": "PRIMARY KEY DEFAULT gen_random_uuid()"},
                {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                {"name": "metadata", "type": "JSONB", "constraints": ""},
                {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
                {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT NOW()"},
            ],
        })

    return schemas
