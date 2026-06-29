import os
import sys
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video_to_youtube(file_path, title, description, category_id="23", tags=None):
    if not os.path.exists(file_path):
        print(f"⚠️ Video asset {file_path} not found. Skipping.")
        return

    print(f"🚀 Initializing API upload payload for: {file_path}...")
    
    # Reconstruct credentials from individual GitHub Secrets
    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")
    refresh_token = os.getenv("YT_REFRESH_TOKEN")
    
    if not client_id or not client_secret or not refresh_token:
        print("❌ Missing credentials during production upload loop.")
        sys.exit(1)

    creds_info = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    
    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(creds_info)
    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or ["finance", "comedy", "shorts"],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    
    try:
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        print(f"📤 Uploading {title} directly to your channel feed...")
        response = request.execute()
        print(f"🎉 SUCCESS! Video published. Video ID: {response.get('id')}")
    except Exception as e:
        print(f"❌ API Upload Error: {e}")

if __name__ == "__main__":
    print("==================================================")
    print("-> RUNNING YOUTUBE PRODUCTION UPLOAD ENGINE...")
    print("==================================================")
    
    # Post the Shorts Video
    upload_video_to_youtube(
        file_path="output/final_short.mp4",
        title="Tech Layoffs Be Like... 😂 #shorts",
        description="A funny automated take on recent tech company layoff trends."
    )
    
    # Post the Long Video
    upload_video_to_youtube(
        file_path="output/final_long.mp4",
        title="The State of Multi-Billion Dollar EV Companies",
        description="A deeper human-style comedy roast about EV companies navigating market shifts."
    )
    
    print("==================================================")
    print("🎉 FULL CONVERGENCE LOOP COMPLETE!")
    print("==================================================")
