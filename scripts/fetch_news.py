"""
Pulls 2-3 recent real headlines about a company via NewsAPI, so script
generation has actual current facts to work with instead of improvising
generic filler. Non-fatal on failure -- degrades to generic mode rather
than blocking the whole pipeline, but quality suffers without it.
"""
import os
import sys
import requests

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "").strip()


def fetch_recent_headlines(company: str, max_results: int = 3) -> list:
    if not NEWSAPI_KEY:
        print("      [WARNING] NEWSAPI_KEY not set -- script will use generic "
              "content instead of real news. Quality will suffer.", file=sys.stderr)
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": company,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_results,
        "apiKey": NEWSAPI_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            print(f"      [WARNING] NewsAPI returned {resp.status_code}, "
                  f"falling back to generic content.", file=sys.stderr)
            return []
        articles = resp.json().get("articles", [])
        headlines = []
        for a in articles[:max_results]:
            title = a.get("title", "").strip()
            desc = (a.get("description") or "").strip()
            if title:
                headlines.append(f"{title}. {desc}".strip())
        return headlines
    except Exception as e:
        print(f"      [WARNING] News fetch failed ({e}), falling back to generic content.",
              file=sys.stderr)
        return []
