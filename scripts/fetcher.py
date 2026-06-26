import os
import requests

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://api.marketaux.com/v1/news/all"
COMPANIES = ["Tesla", "Apple", "Amazon", "Nike", "Meta"]

def fetch_headlines(limit=20):
    if not API_KEY:
        print("Warning: NEWS_API_KEY is missing.")
        return []
    params = {
        "api_token": API_KEY,
        "language": "en",
        "limit": limit
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        headlines = []
        for item in data.get("data", []):
            title = item.get("title")
            if title:
                for c in COMPANIES:
                    if c.lower() in title.lower():
                        headlines.append({"headline": title, "summary": item.get("description", "")})
                        break
        return headlines
    except Exception as e:
        print(f"Fetcher error: {e}")
        return []