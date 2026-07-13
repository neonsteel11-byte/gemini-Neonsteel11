"""
Free vidIQ-style competitor research using YouTube's own Data API (no extra
key needed -- reuses your existing YT credentials). Finds currently popular
videos about a topic so script generation can align with what's actually
getting views right now, instead of guessing blind.
"""
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _get_credentials():
    creds = Credentials(
        token=None, refresh_token=YT_REFRESH_TOKEN, token_uri=TOKEN_URI,
        client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET, scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def fetch_top_titles(query: str, max_results: int = 5) -> list:
    """
    Returns a list of currently popular video titles matching the query --
    real signal for what titles/angles are working right now.
    Non-fatal on failure, returns empty list.
    """
    try:
        youtube = build("youtube", "v3", credentials=_get_credentials())
        resp = youtube.search().list(
            part="snippet", q=query, type="video", order="viewCount",
            maxResults=max_results, publishedAfter="2026-01-01T00:00:00Z"
        ).execute()
        titles = [item["snippet"]["title"] for item in resp.get("items", [])]
        return titles
    except Exception as e:
        print(f"      [WARNING] Trending research failed ({e}), skipping.", file=sys.stderr)
        return []


if __name__ == "__main__":
    print(fetch_top_titles(sys.argv[1] if len(sys.argv) > 1 else "Tesla stock"))
