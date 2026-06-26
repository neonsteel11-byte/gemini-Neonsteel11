import os
import json
from datetime import datetime, timezone
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

LEDGER_PATH = "ledger.json"

def get_youtube_service():
    # Inherit saved authorization credentials seamlessly
    if os.path.exists("youtube_token.pickle"):
        import pickle
        with open("youtube_token.pickle", "rb") as token:
            creds = pickle.load(token)
        return build("youtube", "3", credentials=creds)
    return None

def reconcile_manifest_with_youtube():
    if not os.path.exists(LEDGER_PATH):
        return
        
    with open(LEDGER_PATH, "r") as f:
        manifest = json.load(f)
        
    youtube = get_youtube_service()
    if not youtube:
        print("[Reconciler] Skipping link validation: No valid OAuth session found.")
        return

    # Filter out entries tracking active scheduled assets
    videos_to_check = [
        v for v in manifest.get("videos", []) 
        if v.get("status") == "scheduled" and v.get("youtube_video_id")
    ]
    
    if not videos_to_check:
        print("[Reconciler] Manifest matrix synchronized. No active checks required.")
        return

    ids_string = ",".join([v["youtube_video_id"] for v in videos_to_check])
    
    try:
        request = youtube.videos().list(part="status,snippet", id=ids_string)
        response = request.execute()
        
        yt_statuses = {item["id"]: item for item in response.get("items", [])}
        
        for video in manifest["videos"]:
            v_id = video.get("youtube_video_id")
            if v_id in yt_statuses:
                yt_item = yt_statuses[v_id]
                yt_privacy = yt_item["status"].get("privacyStatus")
                
                # If YouTube flipped it to public, advance the ledger state automatically
                if yt_privacy == "public" and video["status"] == "scheduled":
                    video["status"] = "published"
                    video["published_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                    print(f"[Sync] Asset {v_id} successfully promoted to PUBLISHED status.")
                    
        with open(LEDGER_PATH, "w") as f:
            json.dump(manifest, f, indent=4)
            
    except Exception as e:
        print(f"[Reconciler Fault] Synchronization pause: {e}")

if __name__ == "__main__":
    reconcile_manifest_with_youtube()