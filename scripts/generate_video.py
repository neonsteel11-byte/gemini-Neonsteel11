import os
import sys
import json
import random
from datetime import datetime
from google import genai
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

HISTORY_FILE = "output/published_history.json"
COMPANY_POOL = [
    "Apple", "Tesla", "Google", "Amazon", "Microsoft", "Meta", "Netflix",
    "WeWork", "Enron", "Blockbuster", "Theranos", "Yahoo"
]

# Initialize modern GenAI client using the correct environment variable
ai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_authenticated_youtube_client():
    """Authenticates using your authentic YT OAuth tokens from your GitHub Secrets."""
    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("❌ CRITICAL ERROR: Missing YT_CLIENT_ID, YT_CLIENT_SECRET, or YT_REFRESH_TOKEN in environment variables.")
        sys.exit(1)

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )

    if not creds.valid:
        print("🔄 Refreshing YouTube OAuth Access Token...")
        creds.refresh(Request())

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

class HumanDirectorSuite:
    def generate_highly_monetizable_script(self, company_name, video_type):
        """Generates high-retention content using the fast, modern gemini-2.5-flash model."""
        print(f"🪝 [Director]: Constructing high-retention script via gemini-2.5-flash for {video_type.upper()}...")
        
        prompt = f"Write a high-retention, engaging YouTube script roasting {company_name} for a {video_type}. Make the opening sentence incredibly hooking. Do not include structural notes or robotic AI words like 'delve' or 'testament'."
        
        # Switched to the modern client syntax and standard production model
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()

def upload_to_youtube_studio(file_path, title, description):
    """Streams actual physical file binary directly into your channel dashboard using OAuth."""
    try:
        youtube = get_authenticated_youtube_client()
    except Exception as auth_err:
        print(f"❌ AUTHENTICATION FAILED: Check your secret tokens. Details: {str(auth_err)}")
        return None
    
    if not os.path.exists(file_path):
        print(f"⚠️ Video file {file_path} not found. Ensure rendering framework has compiled the MP4 asset.")
        return None

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["finance", "business", "history", "funny"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "unlisted"
        }
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
    if not os.path.exists(HISTORY_FILE):
        return COMPANY_POOL[0]
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    for company in COMPANY_POOL:
        if company.lower() not in [item.lower() for item in history]:
            return company
    return COMPANY_POOL[0]

def execute_master_production():
    daily_topic = select_daily_topic()
    print(f"\n⚡ STARTING LIVE OAUTH FACTORY EXECUTION: {daily_topic.upper()} ⚡")
    
    director = HumanDirectorSuite()
    short_script = director.generate_highly_monetizable_script(daily_topic, "short")
    long_script = director.generate_highly_monetizable_script(daily_topic, "long")
    
    short_mp4 = f"output/{daily_topic.lower()}_short.mp4"
    long_mp4 = f"output/{daily_topic.lower()}_long.mp4"
    
    short_id = upload_to_youtube_studio(short_mp4, f"The Absolute Chaos of {daily_topic} #shorts", short_script[:200])
    long_id = upload_to_youtube_studio(long_mp4, f"How {daily_topic} Blinded Investors with Pure Chaos", long_script[:200])
    
    if short_id and long_id:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        history.append(daily_topic)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
        print(f"\n🎉 SUCCESS: Both formats logged via modern verified SDK pipeline.")

if __name__ == "__main__":
    execute_master_production()
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
