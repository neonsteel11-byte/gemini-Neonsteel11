import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "youtube_token.pickle"
CLIENT_SECRETS_FILE = "client_secrets.json"

def get_youtube_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(video_path, title, description, privacy_status="private", publish_at=None):
    if not os.path.exists(video_path):
        return None
        
    youtube = get_youtube_service()
    body = {
        "snippet": {"title": title, "description": description, "categoryId": "22"},
        "status": {
            "privacyStatus": privacy_status, 
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True # Compliance flag for AI content
        }
    }
    if publish_at:
        body["status"]["publishAt"] = publish_at
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
    return response.get('id')