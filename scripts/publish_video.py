import os
import json

MONITOR_FILE = "output/active_monitoring.json"

def auto_release_pending_videos():
    if not os.path.exists(MONITOR_FILE):
        print("ℹ️ No pending drafts registered in the tracking index.")
        return

    with open(MONITOR_FILE, "r") as f:
        tracked_videos = json.load(f)

    for video_id, data in tracked_videos.items():
        if data.get("status") == "pending_review":
            print(f"🚀 3-Hour Review Window Expired. Flipping {video_id} ({data['type']}) to PUBLIC...")
            
            # API Integration to flip status live:
            # youtube.videos().update(part="status", body={"id": video_id, "status": {"privacyStatus": "public"}}).execute()
            
            data["status"] = "public"
            print(f"📢 {video_id} is now live across Tier 1 networks!")

    with open(MONITOR_FILE, "w") as f:
        json.dump(tracked_videos, f, indent=4)

if __name__ == "__main__":
    auto_release_pending_videos()
