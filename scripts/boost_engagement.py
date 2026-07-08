"""
For each uploaded video not yet boosted: posts one genuine discussion-starting
comment, and adds the video to a themed playlist (helps discovery via
autoplay/session watch time). Runs once per video, not repeatedly --
spamming comments/playlist adds would look manipulative and risk flags.
"""
import json
import os
import sys
import requests
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, GROQ_API_KEY, GROQ_MODEL

MANIFEST_PATH = "video_manifest.json"
PLAYLIST_STATE_PATH = "playlist_state.json"
PLAYLIST_TITLE = "Funny Finance Roasts"
MIN_AGE_HOURS = float(os.getenv("BOOST_AFTER_HOURS", "1"))

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _get_credentials():
    creds = Credentials(
        token=None, refresh_token=YT_REFRESH_TOKEN, token_uri=TOKEN_URI,
        client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET, scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def _generate_comment(company: str) -> str:
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Write ONE short, funny, genuine-sounding YouTube "
                                           "comment (under 20 words) as the channel owner, asking "
                                           "viewers a question to spark replies about the video's "
                                           "company. No hashtags, no links, no emojis spam."},
            {"role": "user", "content": f"The video is about {company}."}
        ],
        "temperature": 0.9,
    }
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          headers=headers, json=payload, timeout=30)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"].strip().strip('"')
    return "What do you think happens next with this one? 👀"


def _get_or_create_playlist(youtube) -> str:
    if os.path.exists(PLAYLIST_STATE_PATH):
        with open(PLAYLIST_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)["playlist_id"]

    body = {
        "snippet": {"title": PLAYLIST_TITLE,
                    "description": "All the funny finance roasts in one place."},
        "status": {"privacyStatus": "public"},
    }
    resp = youtube.playlists().insert(part="snippet,status", body=body).execute()
    playlist_id = resp["id"]
    with open(PLAYLIST_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump({"playlist_id": playlist_id}, f)
    return playlist_id


def main():
    if not os.path.exists(MANIFEST_PATH):
        print("No manifest found -- nothing to boost yet.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    youtube = build("youtube", "v3", credentials=_get_credentials())
    playlist_id = _get_or_create_playlist(youtube)
    now = datetime.now(timezone.utc)
    changed = False

    for entry in manifest:
        if entry.get("engagement_boosted"):
            continue

        uploaded_at = datetime.fromisoformat(entry["uploaded_at"])
        age_hours = (now - uploaded_at).total_seconds() / 3600
        if age_hours < MIN_AGE_HOURS:
            continue

        video_id = entry["video_id"]

        try:
            comment_text = _generate_comment(entry["company"])
            youtube.commentThreads().insert(
                part="snippet",
                body={"snippet": {"videoId": video_id,
                                   "topLevelComment": {"snippet": {"textOriginal": comment_text}}}}
            ).execute()
            print(f"      {video_id}: posted comment: \"{comment_text}\"")
        except Exception as e:
            print(f"      {video_id}: comment failed (comments may be disabled): {e}", file=sys.stderr)

        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={"snippet": {"playlistId": playlist_id,
                                   "resourceId": {"kind": "youtube#video", "videoId": video_id}}}
            ).execute()
            print(f"      {video_id}: added to playlist '{PLAYLIST_TITLE}'")
        except Exception as e:
            print(f"      {video_id}: playlist add failed: {e}", file=sys.stderr)

        entry["engagement_boosted"] = True
        changed = True

    if changed:
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print("Manifest updated.")
    else:
        print("Nothing to boost this run.")


if __name__ == "__main__":
    main()
