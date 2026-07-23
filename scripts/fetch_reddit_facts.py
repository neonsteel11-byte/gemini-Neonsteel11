"""
Searches Reddit's public search API (no auth needed) for real discussion/
facts about a topic, supplementing Wikipedia grounding with additional
interesting angles people have actually discussed.
"""
import sys
import requests

SEARCH_URL = "https://www.reddit.com/search.json"


def fetch_reddit_context(topic: str, limit: int = 5) -> list:
    headers = {"User-Agent": "AccidentalGeniusBot/1.0"}
    params = {"q": topic, "sort": "top", "limit": limit, "t": "all"}
    try:
        resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            return []
        posts = resp.json()["data"]["children"]
        snippets = []
        for post in posts:
            title = post["data"].get("title", "").strip()
            if title and len(title) > 15:
                snippets.append(title)
        return snippets[:limit]
    except Exception as e:
        print(f"      [WARNING] Reddit context fetch failed: {e}", file=sys.stderr)
        return []


if __name__ == "__main__":
    print(fetch_reddit_context(sys.argv[1] if len(sys.argv) > 1 else "penicillin"))
