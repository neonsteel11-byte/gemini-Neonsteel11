#!/usr/bin/env python3
import os, json, subprocess
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

MANIFEST_PATH = "output/manifest.json"
STATE_PATH = "output/system_state.json"
TEST_MODE = os.environ.get("TEST_MODE", "true") == "true"

def get_authenticated_service():
    """Builds the YouTube API service object using individual environment secrets."""
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise RuntimeError("FATAL: Missing one or more YouTube environment secrets.")

    token_info = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
    }
    creds = Credentials.from_authorized_user_info(token_info)
    return build('youtube', 'v3', credentials=creds)

def calculate_publish_time():
    """Computes the next 09:00 UTC publishing slot with a safety buffer."""
    now = datetime.now(timezone.utc)
    # Target 09:00 AM UTC today
    target = datetime.combine(now.date(), datetime.min.time()).replace(hour=9, tzinfo=timezone.utc)
    
    # If 09:00 UTC has passed today (or is less than 15 mins away), schedule for tomorrow
    if target <= now + timedelta(minutes=15):
        target += timedelta(days=1)
        
    return target.replace(microsecond=0).isoformat().replace("+00:00", "Z")

def run_upload():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if manifest.get("status") != "ready":
        print(f"-> Manifest status is '{manifest.get('status')}'. No upload required.")
        return

    metadata = manifest.get("metadata", {})
    title = metadata.get("title", "").strip()
    description = metadata.get("description", "").strip()
    category_id = metadata.get("categoryId", "22")
    file_path = manifest.get("file_path", "output/final_output.mp4")

    # Calculate the automated release window
    publish_at = calculate_publish_time()

    print(f"-> Starting Scheduled Upload Flow (Test Mode: {TEST_MODE})")
    print(f"-> Title: {title}")
    print(f"-> Target release slot (UTC): {publish_at}")

    if TEST_MODE:
        video_id = "DRYRUN_TEST_ID"
        print("-> Dry run successful. Scheduled parameters validated.")
    else:
        youtube = get_authenticated_service()
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_at
            }
        }
        
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        video_id = response.get("id")
        print(f"-> Video successfully uploaded and scheduled! ID: {video_id}")

    # Track status change back to repository ledger
    manifest["status"] = "scheduled"
    manifest["youtube_video_id"] = video_id
    manifest["publish_at"] = publish_at
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    try:
        subprocess.run(["git", "config", "user.name", "Syndicate Bot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@syndicate.local"], check=True)
        subprocess.run(["git", "add", MANIFEST_PATH], check=True)
        subprocess.run(["git", "commit", "-m", "chore: schedule video distribution slot [skip ci]"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except Exception as e:
        print(f"-> Git sync skipped: {e}")

if __name__ == "__main__":
    run_upload()
