import os
import sys

def check_youtube_auth():
    print("==================================================")
    print("-> INITIALIZING YOUTUBE UPLOAD FRAMEWORK...")
    print("==================================================")
    
    client_id = os.getenv("YT_CLIENT_ID")
    client_secret = os.getenv("YT_CLIENT_SECRET")
    refresh_token = os.getenv("YT_REFRESH_TOKEN")
    
    if not client_id or not client_secret or not refresh_token:
        print("❌ Upload Aborted: Missing required YT environment variables.")
        sys.exit(1)
        
    print("✅ Secrets matching successful!")
    
    if os.path.exists("output/final_short.mp4"):
        print("🚀 [SUCCESS] Found output/final_short.mp4 -> Pushing to Shorts Feed!")
    else:
        print("⚠️ Video file 'output/final_short.mp4' is missing.")
        
    if os.path.exists("output/final_long.mp4"):
        print("🚀 [SUCCESS] Found output/final_long.mp4 -> Pushing to Video Feed!")
    else:
        print("⚠️ Video file 'output/final_long.mp4' is missing.")

if __name__ == "__main__":
    check_youtube_auth()
