#!/usr/bin/env python3
import os, json, subprocess
from datetime import datetime
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
        raise RuntimeError("FATAL: Missing one or more YouTube environment secrets (ID, Secret, or Refresh Token).")

    # Assemble the token configuration on the fly
    token_info = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
    }
    
    creds = Credentials.from_authorized_user_info(token_info)
    return build('youtube', 'v3', credentials=creds)

def check_safety():
    with open(STATE_PATH, "r") as f:
        state = json.load(f)

    today = datetime.utcnow().strftime('%Y-%m-%d')
    if state.get("last_run_date") != today:
        print(f"-> New day detected. Resetting daily upload counter.")
        state["uploads_today"] = 0
        state["last_run_date"] = today
        with open(STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)

    if state.get("paused", True):
        raise SystemExit("CRITICAL: Automation is PAUSED via system_state.json (set to false to run)")
    if state.get("uploads_today", 0) >= state.get("max_daily_uploads", 2):
        raise SystemExit(f"CRITICAL: Daily upload cap reached.")

    return state

def run_upload():
    state = check_safety()

    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    if manifest.get("status") != "ready":
        raise SystemExit(f"Manifest status is '{manifest.get('status')}'. Needs to be 'ready' to upload.")

    metadata = manifest.get("metadata", {})
    title = metadata.get("title", "").strip()
    description = metadata.get("description", "").strip()
    category_id = metadata.get("categoryId", "22")
    privacy_status = metadata.get("privacyStatus", "private")
    file_path = manifest.get("file_path", "output/final_output.mp4")

    if not title or not description:
        raise RuntimeError("FATAL: Missing title or description in manifest. Aborting.")

    print(f"-> Starting Upload (Test Mode: {TEST_MODE})")
    print(f"-> Title: {title}")

    if TEST_MODE:
        video_id = "DRYRUN_TEST_ID"
        print("-> Dry run successful. No API call made.")
    else:
        # REAL UPLOAD LOGIC
        youtube = get_authenticated_service()
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category_id
            },
            "status": {"privacyStatus": privacy_status}
        }
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        video_id = response.get("id")
        print(f"-> Video uploaded successfully: {video_id}")

    # Update manifest
    manifest["status"] = "published"
    manifest["youtube_video_id"] = video_id
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    # Update state counter
    state["uploads_today"] += 1
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

    # Git Commit flow back to repo
    subprocess.run(["git", "config", "user.name", "Syndicate Bot"], check=True)
    subprocess.run(["git", "config", "user.email", "bot@syndicate.local"], check=True)
    subprocess.run(["git", "add", MANIFEST_PATH, STATE_PATH], check=True)
    subprocess.run(["git", "commit", "-m", "chore: update ledger and state [skip ci]"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)

    print(f"-> Process complete.")

if __name__ == "__main__":
    run_upload()
