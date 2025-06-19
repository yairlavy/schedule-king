import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define scopes for Google Calendar API - Updated to include calendar read access
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def authenticate_google_account():
    """
    Authenticate the user with Google account and return the credentials.
    """
    creds = None
    # Construct the path to the token.pickle file (stores user's access and refresh tokens)
    token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'token.pickle')
    token_path = os.path.abspath(token_path)
    
    # Check if the token.pickle file exists (previous authentication)
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)  # Load existing credentials

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        # If credentials are expired but have a refresh token, refresh them
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # Attempt to refresh credentials
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                # If refresh fails, delete the old token and re-authenticate
                if os.path.exists(token_path):
                    os.remove(token_path)
                creds = None
        
        # If no valid credentials or refresh failed, start the OAuth flow
        if not creds or not creds.valid:
            path = os.path.join(os.path.dirname(__file__), '..', '..', 'credentials.json')
            if not os.path.exists(path):
                print(f"credentials.json not found at {path}")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(path, SCOPES)
            try:
                # Run the local server to complete authentication
                try:
                    creds = flow.run_local_server(
                        port=0,
                        success_message='Authentication successful! You can close this window now.',
                        open_browser=True
                    )
                except Exception as local_server_error:
                    print(f"Local server authentication failed: {local_server_error}")
                    print("Trying console-based authentication...")
                    # Fallback to console-based authentication
                    creds = flow.run_console()
            except Exception as e:
                # Print error if authentication fails
                print(f"An error occurred during authentication: {e}")
                return None

        # Save the credentials for the next run
        try:
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)  # Save credentials to file
        except Exception as e:
            print(f"Failed to save credentials: {e}")

    # Return the authenticated credentials
    return creds

def verify_credentials(creds):
    """
    Verify if the credentials are valid by making a simple API call.
    """
    if not creds:
        # Print error if credentials are missing
        print("Failed to authenticate with Google account.")
        return False

    try:
        # Build the Google Calendar API service
        service = build('calendar', 'v3', credentials=creds)
        # Instead of fetching calendar list, just try to get the primary calendar
        # This is a simpler call that requires fewer permissions
        service.calendars().get(calendarId='primary').execute()
        return True
    except Exception as e:
        # Print error if verification fails
        print(f"An error occurred while verifying credentials: {e}")
        return False

def force_reauthentication():
    """
    Force re-authentication by deleting the existing token.
    Call this function if you need to re-authenticate with new scopes.
    """
    token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'token.pickle')
    token_path = os.path.abspath(token_path)
    
    if os.path.exists(token_path):
        try:
            os.remove(token_path)  # Delete the token file to force re-authentication
            print("Token file deleted. Next authentication will request new permissions.")
            return True
        except Exception as e:
            print(f"Failed to delete token file: {e}")
            return False
    else:
        print("No token file found.")
        return True