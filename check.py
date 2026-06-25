import os
import google.oauth2.credentials
import googleapiclient.discovery

creds = google.oauth2.credentials.Credentials(
    token=None,
    refresh_token="1//0gcNCsKSaTedDCgYIARAAGBASNwF-L9IrybDQVYYi6LTna8rgY6M1sPYMnLSxkvPPvdKS67VhjertFtq-qH9WbkAhbi9w7frqqDA",
    client_id="1040164377907-760hgodbtpsrovj519thcdajv2jsgjbr.apps.googleusercontent.com",
    client_secret="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",
    token_uri="https://oauth2.googleapis.com/token"
)
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

# Look at your manifest.json and swap 'REAL_YT_ID' with your actual video ID string (e.g., "dQw4w9WgXcQ")
VIDEO_ID = "1040164377907-760hgodbtpsrovj519thcdajv2jsgjbr.apps.googleusercontent.com" 

request = youtube.videos().list(part="snippet,status", id=VIDEO_ID)
response = request.execute()

if response["items"]:
    item = response["items"][0]
    print("\n=== YOUTUBE LIVE STATUS ===")
    print(f"Title:          {item['snippet']['title']}")
    print(f"Privacy Status: {item['status']['privacyStatus']}")
    print(f"Upload Status:  {item['status']['uploadStatus']}")
    print("===========================")
else:
    print(f"\n[!] Video ID '{VIDEO_ID}' not found on YouTube. Check if the ID matches your manifest.")