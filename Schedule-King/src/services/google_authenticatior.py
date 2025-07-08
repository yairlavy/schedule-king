import os, pickle, json
from src.services.token_fetcher import fetch
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

TOKEN_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'token.pickle')
)

def verify_credentials(creds) -> bool:
    """Verify that credentials are valid by making a test API call."""
    try:
        service = build('calendar', 'v3', credentials=creds, cache_discovery=False)
        service.calendars().get(calendarId='primary').execute()
        return True
    except Exception as e:
        print(f"Credential verification failed: {e}")
        return False

def _load_creds_from_disk():
    """Load credentials from disk."""
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        with open(TOKEN_PATH, 'rb') as f:
            creds = pickle.load(f)
        if isinstance(creds, str):  # Support for old versions
            creds = Credentials.from_authorized_user_info(json.loads(creds), SCOPES)
        return creds
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def _save(creds):
    """Save credentials to disk."""
    try:
        with open(TOKEN_PATH, 'wb') as f:
            pickle.dump(creds, f)
    except Exception as e:
        print(f"Error saving credentials: {e}")

def force_reauthentication():
    """Force re-authentication by deleting the token file."""
    try:
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            print("Deleted old token file")
        return True
    except Exception as e:
        print(f"Error deleting token file: {e}")
        return False

def authenticate_google_account():
    """
    Return a valid Credentials object.
    Will automatically run token_fetcher if no valid token exists.
    """
    tried_fetch = False

    while True:
        creds = _load_creds_from_disk()

        # Refresh if needed
        if creds and not creds.valid and creds.refresh_token:
            try:
                creds.refresh(Request())
                _save(creds)
                print("Token refreshed successfully")
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None  # Force new authentication

        # Verify credentials
        if creds and verify_credentials(creds):
            return creds

        # No valid credentials available
        if tried_fetch:
            raise RuntimeError("Unable to obtain valid Google credentials.")
            
        print("No valid token found – running cloud fetch...")
        try:
            fetch()
            tried_fetch = True
        except ImportError:
            raise RuntimeError("token_fetcher module not found. Please ensure it's in the same directory.")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch token: {e}")