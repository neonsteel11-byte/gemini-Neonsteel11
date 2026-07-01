import time
import sys
import os
import json

HISTORY_FILE = "output/published_history.json"
MONITOR_FILE = "output/active_monitoring.json"

def is_duplicate_topic(company_name):
    if not os.path.exists(HISTORY_FILE):
        return False
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    return company_name.lower() in [item.lower() for item in history]

def log_published_topic(company_name, video_id, video_type):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    history.append(company_name)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
        
    monitored = {}
    if os.path.exists(MONITOR_FILE):
        with open(MONITOR_FILE, "r") as f:
            monitored = json.load(f)
    # Stash as pending so the secondary workflow knows what to release to public
    monitored[video_id] = {
        "company": company_name, 
        "type": video_type, 
        "uploaded_at": time.time(), 
        "status": "pending_review",
        "pivots": 0
    }
    with open(MONITOR_FILE, "w") as f:
        json.dump(monitored, f, indent=4)

def run_daily_production_suite(video_type="short", max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🎬 Initializing {video_type.upper()} Production (Attempt {attempt}/{max_retries})...")
            target_company = "Apple" 
            
            if is_duplicate_topic(target_company):
                print("🛑 Duplicate content filter triggered. Skipping topic.")
                return True
                
            # Render engine compiles cartoon vector assets here...
            
            # STAGE 1: Force upload as 'unlisted' to establish your 3-hour preview cushion
            mock_video_id = f"yt_{video_type}_{int(time.time())}"
            
            log_published_topic(target_company, mock_video_id, video_type)
            print(f"✅ Securely uploaded {video_type.upper()} as Unlisted Draft. ID: {mock_video_id}")
            return True
            
        except Exception as e:
            print(f"⚠️ Remediation triggered: {str(e)}")
            time.sleep(10 * attempt)
            if attempt == max_retries:
                sys.exit(1)

if __name__ == "__main__":
    run_daily_production_suite(video_type="short")
    run_daily_production_suite(video_type="long")
