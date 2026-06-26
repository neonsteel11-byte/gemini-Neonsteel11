#!/usr/bin/env python3
import os
import sys
import json
import datetime
import subprocess
import time

def get_staggered_today_times():
    """
    Calculates separate release timestamps for TODAY.
    Long video: 5:00 PM local NPT (11:15 UTC)
    Short video: 7:00 PM local NPT (13:15 UTC)
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    # Base timestamp for today at 11:15 UTC (5:00 PM NPT)
    long_target = now_utc.replace(hour=11, minute=15, second=0, microsecond=0)
    # Base timestamp for today at 13:15 UTC (7:00 PM NPT)
    short_target = now_utc.replace(hour=13, minute=15, second=0, microsecond=0)
    
    # Self-healing safety cushion: If the targeted hour has already passed in UTC today,
    # push it exactly 15 minutes into the near future to ensure immediate processing.
    if now_utc >= long_target:
        long_target = now_utc + datetime.timedelta(minutes=15)
    if now_utc >= short_target:
        short_target = now_utc + datetime.timedelta(minutes=30)

    return long_target.strftime("%Y-%m-%dT%H:%M:%SZ"), short_target.strftime("%Y-%m-%dT%H:%M:%SZ")

def run_self_healing_git_checks():
    """Verifies repository cleanliness before launching synchronization pipeline."""
    print("-> [Self-Healing] Checking Git Workspace State...")
    try:
        status_output = subprocess.check_output(["git", "status"], stderr=subprocess.STDOUT).decode("utf-8")
        if "rebase in progress" in status_output or "AM in progress" in status_output:
            print("-> [Self-Healing Warning] Git tree is locked. Aborting synchronization.")
            return False
        return True
    except Exception as e:
        print(f"-> [Self-Healing Warning] Unable to confirm git status context: {e}")
        return False

def validate_manifest_schema(path):
    """Ensures file writes weren't interrupted and json integrity is fully intact."""
    if not os.path.exists(path):
        print(f"-> [Validation] Tracked manifest missing at '{path}'.")
        return False
    if os.path.getsize(path) == 0:
        print(f"-> [Validation Error] Truncated 0-byte error detected at '{path}'.")
        return False
    try:
        with open(path, "r") as f:
            json.load(f)
        return True
    except json.JSONDecodeError:
        print(f"-> [Validation Error] Malformed JSON sequence caught in '{path}'.")
        return False

def upload_mock_asset():
    print("-> Executing Hooked Upload Pipeline [STAGGERED TODAY SLOTS]")

    manifest_path = "output/manifest.json"
    headline = "Why Big Tech is Overrated"
    description = "Automated corporate comedy loop."

    if validate_manifest_schema(manifest_path):
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
                if "short_metadata" in data:
                    headline = data["short_metadata"].get("title", headline)
                    description = data["short_metadata"].get("description", description)
        except Exception as e:
            print(f"-> Metadata extraction bypassed: {e}")

    # Calculate both distinct times
    long_time_utc, short_time_utc = get_staggered_today_times()

    print(f"-> Title: {headline} 🤯")
    print(f"   🎬 Long Video Schedule: {long_time_utc} (~5:00 PM Local)")
    print(f"   📱 Short Video Schedule: {short_time_utc} (~7:00 PM Local)")

    mock_video_id = "75jC4nKS6Gg"
    print(f"-> Assets staged successfully! Video ID reference point: {mock_video_id}")

    if not run_self_healing_git_checks():
        print("-> Synchronization tracking skipped due to untrusted workspace state.")
        return

    max_retries = 3
    retry_delay = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
            subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)

            manifest_data = {}
            if os.path.exists(manifest_path) and os.path.getsize(manifest_path) > 0:
                try:
                    with open(manifest_path, "r") as f:
                        manifest_data = json.load(f)
                except Exception:
                    pass

            manifest_data["last_upload_sync_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            manifest_data["scheduled_time_long"] = long_time_utc
            manifest_data["scheduled_time_short"] = short_time_utc
            
            os.makedirs(os.path.dirname(manifest_path) if os.path.dirname(manifest_path) else "output", exist_ok=True)
            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f, indent=2)

            subprocess.run(["git", "add", "output/manifest.json"], check=True)
            subprocess.run(["git", "commit", "-m", "chore: stagger video drops for today [skip ci]"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("-> Synchronization tracking complete.")
            break
            
        except Exception as e:
            print(f"-> Synchronization tracking attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print("-> [Critical] Self-healing push recovery exhausted.")

if __name__ == "__main__":
    upload_mock_asset()
