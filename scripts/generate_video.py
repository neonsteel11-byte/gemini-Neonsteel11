import os
import sys
import time
import json
import random
from datetime import datetime
import google.generativeai as genai
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# File Paths & Content Pools
HISTORY_FILE = "output/published_history.json"
MONITOR_FILE = "output/active_monitoring.json"
COMPANY_POOL = [
    "Apple", "Tesla", "Google", "Amazon", "Microsoft", "Meta", "Netflix",
    "WeWork", "Enron", "Blockbuster", "Theranos", "Yahoo", "Pets_Com",
    "Juicero", "Lehman_Brothers", "Nokia", "Kodak", "Xerox", "Blackberry", "Wirecard"
]

# Configure AI Models & API clients securely
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_youtube_client():
    """Initializes authentic live YouTube API client using repository environment keys."""
    api_service_name = "youtube"
    api_version = "v3"
    developer_key = os.environ.get("GEMINI_API_KEY") 
    return googleapiclient.discovery.build(api_service_name, api_version, developerKey=developer_key)

class HumanDirectorSuite:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_highly_monetizable_script(self, company_name, video_type):
        """Generates trend-jacked, high-retention content explicitly optimized to pass human evaluation."""
        print(f"🪝 [Director]: Crafting aggressive retention hook & formatting for {video_type.upper()}...")
        
        prompt = f"""
        You are an elite, cynical YouTube Director specializing in financial roasts. Write a high-retention script about {company_name}.
        
        CRITICAL ENGINE DIRECTIONS:
        1. Open with a shocking, high-drama, 5-second standalone statement. Do not greet the audience.
        2. Break the content into short, punchy, rhythmic sentences to maintain high viewer retention.
        3. Strictly BAN all robotic AI words like 'delve', 'testament', 'beacon', 'revolutionize', 'moreover', or 'in conclusion'.
        4. Tone must be deadpan, deeply engaging, and highly sarcastic to optimize human engagement metrics.
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()

class UpgradingVisualEngine:
    def __init__(self):
        self.themes = [
            {"bg": "#0a0a16", "accent": "#39ff14", "text_primary": "#ffffff"},
            {"bg": "#1c0606", "accent": "#ff3333", "text_primary": "#ffff00"},
            {"bg": "#0f011a", "accent": "#00ffff", "text_primary": "#ffffff"}
        ]

    def build_visual_layout(self, company_name):
        """Calculates layered composition settings to prevent uniform platform duplication detection."""
        theme = random.choice(self.themes)
        print(f"🎨 [Visuals]: Structuring dynamic parallax layers and easing curves for {company_name} visuals.")
        return {
            "layout_style": random.choice(["comic_book_panel", "split_screen_diagonal", "framed_focus"]),
            "theme": theme,
            "blur_radius": 15,
            "motion_curve": "cubic-bezier(0.25, 1, 0.5, 1)"
        }

def upload_to_youtube_studio(file_path, title, description):
    """Streams actual physical file binary directly into your channel dashboard."""
    youtube = get_youtube_client()
    
    if not os.path.exists(file_path):
        print(f"⚠️ Video file {file_path} not found. Ensure rendering framework has compiled the MP4 asset.")
        return None

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["finance", "business", "history", "funny", "roast"],
            "categoryId": "27" # Education/Infotainment category
        },
        "status": {
            "privacyStatus": "unlisted" # Staged as unlisted for your automatic 3-hour publishing window
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    print(f"🚀 [API]: Broadcasting binary frames to live channel servers for: '{title}'...")
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
    print(f"\n⚡ STARTING LIVE FACTORY EXECUTION: {daily_topic.upper()} ⚡")
    
    director = HumanDirectorSuite()
    visual_engine = UpgradingVisualEngine()
    
    # 1. Human Polish Engine Execution
    short_script = director.generate_highly_monetizable_script(daily_topic, "short")
    long_script = director.generate_highly_monetizable_script(daily_topic, "long")
    
    # 2. Visual Layout Matrix Construction
    layout_config = visual_engine.build_visual_layout(daily_topic)
    
    # Target file paths generated by your rendering architecture
    short_mp4 = f"output/{daily_topic.lower()}_short.mp4"
    long_mp4 = f"output/{daily_topic.lower()}_long.mp4"
    
    try:
        # 3. Stream SHORTS payload to channel
        short_id = upload_to_youtube_studio(
            file_path=short_mp4,
            title=f"The Absolute Chaos of {daily_topic} #shorts",
            description=f"Quick corporate madness teardown.\n\nScript Summary:\n{short_script[:100]}..."
        )
        
        # 4. Stream LONG-FORM payload to channel (Synchronized on same topic!)
        long_id = upload_to_youtube_studio(
            file_path=long_mp4,
            title=f"How {daily_topic} Blinded Investors with Pure Chaos",
            description=f"Deep-dive analytical roast of corporate history.\n\nScript Summary:\n{long_script[:150]}..."
        )
        
        # 5. Lock into local file history system ONLY on successful API verification
        if short_id and long_id:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            history = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r") as f:
                    history = json.load(f)
            history.append(daily_topic)
            with open(HISTORY_FILE, "w") as f:
                json.dump(history, f, indent=4)
            print(f"\n🎉 SUCCESS: Automated pipeline ran perfectly. {daily_topic} is now safely logged.")
            
    except Exception as e:
        print(f"❌ SYSTEM FAILURE: Real production run crashed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    execute_master_production()
# Live Force Update Run
