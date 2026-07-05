import os
import sys

# 🩺 Path Guard: Force Python to recognize the root repository directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import requests
from datetime import datetime, timedelta
from google import genai
from google.genai.errors import ServerError
from scripts.self_healing import log_new_production_upload, check_and_heal_underperforming_videos

COMPANY_POOL = [
    "Apple", "Tesla", "Google", "Amazon", "Microsoft", "Meta", "Netflix", "WeWork", "Enron",
    "Nvidia", "Intel", "AMD", "Sony", "Nintendo", "Disney", "Uber", "Airbnb"
]

try:
    ai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception as e:
    print(f"❌ Failed to initialize Gemini Client: {str(e)}")
    sys.exit(1)

def get_live_access_token():
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    try:
        response = requests.post(token_url, data=payload)
        response_data = response.json()
        if "access_token" in response_data:
            return response_data["access_token"]
        return refresh_token
    except Exception as e:
        print(f"❌ Authentication Pipeline Failure: {str(e)}")
        sys.exit(1)

def upload_to_youtube_holding_tank(file_path, title, description, topic, publish_time_iso):
    access_token = get_live_access_token()
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(b"MOCK_PRODUCTION_STREAM")
            
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "23" 
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_time_iso
        }
    }

    print(f"🚀 Streaming binary frames to Holding Tank: '{title}' (Release Time: {publish_time_iso})...")
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {
        'snippet': (None, json.dumps(metadata), 'application/json'),
        'video': (os.path.basename(file_path), open(file_path, 'rb'), 'video/mp4')
    }
    
    try:
        response = requests.post(
            "https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status",
            headers=headers,
            files=files
        )
        res_json = response.json()
        if "id" in res_json:
            v_id = res_json["id"]
            print(f"✅ Securely staged in holding tank! Video ID: {v_id}")
            log_new_production_upload(v_id, title, topic)
            return v_id
        return None
    except Exception as e:
        print(f"❌ Holding Tank Ingest Error: {str(e)}")
        return None

def execute_master_production():
    access_token = get_live_access_token()
    
    check_and_heal_underperforming_videos(access_token)
    
    day_of_year = datetime.now().timetuple().tm_yday
    daily_topic = COMPANY_POOL[day_of_year % len(COMPANY_POOL)]
    print(f"\n⚡ STARTING 2X DAILY HOLDING TANK INGEST: {daily_topic.upper()} ⚡")
    
    base_time = datetime.utcnow()
    short_release_iso = (base_time + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    long_release_iso = (base_time + timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    short_mp4 = f"output/{daily_topic.lower()}_short.mp4"
    long_mp4 = f"output/{daily_topic.lower()}_long.mp4"
    
    upload_to_youtube_holding_tank(short_mp4, f"The Insane Reality of {daily_topic} #shorts", "Funny finance breakdown.", daily_topic, short_release_iso)
    upload_to_youtube_holding_tank(long_mp4, f"How {daily_topic} Fooled Everyone", "Deep corporate satire dive.", daily_topic, long_release_iso)

if __name__ == "__main__":
    execute_master_production()
