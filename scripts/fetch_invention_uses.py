"""
Fetches detailed information about an invention including:
- What it is
- How it's used
- Modern applications
- Industries that use it
"""
import requests
from urllib.parse import quote

def fetch_invention_details(invention: str) -> dict:
    """Fetch comprehensive invention info from Wikipedia."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(invention)}"
    
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "AccidentalGeniusBot/1.0"})
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}"}
        
        data = resp.json()
        
        # Fetch full article for "Uses" section
        full_url = f"https://en.wikipedia.org/w/api.php?action=parse&format=json&prop=text&section=0&page={quote(invention)}"
        full_resp = requests.get(full_url, timeout=15)
        
        uses_section = ""
        applications = []
        
        if full_resp.status_code == 200:
            html = full_resp.json()["parse"]["text"]["*"]
            # Extract "Uses" or "Applications" section
            if "uses" in html.lower() or "applications" in html.lower():
                # Simple extraction - get text after "Uses" heading
                import re
                uses_match = re.search(r'(?:Uses|Applications).*?(?=<h2|$)', html, re.IGNORECASE | re.DOTALL)
                if uses_match:
                    # Strip HTML tags
                    uses_text = re.sub(r'<[^>]+>', '', uses_match.group(0))
                    uses_section = uses_text.strip()[:500]  # First 500 chars
                    applications = [app.strip() for app in uses_text.split('\n') if len(app.strip()) > 20][:5]
        
        return {
            "title": data.get("title", invention),
            "extract": data.get("extract", ""),
            "uses": uses_section,
            "applications": applications,
            "image_url": data.get("thumbnail", {}).get("source"),
            "description": data.get("description", ""),
        }
    except Exception as e:
        print(f"      [WARNING] Failed to fetch invention details: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import sys
    invention = sys.argv[1] if len(sys.argv) > 1 else "Potato chip"
    details = fetch_invention_details(invention)
    import json
    print(json.dumps(details, indent=2))
