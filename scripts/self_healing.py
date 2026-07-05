import os
import json
import requests
from google import genai

LEDGER_FILE = "output/syndicate_ledger.json"

def load_syndicate_ledger():
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)
    return {"uploaded_videos": []}

def save_syndicate_ledger(data):
    os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
    with open(LEDGER_FILE, "w") as f:
        json.dump(data, f, indent=4)

def check_and_heal_underperforming_videos(access_token):
    print("🩺 [Self-Healing Safeguard]: Scanning Syndicate Ledger for video performance benchmarks...")
    ledger = load_syndicate_ledger()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    ai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    updated_videos = []
    for video in ledger["uploaded_videos"]:
        video_id = video.get("id")
        # Request performance statistics directly from YouTube Video Dashboard Endpoint
        url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_id}"
        
        try:
            res = requests.get(url, headers=headers).json()
            if "items" in res and len(res["items"]) > 0:
                stats = res["items"][0]["statistics"]
                snippet = res["items"][0]["snippet"]
                views = int(stats.get("viewCount", 0))
                
                print(f"📊 Video ID {video_id} currently has {views} views.")
                
                # Performance Safeguard Threshold: If views are low after indexing period
                if views < 100 and not video.get("healed", False):
                    print(f"⚠️ Performance drop detected for Video ID {video_id}! Triggering AI emergency metadata optimization...")
                    
                    # Call Gemini to construct a hyper-viral high-CTR alternate title
                    prompt = f"The YouTube title '{snippet['title']}' is underperforming. Generate a viral, highly clickable finance hook title replacing it. Return ONLY the title line."
                    response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    new_title = response.text.strip().replace('"', '')
                    
                    # Update snippet data structures
                    snippet["title"] = new_title
                    update_url = "https://www.googleapis.com/youtube/v3/videos?part=snippet"
                    update_payload = {"id": video_id, "snippet": snippet}
                    
                    update_res = requests.put(update_url, headers=headers, json=update_payload)
                    if update_res.status_code == 200:
                        print(f"✅ Auto-Optimized: Video ID {video_id} title successfully updated to: '{new_title}'")
                        video["healed"] = True
                        video["optimized_title"] = new_title
            
            updated_videos.append(video)
        except Exception as e:
            print(f"⚠️ Could not complete check for video {video_id}: {str(e)}")
            updated_videos.append(video)

    ledger["uploaded_videos"] = updated_videos
    save_syndicate_ledger(ledger)

def log_new_production_upload(video_id, title, topic):
    ledger = load_syndicate_ledger()
    ledger["uploaded_videos"].append({
        "id": video_id,
        "title": title,
        "topic": topic,
        "healed": False
    })
    save_syndicate_ledger(ledger)
