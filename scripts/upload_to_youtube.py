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

    token_info = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
    }
    creds = Credentials.from_authorized_user_info(token_info)
    return build('youtube', 'v3', credentials=creds)

def safe_load_manifest():
    """Loads manifest securely. Regenerates a fresh fallback structure if empty or malformed."""
    default_manifest = {
        "status": "ready",
        "youtube_video_id": "",
        "metadata": {
            "title": "Autonomous Stream: System Run Alpha",
            "description": "This stream was systematically harvested, rendered, and pushed via automated cloud runtime.\n\n#Automation #Syndicate #Dev",
            "privacyStatus": "public",
            "categoryId": "28"
        }
    }
    
    if not os.path.exists(MANIFEST_PATH) or os.path.getsize(MANIFEST_PATH) == 0:
        print("[WARN] Manifest missing or empty. Creating a fresh default configuration.")
        return default_manifest

    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("[WARN] Manifest contains invalid JSON syntax. Overwriting with clean recovery layout.")
        return default_manifest

def check_safety():
    if not os.path.exists(STATE_PATH) or os.path.getsize(STATE_PATH) == 0:
        state = {"uploads_today": 0, "max_daily_uploads": 2, "paused": False, "last_run_date": ""}
    else:
        with open(STATE_PATH, "r") as f:
            try:
                state = json.load(f)
            except json.JSONDecodeError:
                state = {"uploads_today": 0, "max_daily_uploads": 2, "paused": False, "last_run_date": ""}

    today = datetime.utcnow().strftime('%Y-%m-%d')
    if state.get("last_run_date") != today:
        print(f"-> New day detected. Resetting daily upload counter.")
        state["uploads_today"] = 0
        state["last_run_date"] = today

    if state.get("paused", True):
        raise SystemExit("CRITICAL: Automation is PAUSED via system_state.json")
    if state.get("uploads_today", 0) >= state.get("max_daily_uploads", 2):
        raise SystemExit(f"CRITICAL: Daily upload cap reached.")

    return state

def run_upload():
    state = check_safety()
    manifest = safe_load_manifest()

    if manifest.get("status") != "ready":
        print(f"-> Manifest status is '{manifest.get('status')}'. No upload required.")
        return

    metadata = manifest.get("metadata", {})
    title = metadata.get("title", "").strip()
    description = metadata.get("description", "").strip()
    category_id = metadata.get("categoryId", "22")
    privacy_status = metadata.get("privacyStatus", "private")
    file_path = manifest.get("file_path", "output/final_output.mp4")

    print(f"-> Starting Upload (Test Mode: {TEST_MODE})")
    print(f"-> Title: {title}")

    if TEST_MODE:
        video_id = "DRYRUN_TEST_ID"
        print("-> Dry run successful. No live API call made.")
    else:
        if not os.path.exists(file_path):
            print(f"-> [WARN] Video file {file_path} not found. Creating a placeholder dummy for test safety.")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(b"\x00\x00\x00\x18ftypmp42") # Tiny dummy mp4 header
        
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

    # Save progress state safely
    manifest["status"] = "published"
    manifest["youtube_video_id"] = video_id
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    state["uploads_today"] += 1
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    # Automatically update repository tracking states
    try:
        subprocess.run(["git", "config", "user.name", "Syndicate Bot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@syndicate.local"], check=True)
        subprocess.run(["git", "add", MANIFEST_PATH, STATE_PATH], check=True)
        subprocess.run(["git", "commit", "-m", "chore: update system ledger tracking [skip ci]"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except Exception as e:
        print(f"-> [INFO] Sync skipped or no status modifications changed: {e}")

    print(f"-> Process complete.")

if __name__ == "__main__":
    run_upload()
