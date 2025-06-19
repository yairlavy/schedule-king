from src.services.google_authenticatior import authenticate_google_account, verify_credentials, force_reauthentication
from googleapiclient.discovery import build
import datetime

class GoogleCalendarManager:
    """Manager for Google Calendar operations."""

    def __init__(self):
        """Initialize the Google Calendar Manager."""
        self.creds = authenticate_google_account()
        
        # If credentials verification fails, try to force re-authentication
        if not verify_credentials(self.creds):
            print("Initial authentication failed. Attempting to re-authenticate with proper scopes...")
            # Delete the old token and try again
            if force_reauthentication():
                self.creds = authenticate_google_account()
                if not verify_credentials(self.creds):
                    raise Exception("Failed to authenticate with Google account after re-authentication attempt.")
            else:
                raise Exception("Failed to authenticate with Google account.")

        # Build the Google Calendar service
        self.service = build('calendar', 'v3', credentials=self.creds)

    def create_event(self, summary, description, start_time, end_time, timezone='Asia/Jerusalem'):
        """
        Create a new event in the user's primary Google Calendar.

        Args:
            summary (str): Title of the event.
            description (str): Description of the event.
            start_time (str): Event start time in RFC3339 format.
            end_time (str): Event end time in RFC3339 format.
            timezone (str): Timezone for the event (default is 'Asia/Jerusalem').

        Returns:
            dict or None: The created event resource if successful, None otherwise.
        """

        # Define the event details
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
        }

        try:
            # Insert the event into the primary calendar
            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {created_event.get('htmlLink')}")
            return created_event
        except Exception as e:
            # Handle errors during event creation
            print(f"Error creating event: {e}")
            return None

    def test_connection(self):
        """
        Test the connection to Google Calendar API.
        Returns True if successful, False otherwise.
        """
        try:
            # Try to get the primary calendar info
            calendar = self.service.calendars().get(calendarId='primary').execute()
            print(f"Successfully connected to calendar: {calendar.get('summary', 'Primary Calendar')}")
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False