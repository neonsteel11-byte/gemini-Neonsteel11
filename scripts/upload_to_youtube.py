#!/usr/bin/env python3
import os, json, subprocess
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

MANIFEST_PATH = "output/manifest.json"
TEST_MODE = os.environ.get("TEST_MODE", "true") == "true"

def get_authenticated_service():
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

def determine_current_slot():
    """Determines which content wave to deploy based on the closest target hour."""
    now = datetime.now(timezone.utc)
    
    # Run 1: Noon Short (Target 06:15 UTC)
    # Run 2: Evening Long (Target 12:30 UTC)
    if now.hour < 10:
        return "short", 6, 15
    else:
        return "long", 12, 30

def apply_viral_hooks(title, description, video_type):
    """Auto-hooks metadata with viral formatting parameters optimized for finance content."""
    # Ensure title uses clean capitalization or emotional psychological anchors
    clean_title = title.strip()
    
    if video_type == "short":
        # Shorts require immediate context hooks and loop tags
        if not clean_title.endswith("!") and "#" not in clean_title:
            clean_title += " 🤯"
        if "#shorts" not in clean_title.lower():
            clean_title += " #shorts"
        
        hooked_desc = f"{description}\n\n#shorts #finance #money #wealth #funnyfinance"
    else:
        # Long form optimization requires algorithmic spacing
        hooked_desc = (
            f"⚡ {clean_title} ⚡\n\n"
            f"{description}\n\n"
            "--- \n"
            "📈 Welcome to the Syndicate System. Don't forget to Like and Subscribe for daily financial comedy loops!\n\n"
            "#finance #investing #wealth #stocks #comedy"
        )
        
    return clean_title, hooked_desc

def run_upload():
    if not os.path.exists(MANIFEST_PATH):
        print("-> No operational manifest found. Skipping runtime execution.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    video_type, target_hour, target_minute = determine_current_slot()
    status_key = f"{video_type}_status"
    file_path = f"output/final_{video_type}.mp4"

    if manifest.get(status_key) != "ready":
        print(f"-> Segment slot '{video_type}' is not marked as ready in the tracking ledger.")
        return

    if not os.path.exists(file_path):
        print(f"-> Media missing at path: {file_path}. Aborting automation step.")
        return

    # Calculate release window timestamp
    now = datetime.now(timezone.utc)
    target_time = datetime.combine(now.date(), datetime.min.time()).replace(
        hour=target_hour, minute=target_minute, tzinfo=timezone.utc
    )
    if target_time <= now + timedelta(minutes=15):
        target_time += timedelta(days=1)
    publish_at = target_time.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    # Extract baseline raw metadata
    metadata = manifest.get(f"{video_type}_metadata", {})
    raw_title = metadata.get("title", f"The Ultimate Secret to Wealth Ep. {now.day}")
    raw_desc = metadata.get("description", "Automated distribution run.")

    # Apply the Auto-Hook Optimization layer
    viral_title, viral_desc = apply_viral_hooks(raw_title, raw_desc, video_type)

    print(f"-> Executing Hooked Upload Pipeline [{video_type.upper()} SLOT]")
    print(f"-> Title: {viral_title}")
    print(f"-> Scheduled Release Time: {publish_at}")

    if TEST_MODE:
        video_id = f"DRYRUN_{video_type.upper()}_ID"
        print("-> Test configuration verification complete.")
    else:
        youtube = get_authenticated_service()
        body = {
            "snippet": {
                "title": viral_title,
                "description": viral_desc,
                "categoryId": "22" # People & Blogs/Entertainment fallback
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_at
            }
        }
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        video_id = response.get("id")
        print(f"-> Asset pushed successfully! Video ID reference: {video_id}")

    # Log changes to the manifest ledger
    manifest[status_key] = "scheduled"
    manifest[f"youtube_{video_type}_id"] = video_id
    manifest[f"{video_type}_publish_at"] = publish_at
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    try:
        subprocess.run(["git", "config", "user.name", "Syndicate Bot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@syndicate.local"], check=True)
        subprocess.run(["git", "add", MANIFEST_PATH], check=True)
        subprocess.run(["git", "commit", "-m", f"chore: schedule daily {video_type} release window [skip ci]"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except Exception as e:
        print(f"-> Synchronization tracking skipped: {e}")

if __name__ == "__main__":
    run_upload()
