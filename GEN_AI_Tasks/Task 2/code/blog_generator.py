import os
from google import genai
from google.genai import types
from typing import Dict, List

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

SYSTEM_PROMPT = """You are an expert SEO content writer specialising in product reviews and buying guides.
Write engaging, informative blog posts that:
- Are exactly 150-200 words
- Naturally incorporate the provided SEO keywords (do not force them)
- Include a catchy H1 title and one H2 subheading (use Markdown)
- Use a friendly, helpful tone aimed at potential buyers
- End with a clear call to action
- Format output as clean Markdown (title, intro, body, CTA)"""


def generate_blog_post(product: Dict, keywords: List[str]) -> str:
    if _client:
        blog = _generate_with_ai(product, keywords)
        if blog:
            return blog

    print("  [Warning] AI blog generation unavailable. Using template fallback.")
    return _template_blog(product, keywords)


def _generate_with_ai(product: Dict, keywords: List[str]) -> str:
    kw_list = ", ".join(keywords)
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Write a 150-200 word SEO blog post for the following product.\n\n"
        f"Product Name : {product['name']}\n"
        f"Price        : {product['price']}\n"
        f"Rating       : {product['rating']}\n"
        f"Category     : {product.get('category', 'Electronics')}\n"
        f"Product URL  : {product.get('url', '#')}\n"
        f"SEO Keywords : {kw_list}\n\n"
        f"Write the blog post in Markdown:"
    )

    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
            ),
        )
        return response.text.strip()

    except Exception as e:
        print(f"  [Error] Blog generation failed: {e}")
        return ""


def _template_blog(product: Dict, keywords: List[str]) -> str:
    name = product["name"]
    price = product["price"]
    rating = product["rating"]
    url = product.get("url", "#")
    kw1 = keywords[0] if keywords else name
    kw2 = keywords[1] if len(keywords) > 1 else name

    return f"""# {name}: Is It Worth Buying in 2025?

If you've been searching for the **{kw1}**, look no further — the **{name}** 
has quickly become one of the top-rated options on the market.

## Why Shoppers Love It

Priced at just **{price}**, this product delivers exceptional value for money. 
With an impressive rating of **{rating}**, thousands of verified buyers confirm 
its quality and reliability.

Whether you need it for everyday use or as a premium gift, the {name} ticks all the 
boxes. It's a standout choice for anyone searching for a reliable **{kw2}**.

Built with quality materials and backed by stellar customer reviews, this product 
justifies every penny. Don't miss out — stock sells fast.

👉 **[Check the latest price on Amazon]({url})**

*Found this helpful? Share it with someone looking for the best deals!*
"""
