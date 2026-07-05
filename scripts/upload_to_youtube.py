#!/usr/bin/env python3
import os
import sys
import json
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_youtube_client():
    """Authenticates using the GitHub Actions Repository Secrets."""
    # Read tokens from environmental variables injected by GitHub Actions secrets
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    
    if not refresh_token:
        print("❌ [API ERROR]: YOUTUBE_REFRESH_TOKEN secret is completely missing from GitHub.")
        sys.exit(1)

    info = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    
    creds = Credentials.from_authorized_user_info(info)
    return build("youtube", "v3", credentials=creds)

def upload_real_file(file_path, title, description, category_id="22"):
    """Physically streams the MP4 video binary straight into YouTube Studio."""
    if not os.path.exists(file_path):
        print(f"❌ [API ERROR]: Source file not found at {file_path}")
        return False

    print(f"🚀 [API REAL WORK]: Initializing multi-part binary stream for {file_path}...")
    youtube = get_youtube_client()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "private",  # Staged as private so you can inspect it before going public
            "selfDeclaredMadeForKids": False
        }
    }

    # Stream file chunks seamlessly over HTTP
    media = MediaFileUpload(
        file_path, 
        mimetype="video/mp4", 
        chunksize=1024*1024, 
        resumable=True
    )

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"📦 [API Real Work]: Uploading... {int(status.progress() * 100)}% complete.")
                
        print(f"✅ [API Real Work]: SUCCESS! Video deployed. Real YouTube Video ID: {response['id']}")
        return True

    except HttpError as e:
        print(f"❌ [API ERROR]: Google API Rejected Request: {e.content.decode('utf-8')}")
        sys.exit(1)

if __name__ == "__main__":
    print("⚡ [VISION Core]: Initializing real network transmission channels...")
    
    # Upload the Short form asset
    upload_real_file(
        file_path="output/airbnb_short.mp4",
        title="The Insane Reality of Airbnb 🤯",
        description="How an online rental engine changed the real estate economy forever."
    )
