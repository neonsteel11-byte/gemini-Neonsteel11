"""
Checks the manifest for private videos older than PUBLISH_DELAY_HOURS.
If still private, flips them to public -- giving a review window without
requiring manual intervention every run.
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
PUBLISH_DELAY_HOURS = float(os.getenv("PUBLISH_DELAY_HOURS", "2"))

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _get_credentials():
    creds = Credentials(
        token=None, refresh_token=YT_REFRESH_TOKEN, token_uri=TOKEN_URI,
        client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET, scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def main():
    if not os.path.exists(MANIFEST_PATH):
        print("No manifest found -- nothing to publish yet.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    youtube = build("youtube", "v3", credentials=_get_credentials())
    now = datetime.now(timezone.utc)
    changed = False

    for entry in manifest:
        # Treat missing "privacy" key as private too (covers videos uploaded
        # before this field was added to the manifest schema)
        if entry.get("privacy", "private") != "private" or entry.get("auto_published"):
            continue

        uploaded_at = datetime.fromisoformat(entry["uploaded_at"])
        age_hours = (now - uploaded_at).total_seconds() / 3600
        if age_hours < PUBLISH_DELAY_HOURS:
            print(f"      {entry['video_id']}: only {age_hours:.1f}h old, waiting for {PUBLISH_DELAY_HOURS}h.")
            continue

        video_id = entry["video_id"]
        try:
            resp = youtube.videos().list(part="status", id=video_id).execute()
            items = resp.get("items", [])
            if not items:
                print(f"      {video_id}: not found, skipping.")
                continue
            status = items[0]["status"]
            status["privacyStatus"] = "public"
            youtube.videos().update(part="status", body={"id": video_id, "status": status}).execute()
            entry["auto_published"] = True
            entry["privacy"] = "public"
            changed = True
            print(f"      {video_id}: published to PUBLIC after {age_hours:.1f}h review window.")
        except Exception as e:
            print(f"      {video_id}: FAILED to publish: {e}", file=sys.stderr)

    if changed:
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print("Manifest updated.")
    else:
        print("Nothing ready to publish this run.")


if __name__ == "__main__":
    main()
