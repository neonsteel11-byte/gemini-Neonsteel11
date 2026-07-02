import time
import sys
import os
import json

HISTORY_FILE = "output/published_history.json"
MONITOR_FILE = "output/active_monitoring.json"

# The rotation deck of target companies
COMPANY_POOL = ["Apple", "Tesla", "Google", "Amazon", "Microsoft", "Meta", "Netflix"]

def select_daily_topic():
    """Selects one company for the day that hasn't been used yet."""
    if not os.path.exists(HISTORY_FILE):
        return COMPANY_POOL[0]
        
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
        
    # Find the first company that isn't in your history file
    for company in COMPANY_POOL:
        if company.lower() not in [item.lower() for item in history]:
            return company
            
    # Fallback if every single company in the pool has been used once
    print("🔄 All companies have been roasted! Resetting history tracking pool...")
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    return COMPANY_POOL[0]

def log_final_production(company_name, short_id, long_id):
    """Saves everything to history ONLY after BOTH videos successfully upload."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    # 1. Update Duplicate History File
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    history.append(company_name)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
        
    # 2. Update Active Monitor File for the 3-Hour Auto-Public Release
    monitored = {}
    if os.path.exists(MONITOR_FILE):
        with open(MONITOR_FILE, "r") as f:
            monitored = json.load(f)
            
    monitored[short_id] = {"company": company_name, "type": "short", "status": "pending_review"}
    monitored[long_id] = {"company": company_name, "type": "long", "status": "pending_review"}
    
    with open(MONITOR_FILE, "w") as f:
        json.dump(monitored, f, indent=4)

def run_synchronized_production():
    # Step 1: Pick the ONE topic for today's entire cycle
    daily_topic = select_daily_topic()
    print(f"🎯 TODAY'S COMBINED TARGET TOPIC: {daily_topic.upper()}")
    
    try:
        # Step 2: Render & Upload the SHORT Video
        print(f"🎬 [1/2] Generating SHORT for {daily_topic}...")
        # (Cartoon render processing here...)
        mock_short_id = f"yt_short_{int(time.time())}"
        print(f"✅ Short uploaded as Unlisted Draft: {mock_short_id}")
        
        # Step 3: Render & Upload the LONG Video (Using the exact same topic!)
        print(f"🎬 [2/2] Generating LONG-FORM for {daily_topic}...")
        # (Cartoon render processing here...)
        mock_long_id = f"yt_long_{int(time.time())}"
        print(f"✅ Long-form uploaded as Unlisted Draft: {mock_long_id}")
        
        # Step 4: Complete the cycle and lock it into the database
        log_final_production(daily_topic, mock_short_id, mock_long_id)
        print(f"🎉 Production suite completed successfully for {daily_topic}!")
        
    except Exception as e:
        print(f"⚠️ Production halted due to system error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_synchronized_production()
