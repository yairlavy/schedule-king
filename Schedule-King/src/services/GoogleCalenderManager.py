from src.services.google_authenticatior import authenticate_google_account, verify_credentials, force_reauthentication
from googleapiclient.discovery import build

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

    def create_academic_calendar(self, calendar_name="לוח זמנים אקדמי", description="לוח זמנים לקורסים אקדמיים"):
        """
        Create a new Google Calendar for academic events.
        
        Args:
            calendar_name (str): Name for the new calendar
            description (str): Description for the new calendar
            
        Returns:
            str: Calendar ID of the created calendar, or None if creation failed
        """
        calendar = {
            'summary': calendar_name,
            'description': description,
            'timeZone': 'Asia/Jerusalem'
        }
        
        try:
            created_calendar = self.service.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar['id']
            print(f"Created new calendar: {calendar_name} (ID: {calendar_id})")
            return calendar_id
        except Exception as e:
            print(f"Error creating calendar: {e}")
            return None

    def get_or_create_academic_calendar(self, calendar_name="לוח זמנים אקדמי"):
        """
        Get existing academic calendar or create a new one if it doesn't exist.
        
        Args:
            calendar_name (str): Name of the calendar to find or create
            
        Returns:
            str: Calendar ID of the academic calendar
        """
        try:
            # List all calendars to find existing academic calendar
            calendar_list = self.service.calendarList().list().execute()
            
            for calendar_item in calendar_list.get('items', []):
                if calendar_item.get('summary') == calendar_name:
                    print(f"Found existing calendar: {calendar_name} (ID: {calendar_item['id']})")
                    return calendar_item['id']
            
            # If not found, create a new one
            print(f"Calendar '{calendar_name}' not found. Creating new calendar...")
            return self.create_academic_calendar(calendar_name)
            
        except Exception as e:
            print(f"Error searching for calendar: {e}")
            return None

    def delete_calendar(self, calendar_id):
        """
        Delete a Google Calendar.
        
        Args:
            calendar_id (str): ID of the calendar to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.service.calendars().delete(calendarId=calendar_id).execute()
            print(f"Calendar with ID {calendar_id} deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting calendar: {e}")
            return False

    def create_event(self, summary, description, start_time, end_time, calendar_id='primary', color_id=None, timezone='Asia/Jerusalem'):
        """
        Create a new event in the specified Google Calendar.

        Args:
            summary (str): Title of the event.
            description (str): Description of the event.
            start_time (str): Event start time in RFC3339 format.
            end_time (str): Event end time in RFC3339 format.
            calendar_id (str): ID of the calendar to create the event in (default is 'primary').
            color_id (str, optional): Color ID for the event (see Google Calendar API color IDs).
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

        if color_id:
            event['colorId'] = color_id

        try:
            # Insert the event into the specified calendar
            created_event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Event created: {created_event.get('htmlLink')}")
            return created_event
        except Exception as e:
            # Handle errors during event creation
            print(f"Error creating event: {e}")
            return None
        

    def delete_event(self, event_id, calendar_id='primary'):
        """
        Delete an event from the specified Google Calendar.

        Args:
            event_id (str): The ID of the event to delete.
            calendar_id (str): ID of the calendar containing the event (default is 'primary').

        Returns:
            bool: True if the event was deleted successfully, False otherwise.
        """
        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            print(f"Event with ID {event_id} deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
        

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