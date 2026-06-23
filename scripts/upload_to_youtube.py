import os
import glob
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

VIDEO_DIR = "output"
MANIFEST_PATH = os.path.join(VIDEO_DIR, "manifest.json")

CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
    raise SystemExit("Environment variables not set.")

# 1. Load Dynamic Metadata from the Syndicate Ledger if it exists
title = os.environ.get("YT_DEFAULT_TITLE", "Automated Upload")
description = "Uploaded via automated pipeline."
privacy_status = os.environ.get("YT_PRIVACY", "private")
category_id = "22"

if os.path.exists(MANIFEST_PATH):
    try:
        with open(MANIFEST_PATH, "r") as f:
            manifest = json.load(f)
        if manifest.get("status") == "published":
            raise SystemExit("Manifest indicates this video was already published. Skipping.")
        
        meta = manifest.get("metadata", {})
        title = meta.get("title", title)
        description = meta.get("description", description)
        privacy_status = meta.get("privacyStatus", privacy_status)
        category_id = meta.get("categoryId", category_id)
        print("-> Successfully loaded metadata from manifest.json")
    except Exception as e:
        print(f"Warning: Failed to parse manifest.json ({e}). Using env fallbacks.")

# 2. Authenticate
creds = Credentials(
    token=None, 
    refresh_token=REFRESH_TOKEN, 
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET,
    scopes=[
        "https://www.googleapis.com/auth/youtube.upload", 
        "https://www.googleapis.com/auth/youtube.force-ssl"
    ]
)

youtube = build("youtube", "v3", credentials=creds)
videos = sorted(glob.glob(os.path.join(VIDEO_DIR, "*.mp4")))

if not videos:
    raise SystemExit("No .mp4 files found.")

video_file = videos[-1]
media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

body = {
    "snippet": {
        "title": title[:100],  # YouTube Max Cap
        "description": description[:5000], 
        "categoryId": category_id
    }, 
    "status": {
        "privacyStatus": privacy_status
    }
}

print(f"Uploading {video_file} with title: '{title}'...")
request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
response = request.execute()

video_id = response.get("id")
print("Upload complete. Video id:", video_id)

# 3. Update the Ledger Status to prevent double-uploads
if os.path.exists(MANIFEST_PATH):
    try:
        manifest["status"] = "published"
        manifest["youtube_video_id"] = video_id
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=2)
        print("-> manifest.json updated to published state.")
    except Exception as e:
        print(f"Failed to update manifest.json status: {e}")