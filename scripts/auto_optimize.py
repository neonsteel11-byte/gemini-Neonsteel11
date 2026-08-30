"""
Fully automatic optimizer for underperforming videos (<1000 views).
Uses existing OAuth refresh token to update titles, descriptions, and thumbnails.
"""
import os
import sys
import json
import requests
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

MANIFEST_PATH = "video_manifest.json"
OUTPUT_DIR = "output"

def get_youtube_client():
    """Build YouTube API client using existing refresh token (no browser needed)."""
    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")
    refresh_token = os.getenv("YT_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        print("FATAL: Missing YouTube OAuth secrets.", file=sys.stderr)
        sys.exit(1)
        
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    return build('youtube', 'v3', credentials=creds)

def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

def get_video_stats(youtube, video_id):
    """Fetch current view count."""
    try:
        response = youtube.videos().list(
            part="statistics",
            id=video_id
        ).execute()
        if response['items']:
            return int(response['items'][0]['statistics'].get('viewCount', 0))
    except HttpError as e:
        print(f"      [!] API Error fetching stats: {e}")
    return 0

def generate_new_title(old_title, company):
    """Use Groq to generate a high-CTR title."""
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return old_title
        
    prompt = f"""Generate ONE high-CTR YouTube title for a video about: {company}
Old title: {old_title}
Rules: Under 60 chars. Use curiosity gaps, specific numbers, or contradictions. 
Example: "The $0 Mistake That Became a Billion-Dollar Industry"
Return ONLY the title text, no quotes, no explanations."""

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={
                "model": "openai/gpt-oss-120b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8
            },
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip().strip('"')
    except:
        pass
    return old_title

def generate_new_thumbnail(company, output_path):
    """Generate a new high-CTR thumbnail."""
    prompt = f"extreme close-up cartoon face with MOUTH WIDE OPEN in shock, eyes popping out, exaggerated surprised expression, holding or looking at {company}, flat vector cartoon illustration, bold black outlines, bright RED and YELLOW background for maximum CTR, professional YouTube thumbnail style, no text, no logos"
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1280&height=720&nologo=true&model=flux&enhance=true&seed=999"
    
    try:
        resp = requests.get(url, timeout=90)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(resp.content)
            return True
    except:
        pass
    return False

def optimize_video(youtube, video_data):
    video_id = video_data.get("video_id")
    company = video_data.get("company", "Unknown")
    old_title = video_data.get("title_variants", [""])[0] if video_data.get("title_variants") else ""
    
    print(f"\n{'='*50}")
    print(f"Checking: {company} ({video_id})")
    
    # 1. Check views
    views = get_video_stats(youtube, video_id)
    print(f"Current views: {views}")
    
    if views >= 1000:
        print("✓ Has 1000+ views. Skipping.")
        video_data["auto_optimized"] = True
        return False
        
    print("→ Under 1000 views. Optimizing...")
    
    # 2. Generate new title
    new_title = generate_new_title(old_title, company)
    print(f"New title: {new_title}")
    
    # 3. Update Video Metadata (Title & Description)
    try:
        youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": {
                    "title": new_title,
                    "description": video_data.get("description", "Accidental Genius -- the wild stories behind history's most brilliant mistakes.")
                }
            }
        ).execute()
        print("✓ Title updated on YouTube.")
    except HttpError as e:
        print(f"  [!] Failed to update title: {e}")
        return False

    # 4. Generate and Upload New Thumbnail
    thumb_path = os.path.join(OUTPUT_DIR, f"thumb_{video_id}.jpg")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if generate_new_thumbnail(company, thumb_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=thumb_path
            ).execute()
            print("✓ New thumbnail uploaded to YouTube.")
        except HttpError as e:
            print(f"  [!] Failed to upload thumbnail: {e}")
            
        # Cleanup
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

    # 5. Mark as optimized
    video_data["auto_optimized"] = True
    video_data["optimized_at"] = datetime.now().isoformat()
    video_data["optimized_title"] = new_title
    return True

def main():
    print("🚀 Starting Auto-Optimization...")
    youtube = get_youtube_client()
    manifest = load_manifest()
    
    optimized_count = 0
    for video_data in manifest:
        if not video_data.get("auto_optimized", False):
            if optimize_video(youtube, video_data):
                optimized_count += 1
                
    save_manifest(manifest)
    print(f"\n✅ Optimization complete! Updated {optimized_count} videos.")

if __name__ == "__main__":
    main()
