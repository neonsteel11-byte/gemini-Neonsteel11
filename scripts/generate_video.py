import os
import sys
import json
import requests
from google import genai

HISTORY_FILE = "output/published_history.json"
COMPANY_POOL = ["Apple", "Tesla", "Google", "Amazon", "Microsoft", "Meta", "Netflix", "WeWork", "Enron"]

# Initialize Gemini Client for high-retention narration generation
ai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_live_access_token():
    """Fetches a pristine access token directly from Google OAuth without using strict library classes."""
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
        print("🔄 Exchanging permanent credentials via direct HTTP POST...")
        response = requests.post(token_url, data=payload)
        response_data = response.json()
        
        if "access_token" in response_data:
            return response_data["access_token"]
        else:
            print(f"⚠️ Google OAuth Response: {response_data}")
            # Ultimate fail-safe fallback to raw token pass-through
            return refresh_token
    except Exception as e:
        print(f"❌ Direct Authentication Pipeline Intercept Failed: {str(e)}")
        sys.exit(1)

class HumanDirectorSuite:
    def generate_highly_monetizable_script(self, company_name, video_type):
        print(f"🪝 [Director]: Constructing high-retention narration script for {video_type.upper()}...")
        prompt = (
            f"Write a highly engaging, fast-paced YouTube script roasting {company_name} for a {video_type}. "
            f"Make the narrator sound authentic, witty, and human. Do not include structural stage directions."
        )
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()

def upload_to_youtube_studio(file_path, title, description):
    access_token = get_live_access_token()
    
    if not os.path.exists(file_path):
        print(f"⚠️ Video asset file {file_path} not found. Skipping upload step.")
        return None

    # Video Metadata Manifest
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "27" # Education / Infotainment Category
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }

    print(f"🚀 Streaming binary frames directly to YouTube dashboard: '{title}'...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Direct multipart upload protocol bypassing validation libraries completely
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
            print(f"✅ Live Verification: Asset is officially uploaded! Video ID: {res_json['id']}")
            return res_json["id"]
        else:
            print(f"❌ YouTube upload failed: {res_json}")
            return None
    except Exception as e:
        print(f"❌ Upload Connection Error: {str(e)}")
        return None

def select_daily_topic():
    return COMPANY_POOL[0]

def execute_master_production():
    daily_topic = select_daily_topic()
    print(f"\n⚡ STARTING LIVE OAUTH FACTORY EXECUTION: {daily_topic.upper()} ⚡")
    
    director = HumanDirectorSuite()
    short_script = director.generate_highly_monetizable_script(daily_topic, "short")
    long_script = director.generate_highly_monetizable_script(daily_topic, "long")
    
    short_mp4 = f"output/{daily_topic.lower()}_short.mp4"
    long_mp4 = f"output/{daily_topic.lower()}_long.mp4"
    
    upload_to_youtube_studio(short_mp4, f"The Absolute Chaos of {daily_topic} #shorts", short_script[:200])
    upload_to_youtube_studio(long_mp4, f"How {daily_topic} Blinded Investors", long_script[:200])

if __name__ == "__main__":
    execute_master_production()
