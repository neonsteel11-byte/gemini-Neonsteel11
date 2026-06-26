#!/usr/bin/env python3
import json
import os
from googleapiclient.discovery import build

def check_8_hour_traction():
    manifest_path = "output/manifest.json"
    if not os.path.exists(manifest_path):
        print("-> No manifest found to check.")
        return

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # For this real-time check, we can use a standard Developer API Key
    # because public view counts don't require private OAuth clearance.
    api_key = os.getenv("GEMINI_API_KEY") # Or your dedicated YouTube API Key
    if not api_key:
        print("-> Missing API Key in environment.")
        return

    youtube = build("youtube", "v3", developerKey=api_key)

    print("--- 8-Hour Real-Time Traction Report ---")
    for slot, data in manifest.items():
        video_id = data.get("video_id")
        if not video_id or video_id == "75jC4nKS6Gg": # Skip mock IDs
            continue
            
        try:
            request = youtube.videos().list(part="statistics,snippet", id=video_id)
            response = request.execute()
            
            if response["items"]:
                stats = response["items"][0]["statistics"]
                title = response["items"][0]["snippet"]["title"]
                print(f"\n📺 Video: {title}")
                print(f"   👀 Views:  {stats.get('viewCount', 0)}")
                print(f"   👍 Likes:  {stats.get('likeCount', 0)}")
                print(f"   💬 Comments: {stats.get('commentCount', 0)}")
            else:
                print(f"-> Video {video_id} not found or still private.")
        except Exception as e:
            print(f"-> Error checking video {video_id}: {e}")

if __name__ == "__main__":
    check_8_hour_traction()
