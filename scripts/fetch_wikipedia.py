"""
Fetches real facts and a real image URL for a person/invention from
Wikipedia's public REST API (free, no key). Used so inventor-history
videos use ACTUAL historical images instead of AI-generated faces --
more accurate and avoids AI-likeness risk entirely.
"""
import sys
import requests
from urllib.parse import quote

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"


def fetch_wiki_info(title: str) -> dict:
    """
    Returns {"summary": str, "image_url": str or None} for a Wikipedia page.
    Non-fatal on failure -- returns empty summary/no image, caller decides
    whether to fall back to an AI-generated illustration instead.
    """
    url = WIKI_API.format(title=quote(title.replace(" ", "_")))
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "FinanceInventionBot/1.0"})
        if resp.status_code != 200:
            print(f"      [WARNING] Wikipedia lookup failed for '{title}' "
                  f"({resp.status_code}), no real image available.", file=sys.stderr)
            return {"summary": "", "image_url": None}
        data = resp.json()
        summary = data.get("extract", "")
        image_url = None
        if "originalimage" in data:
            image_url = data["originalimage"].get("source")
        elif "thumbnail" in data:
            image_url = data["thumbnail"].get("source")
        return {"summary": summary, "image_url": image_url}
    except Exception as e:
        print(f"      [WARNING] Wikipedia fetch error for '{title}': {e}", file=sys.stderr)
        return {"summary": "", "image_url": None}


if __name__ == "__main__":
    result = fetch_wiki_info(sys.argv[1] if len(sys.argv) > 1 else "Thomas Edison")
    print(result)
