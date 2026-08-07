"""Uploads a finished video to YouTube using the YouTube Data API v3.
Uses a refresh token directly -- works identically locally and in GitHub Actions."""
import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_URI = "https://oauth2.googleapis.com/token"

def _get_credentials():
    if not (YT_CLIENT_ID and YT_CLIENT_SECRET and YT_REFRESH_TOKEN):
        print("FATAL: YT_CLIENT_ID, YT_CLIENT_SECRET, and YT_REFRESH_TOKEN must all be set.", file=sys.stderr)
        sys.exit(1)
    creds = Credentials(
        token=None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri=TOKEN_URI,
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET,
        scopes=SCOPES,
    )
    try:
        creds.refresh(Request())
    except Exception as e:
        print(f"FATAL: could not refresh YouTube access token -- your YT_REFRESH_TOKEN may be invalid or revoked: {e}", file=sys.stderr)
        sys.exit(1)
    return creds

def upload_video(video_path: str, title: str, description: str, tags: list, is_short: bool, privacy_status: str = "public", thumbnail_path: str = None):
    if not os.path.exists(video_path):
        print(f"FATAL: video file {video_path} does not exist, cannot upload.", file=sys.stderr)
        sys.exit(1)
    if is_short and "#shorts" not in title.lower() and "#shorts" not in description.lower():
        description = description + "\n#shorts"
    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": "25",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  upload progress: {int(status.progress() * 100)}%")
    if "id" not in response:
        print(f"FATAL: upload finished but response has no video id: {response}", file=sys.stderr)
        sys.exit(1)
    video_id = response["id"]
    print(f"Uploaded successfully: https://youtube.com/watch?v={video_id}")

    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumbnail_path)).execute()
            print(f"      [OK] Thumbnail set for {video_id}")
        except Exception as e:
            print(f"      [!] Thumbnail upload failed (non-fatal): {e}")

    return video_id
