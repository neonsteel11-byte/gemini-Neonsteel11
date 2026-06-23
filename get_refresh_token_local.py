from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

if not os.path.exists("client_secret.json"):
    print("ERROR: Please download your client_secret.json from Google Cloud Console first!")
    print("Rename it to exactly 'client_secret.json' and place it in this folder.")
    exit(1)

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json",
    scopes=SCOPES,
)
creds = flow.run_local_server(port=0, prompt="consent")

print("\n================ SUCCESS ================")
print("Copy this exact value for YT_REFRESH_TOKEN:")
print(creds.refresh_token)
print("=========================================\n")

conf = json.load(open("client_secret.json"))
cfg = conf.get("installed") or conf.get("web")
print("VERIFY THESE MATCH GITHUB SECRETS:")
print("CLIENT_ID:", cfg.get("client_id"))
print("CLIENT_SECRET:", cfg.get("client_secret"))
