import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.requests import Request
from googleapiclient.discovery import build

# Define scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.EVENTS']

@staticmethod
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
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        # If credentials are expired but have a refresh token, refresh them
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # If no valid credentials, start the OAuth flow
            path = os.path.join(os.path.dirname(__file__), '..', '..', 'credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(path, SCOPES)
            try:
                # Run the local server to complete authentication
                creds = flow.run_local_server(
                    port=0,
                    success_message='Authentication successful! You can close this window now.',
                    open_browser=True
                )
            except Exception as e:
                # Print error if authentication fails
                print(f"An error occurred during authentication: {e}")
                return None

        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    # Return the authenticated credentials
    return creds

@staticmethod
def verify_credentials(creds):
    """
    Verify if the credentials are valid.
    """
    if not creds:
        # Print error if credentials are missing
        print("Failed to authenticate with Google account.")
        return False

    try:
        # Build the Google Calendar API service
        service = build('calendar', 'v3', credentials=creds)
        # Attempt to fetch the calendar list to verify credentials
        service.calendarList().list().execute()
        return True
    except Exception as e:
        # Print error if verification fails
        print(f"An error occurred while verifying credentials: {e}")
        return False