#!/usr/bin/env python3
import os, json, subprocess, smtplib
from email.message import EmailMessage

MANIFEST_PATH = "output/manifest.json"
STATE_PATH = "output/system_state.json"
TEST_MODE = os.environ.get("TEST_MODE", "true") == "true"

def check_safety():
    with open(STATE_PATH, "r") as f:
        state = json.load(f)
    if state.get("paused", True):
        raise SystemExit("CRITICAL: Automation is PAUSED via system_state.json")
    if state.get("uploads_today", 0) >= state.get("max_daily_uploads", 2):
        raise SystemExit("CRITICAL: Daily upload cap reached.")
    return state

def run_upload():
    state = check_safety()
    
    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    # ... [Insert your existing Google API Authentication here] ...

    if TEST_MODE:
        video_id = "DRYRUN_TEST_ID"
    else:
        # ... [Insert your existing upload logic here] ...
        # video_id = response.get("id")
        video_id = "REAL_YT_ID"

    # Update manifest
    manifest["status"] = "published"
    manifest["youtube_video_id"] = video_id
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    # Update state counter
    state["uploads_today"] += 1
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

    # Commit with [skip ci]
    subprocess.run(["git", "config", "user.name", "Syndicate Bot"])
    subprocess.run(["git", "config", "user.email", "bot@syndicate.local"])
    subprocess.run(["git", "add", MANIFEST_PATH, STATE_PATH])
    subprocess.run(["git", "commit", "-m", "chore: update ledger and state [skip ci]"])
    subprocess.run(["git", "push", "origin", "main"])

    print(f"-> Upload complete: {video_id}")

if __name__ == "__main__":
    run_upload()