import os, glob
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

VIDEO_DIR = "output"
CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")

if not (CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN):
    raise SystemExit("Environment variables not set.")

creds = Credentials(token=None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token",
                    client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                    scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"])

youtube = build("youtube", "v3", credentials=creds)
videos = sorted(glob.glob(os.path.join(VIDEO_DIR, "*.mp4")))

if not videos:
    raise SystemExit("No .mp4 files found.")

video_file = videos[-1]
media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
body = {"snippet":{"title": os.environ.get("YT_DEFAULT_TITLE", "Upload"), "categoryId":"22"}, "status":{"privacyStatus": os.environ.get("YT_PRIVACY", "private")}}

print(f"Uploading {video_file}...")
request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
response = request.execute()
print("Upload complete. Video id:", response.get("id"))
