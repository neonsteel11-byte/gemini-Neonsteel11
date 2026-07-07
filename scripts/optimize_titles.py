"""
Checks videos uploaded more than MIN_AGE_HOURS ago. If a video's views are
below VIEW_THRESHOLD, swaps its title/description/hashtags to the next
pre-generated variant (one swap per video, never repeated -- looping titles
constantly reads as manipulative and risks policy flags).
"""
import json
import os
import sys
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

MANIFEST_PATH = "video_manifest.json"
MIN_AGE_HOURS = int(os.getenv("OPTIMIZE_AFTER_HOURS", "24"))
VIEW_THRESHOLD = int(os.getenv("MIN_VIEWS_THRESHOLD", "50"))

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _get_credentials():
    creds = Credentials(
        token=None, refresh_token=YT_REFRESH_TOKEN, token_uri=TOKEN_URI,
        client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET, scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def _load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        print("No manifest found -- nothing to optimize yet.")
        sys.exit(0)
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def main():
    manifest = _load_manifest()
    youtube = build("youtube", "v3", credentials=_get_credentials())
    now = datetime.now(timezone.utc)
    changed = False

    for entry in manifest:
        if entry.get("optimized"):
            continue

        uploaded_at = datetime.fromisoformat(entry["uploaded_at"])
        age_hours = (now - uploaded_at).total_seconds() / 3600
        if age_hours < MIN_AGE_HOURS:
            continue

        video_id = entry["video_id"]
        stats = youtube.videos().list(part="statistics,snippet", id=video_id).execute()
        items = stats.get("items", [])
        if not items:
            print(f"      {video_id}: not found (deleted/private issue?), skipping.")
            continue

        views = int(items[0]["statistics"].get("viewCount", 0))
        print(f"      {video_id}: {views} views after {age_hours:.1f}h (threshold {VIEW_THRESHOLD})")

        if views >= VIEW_THRESHOLD:
            entry["optimized"] = True  # performing fine, stop tracking it
            changed = True
            continue

        variants = entry["title_variants"]
        next_index = entry["variant_index"] + 1
        if next_index >= len(variants):
            entry["optimized"] = True  # no more variants left to try
            changed = True
            print(f"      {video_id}: underperforming but no variants left, marking done.")
            continue

        new_title = variants[next_index]
        hashtags = " ".join(entry.get("hashtags", []))
        new_description = (
            f"{new_title}\n\nFunny finance commentary on {entry['company']}. "
            f"Satire, not financial advice.\n\n{hashtags}"
        )

        snippet = items[0]["snippet"]
        snippet["title"] = new_title[:100]
        snippet["description"] = new_description[:5000]

        youtube.videos().update(part="snippet", body={"id": video_id, "snippet": snippet}).execute()

        entry["variant_index"] = next_index
        entry["optimized"] = True
        changed = True
        print(f"      {video_id}: underperforming, switched to variant {next_index}: '{new_title}'")

    if changed:
        _save_manifest(manifest)
        print("Manifest updated.")
    else:
        print("Nothing to update this run.")


if __name__ == "__main__":
    main()
