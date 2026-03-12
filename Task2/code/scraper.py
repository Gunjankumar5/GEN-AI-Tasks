"""
scraper.py — Scrape trending / best-selling products from Amazon using BeautifulSoup.

Note: Amazon aggressively blocks scrapers. This module uses:
  1. Realistic headers + randomised delays
  2. A fallback mock dataset if scraping fails (for demo purposes)

For production use, consider the Amazon Product Advertising API or
a paid scraping service (Oxylabs, ScraperAPI, etc.).
"""

import time
import random
import requests
from typing import List, Dict
from bs4 import BeautifulSoup

AMAZON_BESTSELLERS_URL = "https://www.amazon.com/Best-Sellers/zgbs/electronics/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}


def scrape_trending_products(
    limit: int = 5,
    url: str = AMAZON_BESTSELLERS_URL,
    category: str = "Electronics",
) -> List[Dict]:
    """
    Scrape best-selling products.

    Args:
        limit: Max number of products to return.
        url: Amazon best-sellers page URL.
        category: Product category label to attach to each product.

    Returns:
        List of product dicts: {name, price, rating, reviews, url, category}
    """
    try:
        time.sleep(random.uniform(1.5, 3.0))  # polite delay
        response = requests.get(url, headers=HEADERS, timeout=12)
        response.raise_for_status()
        return _parse_products(response.text, limit, category)
    except requests.RequestException as e:
        print(f"  [Warning] Scraping failed ({e}). Using mock product data.")
        return _mock_products()[:limit]


def _parse_products(html: str, limit: int, category: str) -> List[Dict]:
    """Parse Amazon bestsellers HTML."""
    soup = BeautifulSoup(html, "html.parser")
    products = []

    items = soup.select("div.zg-grid-general-faceout")[:limit]
    if not items:
        print("  [Warning] Selector matched 0 items — HTML structure may have changed.")
        return _mock_products()[:limit]

    for item in items:
        name_tag = item.select_one("div._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
        price_tag = item.select_one("span.p13n-sc-price")
        rating_tag = item.select_one("span.a-icon-alt")
        link_tag = item.select_one("a.a-link-normal")

        products.append(
            {
                "name": name_tag.get_text(strip=True) if name_tag else "Unknown Product",
                "price": price_tag.get_text(strip=True) if price_tag else "N/A",
                "rating": rating_tag.get_text(strip=True) if rating_tag else "N/A",
                "url": "https://www.amazon.com" + link_tag["href"] if link_tag else "",
                "category": category,
            }
        )

    return products if products else _mock_products()[:limit]


def _mock_products() -> List[Dict]:
    """Fallback mock products for offline demo."""
    return [
        {
            "name": "Apple AirPods Pro (2nd Generation)",
            "price": "$189.99",
            "rating": "4.7 out of 5 stars",
            "reviews": "85,342",
            "url": "https://www.amazon.com/apple-airpods-pro",
            "category": "Electronics",
        },
        {
            "name": "Anker 65W USB-C Charging Station",
            "price": "$35.99",
            "rating": "4.8 out of 5 stars",
            "reviews": "42,187",
            "url": "https://www.amazon.com/anker-charger",
            "category": "Electronics",
        },
        {
            "name": "Kindle Paperwhite (16 GB)",
            "price": "$139.99",
            "rating": "4.6 out of 5 stars",
            "reviews": "63,450",
            "url": "https://www.amazon.com/kindle-paperwhite",
            "category": "Electronics",
        },
    ]
