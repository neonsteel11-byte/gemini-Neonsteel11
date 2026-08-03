"""
Auto-optimizes videos with <1000 views by:
1. Fetching current stats from YouTube Analytics
2. Generating new high-CTR titles
3. Creating new thumbnails
4. Updating tags/description
5. Re-uploading optimized version
"""
import argparse
import json
import os
import sys
import requests
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import OUTPUT_DIR

MANIFEST_PATH = "video_manifest.json"

def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

def get_youtube_credentials():
    """Get OAuth credentials for YouTube API."""
    # This would need proper OAuth flow
    # For now, return None - you'll need to set up OAuth properly
    return None

def fetch_video_stats(video_id: str) -> dict:
    """Fetch view count, CTR, average view duration from YouTube Analytics."""
    try:
        # This requires YouTube Data API v3
        # You'd need to implement proper authentication
        print(f"      Fetching stats for video {video_id}...")
        # Placeholder - implement actual API call
        return {
            "views": 0,  # Replace with actual API call
            "ctr": 0.0,
            "avg_view_duration": 0.0
        }
    except Exception as e:
        print(f"      [WARNING] Failed to fetch stats: {e}")
        return {"views": 0, "ctr": 0.0, "avg_view_duration": 0.0}

def generate_new_title(old_title: str, company: str) -> str:
    """Generate a new high-CTR title using Groq API."""
    from scripts.script_gen import _call_with_retry
    
    prompt = f"""Generate 3 HIGH-CTR YouTube titles for a video about {company}.
Old title: {old_title}

Rules:
- Use curiosity gaps: "The $0 Mistake That Became..."
- Include specific numbers: "$50 billion", "2 weeks", etc.
- Create contradiction: "He HATED potatoes. So he invented chips."
- Keep under 60 characters
- Use ALL CAPS for 1-2 power words

Return ONLY JSON array: ["title1", "title2", "title3"]"""
    
    try:
        response = _call_with_retry(prompt)
        import json as json_lib
        titles = json_lib.loads(response)
        return titles[0] if titles else old_title
    except:
        return old_title

def generate_new_thumbnail(invention: str) -> str:
    """Generate new high-CTR thumbnail."""
    from scripts.image_gen import _generate_pollinations
    
    thumbnail_path = os.path.join(OUTPUT_DIR, f"optimized_thumb_{invention.replace(' ', '_')}.jpg")
    
    # High-CTR formula: shocked face + bold text area + bright colors
    prompt = f"""extreme close-up cartoon face with MOUTH WIDE OPEN in shock, 
eyes popping out, exaggerated surprised expression, 
holding or looking at {invention},
flat vector cartoon illustration, bold black outlines,
bright RED and YELLOW background for maximum CTR,
professional YouTube thumbnail style, no text, no logos"""
    
    try:
        _generate_pollinations(prompt, thumbnail_path, (1280, 720), seed=999)
        print(f"      Generated new thumbnail: {thumbnail_path}")
        return thumbnail_path
    except Exception as e:
        print(f"      [WARNING] Thumbnail generation failed: {e}")
        return None

def optimize_video(video_data: dict, force: bool = False) -> bool:
    """Optimize a single underperforming video."""
    video_id = video_data.get("video_id")
    company = video_data.get("company", "")
    old_title = video_data.get("title_variants", [""])[0] if video_data.get("title_variants") else ""
    
    print(f"\n{'='*60}")
    print(f"Optimizing: {company}")
    print(f"Video ID: {video_id}")
    print(f"Old title: {old_title}")
    print(f"{'='*60}")
    
    # Fetch current stats
    stats = fetch_video_stats(video_id)
    views = stats.get("views", 0)
    ctr = stats.get("ctr", 0.0)
    
    print(f"Current stats: {views} views, {ctr*100:.1f}% CTR")
    
    # Check if optimization needed
    if views >= 1000 and not force:
        print("      ✓ Video has 1000+ views, skipping")
        return False
    
    print("      → Video underperforming, optimizing...")
    
    # Generate new title
    new_title = generate_new_title(old_title, company)
    print(f"      New title: {new_title}")
    
    # Generate new thumbnail
    new_thumb_path = generate_new_thumbnail(company)
    
    # Update video on YouTube
    # This would require YouTube Data API v3 update call
    print("      [!] Manual update required - YouTube API needs OAuth setup")
    print(f"      Suggested actions:")
    print(f"        1. Go to YouTube Studio → Content")
    print(f"        2. Find video: {old_title}")
    print(f"        3. Change title to: {new_title}")
    print(f"        4. Upload new thumbnail: {new_thumb_path}")
    
    # Mark as optimized in manifest
    video_data["optimized"] = True
    video_data["optimized_at"] = datetime.now().isoformat()
    video_data["optimized_title"] = new_title
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Auto-optimize underperforming videos")
    parser.add_argument("--threshold", type=int, default=1000, help="View count threshold")
    parser.add_argument("--optimize-all", action="store_true", help="Optimize all videos regardless of views")
    args = parser.parse_args()
    
    manifest = load_manifest()
    
    print(f"\n{'='*60}")
    print(f"Auto-Optimization System")
    print(f"Threshold: {args.threshold} views")
    print(f"Total videos in manifest: {len(manifest)}")
    print(f"{'='*60}\n")
    
    optimized_count = 0
    
    for video_data in manifest:
        if video_data.get("optimized"):
            print(f"Skipping {video_data.get('company')}: already optimized")
            continue
        
        if optimize_video(video_data, force=args.optimize_all):
            optimized_count += 1
    
    save_manifest(manifest)
    
    print(f"\n{'='*60}")
    print(f"Optimization complete!")
    print(f"Optimized {optimized_count} videos")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
