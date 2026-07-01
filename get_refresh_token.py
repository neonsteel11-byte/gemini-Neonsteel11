import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

def main():
    client_id = input("Enter your YT_CLIENT_ID: ").strip()
    client_secret = input("Enter your YT_CLIENT_SECRET: ").strip()
    
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    
    # Using the standard local server flow (which launches a browser window locally)
    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    
    print("\nStarting local authentication server...")
    print("A browser window should open automatically. If not, follow the link it provides.\n")
    
    # This automatically finds an open local port, handles the login, and captures the credentials
    credentials = flow.run_local_server(host='localhost', port=8080, prompt='consent')
    
    print("\n🚀 SUCCESS! Here is your permanent YT_REFRESH_TOKEN:\n")
    print(credentials.refresh_token)
    print("\nCopy the token above and update it inside your GitHub Secrets!")

if __name__ == "__main__":
    main()
