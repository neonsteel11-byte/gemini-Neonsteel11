import os
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
CLIENT_SECRETS = "client_secret.json"

def main():
    if not os.path.exists(CLIENT_SECRETS):
        print("Place client_secret.json in the repo root.")
        return
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
    creds = flow.run_local_server(port=0)
    print("==== COPY THIS REFRESH TOKEN INTO GITHUB SECRET: YT_REFRESH_TOKEN ====")
    print(creds.refresh_token)

if __name__ == '__main__':
    main()
