"""
Run this ONCE locally (never in GitHub Actions) if you need a new
YT_REFRESH_TOKEN -- e.g. if your existing one stops working.

Usage:
  python3 scripts/get_refresh_token.py <client_id> <client_secret>

It opens a browser, you log into the YouTube channel you want to post to,
and it prints a refresh token. Save that as the YT_REFRESH_TOKEN secret.
"""
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/get_refresh_token.py <client_id> <client_secret>")
        sys.exit(1)

    client_id, client_secret = sys.argv[1], sys.argv[2]

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n--- SUCCESS ---")
    print("Save this as your YT_REFRESH_TOKEN secret:\n")
    print(creds.refresh_token)
