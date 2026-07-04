import os
import sys
import json
import random
import requests
from google import genai
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

HISTORY_FILE = "output/published_history.json"
COMPANY_POOL = ["Apple", "Tesla", "Google", "Amazon", "Microsoft", "Meta", "Netflix", "WeWork", "Enron"]

# Initialize Gemini Client
ai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_authenticated_youtube_client():
    """Bypasses strict library validations and requests a raw access token directly from Google."""
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
        print("🔄 Requesting direct access token bypass payload from Google OAuth...")
        response = requests.post(token_url, data=payload)
        response_data = response.json()

        if "access_token" in response_data:
            creds = Credentials(token=response_data["access_token"])
            return googleapiclient.discovery.build("youtube", "v3", credentials=creds)
        else:
            print(f"⚠️ Direct swap payload error fallback: {response_data}")
            creds = Credentials(token=refresh_token)
            return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    except Exception as e:
        print(f"❌ Custom Auth Interceptor Failed: {str(e)}")
        sys.exit(1)

class HumanDirectorSuite:
    def generate_highly_monetizable_script(self, company_name, video_type):
        print(f"🪝 [Director]: Constructing high-retention script via gemini-2.5-flash for {video_type.upper()}...")
        prompt = f"Write a short, engaging YouTube script roasting {company_name} for a {video_type}."
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()

def upload_to_youtube_studio(file_path, title, description):
    try:
        youtube = get_authenticated_youtube_client()
    except Exception as auth_err:
        print(f"❌ AUTHENTICATION FAILED: {str(auth_err)}")
        return None

    if not os.path.exists(file_path):
        print(f"⚠️ Video file {file_path} not found. Ensure rendering framework has compiled the MP4 asset.")
        return None

    body = {
        "snippet": {"title": title, "description": description, "categoryId": "27"},
        "status": {"privacyStatus": "unlisted"}
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    print(f"🚀 Broadcasting binary frames to live channel servers for: '{title}'...")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📦 Streaming Data Block: {int(status.progress() * 100)}% pushed...")

    print(f"✅ Live Verification: Asset is officially uploaded! Video ID: {response['id']}")
    return response["id"]

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
