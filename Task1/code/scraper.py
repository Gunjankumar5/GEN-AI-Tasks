import os
import requests
from typing import List, Dict


NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"


def fetch_trending_news(limit: int = 5, category: str = "technology") -> List[Dict]:
    if NEWSAPI_KEY:
        return _fetch_from_newsapi(limit, category)
    else:
        print("  [Warning] NEWSAPI_KEY not set. Using mock trending articles.")
        return _mock_articles()[:limit]


def _fetch_from_newsapi(limit: int, category: str) -> List[Dict]:
    params = {
        "apiKey": NEWSAPI_KEY,
        "category": category,
        "language": "en",
        "pageSize": limit,
    }
    try:
        response = requests.get(NEWSAPI_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = []
        for item in data.get("articles", []):
            articles.append(
                {
                    "title": item.get("title", "Untitled"),
                    "summary": item.get("description") or item.get("content") or "",
                    "url": item.get("url", ""),
                    "source": item.get("source", {}).get("name", "Unknown"),
                }
            )
        return articles

    except requests.RequestException as e:
        print(f"  [Error] NewsAPI request failed: {e}")
        return _mock_articles()[:limit]


def _mock_articles() -> List[Dict]:
    return [
        {
            "title": "AI Breakthroughs Transforming Healthcare in 2025",
            "summary": (
                "Artificial intelligence is revolutionizing diagnostics, drug discovery, "
                "and personalized treatment plans at an unprecedented pace."
            ),
            "url": "https://example.com/ai-healthcare",
            "source": "Mock News",
        },
        {
            "title": "Electric Vehicles Hit Record Sales Globally",
            "summary": (
                "EV adoption surpassed all expectations this quarter as battery costs "
                "dropped and new charging infrastructure expanded rapidly."
            ),
            "url": "https://example.com/ev-record",
            "source": "Mock News",
        },
        {
            "title": "Climate Summit Reaches Historic Carbon Agreement",
            "summary": (
                "World leaders signed a landmark deal to cut carbon emissions by 50% "
                "before 2035, backed by a $500 billion green energy fund."
            ),
            "url": "https://example.com/climate-summit",
            "source": "Mock News",
        },
    ]
