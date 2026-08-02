"""
Pulls recent real headlines about a company via NewsAPI and MarketAux, 
so script generation has actual current facts to work with instead of 
improvising generic filler. Non-fatal on failure -- degrades to generic 
mode rather than blocking the whole pipeline.
"""
import os
import sys
import requests

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "").strip()
MARKETAUX_API_KEY = os.getenv("MARKETAUX_API_KEY", "").strip()


def fetch_newsapi_headlines(company: str, max_results: int = 3) -> list:
    if not NEWSAPI_KEY:
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
            return []
        articles = resp.json().get("articles", [])
        headlines = []
        for a in articles[:max_results]:
            title = a.get("title", "").strip()
            desc = (a.get("description") or "").strip()
            if title:
                headlines.append(f"{title}. {desc}".strip())
        return headlines
    except Exception:
        return []


def fetch_marketaux_headlines(company: str, max_results: int = 3) -> list:
    if not MARKETAUX_API_KEY:
        return []

    url = "https://api.marketaux.com/v1/news/all"
    params = {
        "q": company,
        "filter_entities": "true",
        "limit": max_results,
        "api_token": MARKETAUX_API_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            return []
        data = resp.json()
        headlines = []
        for article in data.get("data", [])[:max_results]:
            title = article.get("title", "").strip()
            desc = (article.get("description") or "").strip()
            if title:
                headlines.append(f"{title}. {desc}".strip())
        return headlines
    except Exception:
        return []


def fetch_recent_headlines(company: str, max_results: int = 3) -> list:
    headlines = []
    
    # 1. Try NewsAPI (broad general news coverage)
    newsapi_results = fetch_newsapi_headlines(company, max_results)
    headlines.extend(newsapi_results)
    
    # 2. Try MarketAux (financial-specific coverage) to supplement if needed
    if len(headlines) < max_results:
        marketaux_results = fetch_marketaux_headlines(company, max_results - len(headlines))
        headlines.extend(marketaux_results)
    
    # Deduplicate based on first 60 characters to avoid identical headlines from both sources
    unique_headlines = []
    seen = set()
    for h in headlines:
        key = h[:60].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique_headlines.append(h)
            
    if not unique_headlines:
        print("      [WARNING] Both NewsAPI and MarketAux failed or returned no results. "
              "Script will use generic content. Quality may suffer.", file=sys.stderr)
        
    return unique_headlines[:max_results]
