from src.services.google_authenticatior import authenticate_google_account, verify_credentials
from googleapiclient.discovery import build
import datetime

class GoogleCalendarManager:
    """Manager for Google Calendar operations."""

    def __init__(self):
        """Initialize the Google Calendar Manager."""
        self.creds = authenticate_google_account()
        if not verify_credentials(self.creds):
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
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f"event created : {event.get('htmlLink')}")
            return event
        except Exception as e:
            # Handle errors during event creation
            print(f"error creating event: {e}")
            return None