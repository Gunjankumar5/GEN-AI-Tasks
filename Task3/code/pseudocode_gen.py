import os
import json
from google import genai
from google.genai import types

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

SYSTEM_PROMPT = """You are a software architect writing pseudocode for system modules.
For each module, write clear, language-agnostic pseudocode for its most critical function.
Return ONLY valid JSON — a list of pseudocode blocks:
[
  {
    "module": "Module Name",
    "function": "functionName(params)",
    "code": "FUNCTION functionName(params)\\n  // pseudocode here\\nEND FUNCTION"
  }
]
Keep pseudocode readable, with 5-12 lines per function. Use indentation for clarity."""


def generate_pseudocode(modules: list[dict]) -> list[dict]:
    if _client:
        result = _generate_with_ai(modules)
        if result:
            return result

    return _fallback_pseudocode(modules)


def _generate_with_ai(modules: list[dict]) -> list[dict]:
    module_summary = "\n".join(
        [f"- {m['name']}: {m['description']}" for m in modules]
    )
    user_prompt = (
        f"Generate pseudocode for the core function of each module:\n{module_summary}"
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
        return data if isinstance(data, list) else data.get("pseudocode", [])
    except (Exception, json.JSONDecodeError) as e:
        print(f"  [Error] Pseudocode generation failed: {e}")
        return []


def _fallback_pseudocode(modules: list[dict]) -> list[dict]:
    """Return template pseudocode blocks based on common module names."""
    templates = {
        "auth": {
            "function": "loginUser(email, password)",
            "code": (
                "FUNCTION loginUser(email, password)\n"
                "  user = database.findUserByEmail(email)\n"
                "  IF user is NULL THEN\n"
                "    RETURN error('User not found')\n"
                "  END IF\n"
                "  IF NOT verifyPasswordHash(password, user.password_hash) THEN\n"
                "    RETURN error('Invalid credentials')\n"
                "  END IF\n"
                "  token = generateJWT(user.id, user.role, expiresIn='24h')\n"
                "  RETURN { token, user }\n"
                "END FUNCTION"
            ),
        },
        "order": {
            "function": "placeOrder(userId, cartItems, deliveryAddress)",
            "code": (
                "FUNCTION placeOrder(userId, cartItems, deliveryAddress)\n"
                "  VALIDATE cartItems is not empty\n"
                "  FOR EACH item IN cartItems DO\n"
                "    product = ProductService.getById(item.productId)\n"
                "    IF product.stock_qty < item.quantity THEN\n"
                "      RETURN error('Insufficient stock for ' + product.name)\n"
                "    END IF\n"
                "  END FOR\n"
                "  total = calculateTotal(cartItems)\n"
                "  order = database.createOrder(userId, cartItems, total, deliveryAddress)\n"
                "  ProductService.decrementStock(cartItems)\n"
                "  NotificationService.notify(userId, 'Order placed successfully')\n"
                "  RETURN order\n"
                "END FUNCTION"
            ),
        },
        "payment": {
            "function": "processPayment(orderId, method, amount)",
            "code": (
                "FUNCTION processPayment(orderId, method, amount)\n"
                "  order = OrderService.getById(orderId)\n"
                "  IF order.payment_status == 'paid' THEN\n"
                "    RETURN error('Order already paid')\n"
                "  END IF\n"
                "  gatewayResponse = PaymentGateway.charge(method, amount)\n"
                "  IF gatewayResponse.success THEN\n"
                "    database.createPayment(orderId, amount, method, gatewayResponse.txnId)\n"
                "    OrderService.updatePaymentStatus(orderId, 'paid')\n"
                "    NotificationService.sendReceipt(order.userId, amount)\n"
                "    RETURN { success: true, txnId: gatewayResponse.txnId }\n"
                "  ELSE\n"
                "    RETURN error('Payment failed: ' + gatewayResponse.error)\n"
                "  END IF\n"
                "END FUNCTION"
            ),
        },
    }

    result = []
    for module in modules:
        name = module["name"].lower()
        matched_key = next((k for k in templates if k in name), None)

        if matched_key:
            t = templates[matched_key]
            result.append({
                "module": module["name"],
                "function": t["function"],
                "code": t["code"],
            })
        else:
            result.append({
                "module": module["name"],
                "function": f"handleRequest(requestData)",
                "code": (
                    f"FUNCTION handleRequest(requestData)\n"
                    f"  VALIDATE requestData against schema\n"
                    f"  IF validation fails THEN\n"
                    f"    RETURN error('Validation failed', errors)\n"
                    f"  END IF\n"
                    f"  result = database.processRequest(requestData)\n"
                    f"  log('{module['name']} processed request', requestData.id)\n"
                    f"  RETURN result\n"
                    f"END FUNCTION"
                ),
            })

    return result
