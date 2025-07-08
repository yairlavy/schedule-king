import webbrowser, time, pickle, json, requests
from pathlib import Path
from google.oauth2.credentials import Credentials

# URL of your deployed Cloud Function
BROKER = "https://us-central1-schedule-king-463317.cloudfunctions.net/function-calendar"

# Path to store the token file
TOKEN = Path(__file__).parent.parent.parent / "token.pickle"

def fetch():
    try:
        # 1. Request an authentication URL from the broker
        print("Starting OAuth flow...")
        r = requests.post(f"{BROKER}/auth/start")
        r.raise_for_status()
        
        data = r.json()
        state = data["state"]
        
        print("Opening browser for authentication...")  # Opening browser for authentication
        webbrowser.open(data["auth_url"])

        # 2. Poll the broker until the token is ready
        print("Waiting for authorization...")
        while True:
            r = requests.get(f"{BROKER}/auth/token", params={"state": state})
            if r.status_code == 200:
                response_data = r.json()
                creds_json = response_data["token"]
                
                # Load credentials from the received JSON
                creds_dict = json.loads(creds_json)
                creds = Credentials.from_authorized_user_info(creds_dict)
                
                # Save credentials to a pickle file
                with open(TOKEN, "wb") as f:
                    pickle.dump(creds, f)
                    
                print(f"token.pickle created at {TOKEN} – you can now run the code normally")
                break
            elif r.status_code == 202:
                print("Still waiting for authorization...")
                time.sleep(2)
            else:
                print(f"Error: {r.status_code} - {r.text}")
                break
                
    except Exception as e:
        print(f"Error during OAuth flow: {e}")

if __name__ == "__main__":
    # If token does not exist, start authentication flow
    if not TOKEN.exists():
        fetch()
    else:
        print(f"token.pickle already exists at {TOKEN} – skipping authentication process")