import os
import sys
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video_to_youtube(file_path, title, description, tags=None):
    if not os.path.exists(file_path):
        print(f"⚠️ Video asset {file_path} not found.")
        return

    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")
    refresh_token = os.getenv("YT_REFRESH_TOKEN")

    creds_info = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    
    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(creds_info)
    youtube = build("youtube", "v3", credentials=credentials)

    # Explicitly structuring the metadata payload body
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or ["finance", "comedy", "shorts", "stocks"],
            "categoryId": "23" # Comedy
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)
    
    try:
        # Pushing both body (metadata) and media_body (the video file) together
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        print(f"📤 Deploying live: {title}...")
        response = request.execute()
        print(f"🎉 Published! Video ID: {response.get('id')}")
    except Exception as e:
        print(f"❌ Upload Error: {e}")

if __name__ == "__main__":
    print("==================================================")
    print("-> RUNNING METADATA-FIX UPLOAD ENGINE...")
    print("==================================================")
    
    upload_video_to_youtube(
        file_path="output/final_short.mp4",
        title="Tech Layoffs Be Like... 😂 #shorts #finance #tech",
        description="When the company lays off 10,000 people but the stock price goes up. #shorts #finance #comedy"
    )
    
    upload_video_to_youtube(
        file_path="output/final_long.mp4",
        title="The Reality of Multi-Billion Dollar EV Companies",
        description="An in-depth comedy roast about electric vehicle companies trying to survive the market shifts. #finance #ev #stocks #business"
    )
