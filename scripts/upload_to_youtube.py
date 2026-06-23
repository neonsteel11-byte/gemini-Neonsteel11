#!/usr/bin/env python3
import os, json, subprocess
from datetime import datetime

MANIFEST_PATH = "output/manifest.json"
STATE_PATH = "output/system_state.json"
TEST_MODE = os.environ.get("TEST_MODE", "true") == "true"

def check_safety():
    with open(STATE_PATH, "r") as f:
        state = json.load(f)
    
    # Reset logic: If date has changed, reset uploads_today to 0
    today = datetime.utcnow().strftime('%Y-%m-%d')
    if state.get("last_run_date") != today:
        print(f"-> New day detected ({today}). Resetting daily upload counter.")
        state["uploads_today"] = 0
        state["last_run_date"] = today
        # Save reset state immediately
        with open(STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)

    if state.get("paused", True):
        raise SystemExit("CRITICAL: Automation is PAUSED via system_state.json")
    if state.get("uploads_today", 0) >= state.get("max_daily_uploads", 2):
        raise SystemExit(f"CRITICAL: Daily upload cap ({state['max_daily_uploads']}) reached.")
    
    return state

def run_upload():
    state = check_safety()
    
    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    # Note: Ensure your existing Auth logic is called here
    print(f"-> Starting Upload (Test Mode: {TEST_MODE})")

    if TEST_MODE:
        video_id = "DRYRUN_TEST_ID"
        print("-> Dry run successful.")
    else:
        # REPLACE THIS WITH YOUR REAL UPLOAD LOGIC
        # video_id = youtube_service.videos().insert(...).execute().get("id")
        video_id = "REAL_YT_ID" 
        print(f"-> Video uploaded: {video_id}")

    # Update manifest
    manifest["status"] = "published"
    manifest["youtube_video_id"] = video_id
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    # Update state counter
    state["uploads_today"] += 1
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

    # Commit the changes so the repo remembers the new state
    subprocess.run(["git", "config", "user.name", "Syndicate Bot"], check=True)
    subprocess.run(["git", "config", "user.email", "bot@syndicate.local"], check=True)
    subprocess.run(["git", "add", MANIFEST_PATH, STATE_PATH], check=True)
    subprocess.run(["git", "commit", "-m", "chore: update ledger and state [skip ci]"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)

    print(f"-> Process complete.")

if __name__ == "__main__":
    run_upload()