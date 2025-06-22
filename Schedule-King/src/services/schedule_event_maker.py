from src.services.GoogleCalenderManager import GoogleCalendarManager
from src.models.schedule import Schedule
from datetime import datetime, timedelta
from src.services.academic_calender_parser import get_full_academic_year  # Import function to read academic year data

# Map day numbers (1-7) to Python's weekday numbers
# Python uses datetime.weekday() where 0=Monday, 1=Tuesday, etc.
# Our code uses 1=Sunday, 2=Monday, etc.
# Therefore we need o convert: 1 (Sunday) -> 6 (Sunday in Python), 2 (Monday) -> 0 (Monday in Python), etc.
day_mapping_for_weekday = {
    "1": 6,  # Sunday
    "2": 0,  # Monday
    "3": 1,  # Tuesday
    "4": 2,  # Wednesday
    "5": 3,  # Thursday
    "6": 4,  # Friday
    "7": 5   # Saturday
}   

# Define color mapping for different lesson types
# Google Calendar limits colors to a fixed set of predefined options
# Each lesson type gets a different color to distinguish them in the calendar
slot_type_colors = {
    "Lecture": "9",    # Light blue for lectures
    "Tirgul": "5",     # Orange/yellow for tutorials
    "Maabada": "10",   # Light green for labs
    "holiday": "11"    # Red for holidays
}

class ScheduleEventMaker:
    """
    Handles creation and deletion of Google Calendar events for academic schedules.
    This class manages holidays, semester boundaries, and prevents lesson conflicts during holidays.
    
    Key features:
    - Creates recurring weekly events for lessons
    - Creates multi-day holiday events
    - Prevents conflicts between lessons and holidays
    - Deletes all semester events
    - Creates and manages a dedicated academic calendar
    """

    def __init__(self, calendar_name="לוח זמנים אקדמי"):
        """
        Initialize the ScheduleEventMaker - creates Google Calendar connection and loads academic year data.
        
        Args:
            calendar_name (str): Name for the academic calendar
        
        Loads:
        - Google Calendar manager for performing calendar operations
        - Academic year data (semesters and holidays) from the parser
        - Creates or finds the academic calendar
        
        Raises:
            Exception: If there's an issue initializing the Google Calendar connection
        """
        try:
            self.calendar_manager = GoogleCalendarManager()
            # Load academic year data including holidays and semesters
            self.academic_data = get_full_academic_year()
            # Get or create the academic calendar
            self.academic_calendar_id = self.calendar_manager.get_or_create_academic_calendar(calendar_name)
            if not self.academic_calendar_id:
                raise Exception("Failed to create or find academic calendar")
            print(f"Using academic calendar ID: {self.academic_calendar_id}")
        except Exception as e:
            raise

    def _get_current_semester(self):
        """
        Determine which semester we're currently in based on today's date.
        
        Iterates through all semesters in the academic data and checks if today's date
        falls within any semester's start and end dates.
        
        Returns:
            dict: The current semester dictionary containing start/end dates and name,
                  or None if not currently in any semester period
        """
        today = datetime.now().date()
        # Loop through all semesters to find the one containing today's date
        for semester in self.academic_data['semesters']:
            semester_start = semester['start'].date()
            semester_end = semester['end'].date()
            if semester_start <= today <= semester_end:
                return semester
        return None

    def _is_holiday_date(self, check_date):
        """
        Check if a given date falls within any holiday period.
        
        Args:
            check_date (datetime.date or datetime.datetime): The date to check
            
        Returns:
            dict: The holiday dictionary if the date is within a holiday period,
                  None otherwise
        """
        # Convert datetime to date if necessary
        check_date = check_date.date() if isinstance(check_date, datetime) else check_date
        # Loop through all holidays to see if the date falls within any holiday range
        for holiday in self.academic_data['holidays']:
            holiday_start = holiday['start'].date()
            holiday_end = holiday['end'].date()
            if holiday_start <= check_date <= holiday_end:
                return holiday
        return None

    def _get_all_holiday_dates_in_semester(self, semester):
        """
        Get all dates that are holidays within the given semester.
        This is used to create exclusion dates for regular lesson events.
        
        Args:
            semester (dict): Semester dictionary containing start and end dates
            
        Returns:
            set: A set of dates that should be excluded from regular events
                 because they fall during holidays
        """
        semester_start = semester['start'].date()
        semester_end = semester['end'].date()
        holiday_dates = set()
        
        # Check each holiday to see if it overlaps with the semester
        for holiday in self.academic_data['holidays']:
            holiday_start = holiday['start'].date()
            holiday_end = holiday['end'].date()
            
            # Check if holiday overlaps with semester period
            if holiday_start <= semester_end and holiday_end >= semester_start:
                # Add all dates in the holiday period that are within the semester
                current_date = max(holiday_start, semester_start)
                end_date = min(holiday_end, semester_end)
                while current_date <= end_date:
                    holiday_dates.add(current_date)
                    current_date += timedelta(days=1)
        
        return holiday_dates

    def _create_holiday_event(self, holiday, semester_start, semester_end):
        """
        Create a single multi-day holiday event that spans the entire holiday period.
        This replaces the old approach of creating separate daily events for each holiday day.
        
        Args:
            holiday (dict): Holiday dictionary containing title, start, and end dates
            semester_start (datetime.date): Start date of the semester
            semester_end (datetime.date): End date of the semester
            
        Returns:
            dict: The created Google Calendar event, or None if creation failed
        """
        holiday_start = holiday['start'].date()
        holiday_end = holiday['end'].date()
        
        # Calculate the actual start and end dates within the semester bounds
        # This ensures we only create events for the part of the holiday that overlaps with the semester
        actual_start = max(holiday_start, semester_start)
        actual_end = min(holiday_end, semester_end)
        
        # Create multi-day all-day event
        # Note: Google Calendar end date is exclusive, so we add 1 day
        event = {
            'summary': holiday['title'],
            'start': {
                'date': actual_start.isoformat(),
                'timeZone': 'Asia/Jerusalem',
            },
            'end': {
                'date': (actual_end + timedelta(days=1)).isoformat(),  # End date is exclusive in Google Calendar
                'timeZone': 'Asia/Jerusalem',
            },
            'colorId': slot_type_colors['holiday']  # Red color for holidays
        }
        
        # Insert the event into the academic calendar
        try:
            created_event = self.calendar_manager.service.events().insert(
                calendarId=self.academic_calendar_id, 
                body=event
            ).execute()
            days_count = (actual_end - actual_start).days + 1
            print(f"Holiday event created: {holiday['title']} from {actual_start} to {actual_end} ({days_count} days)")
            return created_event
        except Exception as e:
            print(f"Error creating holiday event: {e}")
            return None

    def create_events(self, schedule: Schedule) -> bool:
        """
        Create recurring events for the schedule, respecting holidays and semester boundaries.
        This is the main function that orchestrates the entire event creation process.
        
        The process:
        1. Determine current semester
        2. Create holiday events (multi-day events)
        3. Create recurring lesson events with holiday exclusions
        4. Handle location and lecturer information
        
        Args:
            schedule (Schedule): The schedule object containing all lesson information
            
        Returns:
            bool: True if events were created successfully, False otherwise
        """
        # Step 1: Get current semester information
        current_semester = self._get_current_semester()
        if not current_semester:
            print("Not currently in any semester period. Cannot create events.")
            return False

        print(f"Creating events for {current_semester['name']} in academic calendar")
        
        # Step 2: Extract lessons organized by day of week
        daily_slots = schedule.extract_by_day()

        # Get semester boundaries for event creation
        semester_start = current_semester['start'].date()
        semester_end = current_semester['end'].date()

        # Step 3: Create holiday events first (one event per holiday covering multiple days)
        # This ensures holidays appear in the calendar before we create lesson events
        created_holidays = set()
        for holiday in self.academic_data['holidays']:
            holiday_start = holiday['start'].date()
            holiday_end = holiday['end'].date()
            # Check if holiday overlaps with current semester
            if holiday_start <= semester_end and holiday_end >= semester_start:
                # Prevent creating duplicate events for the same holiday
                if holiday['title'] not in created_holidays:
                    self._create_holiday_event(holiday, semester_start, semester_end)
                    created_holidays.add(holiday['title'])

        # Step 4: Get all holiday dates in the semester for exclusion from regular events
        # This prevents lesson events from being created on holiday dates
        holiday_dates = self._get_all_holiday_dates_in_semester(current_semester)

        # Step 5: Create recurring events for each day type and course combination
        for day_num_str, slots in daily_slots.items():
            # Convert our day numbering to Python's weekday numbering
            day_of_week_int = day_mapping_for_weekday.get(day_num_str)
            if day_of_week_int is None:
                print(f"Warning: Unknown day: {day_num_str}. Skipping.")
                continue

            # Find the first occurrence of this weekday in the semester
            # This calculates when the first lesson of this weekday should occur
            first_week_start = semester_start - timedelta(days=semester_start.weekday())
            first_occurrence = first_week_start + timedelta(days=day_of_week_int)
            
            # If the first occurrence is before semester start, move to next week
            if first_occurrence < semester_start:
                first_occurrence += timedelta(weeks=1)
            # Skip if no occurrence within semester (shouldn't happen in normal cases)
            if first_occurrence > semester_end:
                continue

            # Create recurring events for each lesson slot on this day
            for slot_type, course_name, course_code, slot_obj in slots:
                # Step 5a: Build the basic event time information
                start_datetime = datetime.combine(first_occurrence, slot_obj.start_time)
                end_datetime = datetime.combine(first_occurrence, slot_obj.end_time)
                # Convert to ISO format for Google Calendar API
                # This is the format required by Google Calendar for dateTime fields
                start_time_iso = start_datetime.isoformat()
                end_time_iso = end_datetime.isoformat()
                
                # Step 5b: Build event title and description
                title = f"{course_name} - {slot_type}"
                description = f"Course: {course_name}\nCourse Code: {course_code}"
                
                # Step 5c: Add location information if available
                building = getattr(slot_obj, 'building', None)
                room = getattr(slot_obj, 'room', None)
                location = None
                if building and room:
                    location = f"{building} - {room}"
                elif building:
                    location = f"{building}"
                elif room:
                    location = f"{room}"
                if location:
                    description += f"\nLocation: {location}"
                
                # Step 5d: Add lecturer information if available
                lecturer = getattr(slot_obj, 'lecturer', None) or getattr(slot_obj, 'instructor', None)
                if lecturer:
                    description += f"\nLecturer: {lecturer}"

                # Step 5e: Set event color based on lesson type 
                # This uses the predefined color mapping for different lesson types
                # Default to "1" (default color) if slot type is unknown
                color_id = slot_type_colors.get(slot_type, "1")
                
                # Step 5f: Calculate recurrence parameters
                # Count how many weeks this event should repeat
                weeks_count = ((semester_end - first_occurrence).days // 7) + 1
                
                # Step 5g: Create list of exception dates (holidays) in the correct format
                # These dates will be excluded from the recurring event
                exception_dates = []
                current_check_date = first_occurrence
                while current_check_date <= semester_end:
                    if current_check_date in holiday_dates:
                        # Format as YYYYMMDDTHHMMSS for the specific event time
                        exception_datetime = datetime.combine(current_check_date, slot_obj.start_time)
                        exception_dates.append(exception_datetime.strftime('%Y%m%dT%H%M%S'))
                    current_check_date += timedelta(weeks=1)
                
                # Step 5h: Build recurrence rules
                # RRULE defines the repetition pattern, EXDATE excludes specific dates
                recurrence_rules = [f'RRULE:FREQ=WEEKLY;COUNT={weeks_count}']
                if exception_dates:
                    recurrence_rules.append(f'EXDATE;TZID=Asia/Jerusalem:{",".join(exception_dates)}')
                
                # Step 5i: Build the complete event object for Google Calendar API
                event = {
                    'summary': title,
                    'description': description,
                    'start': {
                        'dateTime': start_time_iso,
                        'timeZone': 'Asia/Jerusalem',
                    },
                    'end': {
                        'dateTime': end_time_iso,
                        'timeZone': 'Asia/Jerusalem',
                    },
                    'colorId': color_id,
                    'recurrence': recurrence_rules
                }
                
                # Step 5j: Insert the event into the academic calendar
                try:
                    created_event = self.calendar_manager.service.events().insert(
                        calendarId=self.academic_calendar_id, 
                        body=event
                    ).execute()
                    print(f"Recurring event created: {title} starting {first_occurrence} (excluding {len(exception_dates)} holiday dates)")
                except Exception as e:
                    print(f"Error creating recurring event: {e}")

        return True

    def delete_semester_events(self, semester_name=None):
        """
        Delete all events for a specific semester from the academic Google Calendar.
        This is useful for cleaning up the calendar or re-creating events.
        
        Args:
            semester_name (str, optional): Name of the semester to delete events for.
                                         If None, deletes events for the current semester.
                                         
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        # Determine which semester to delete events for
        if semester_name is None:
            # Use current semester if no specific semester is provided
            current_semester = self._get_current_semester()
            if not current_semester:
                print("Not currently in any semester period.")
                return False
            semester = current_semester
        else:
            # Find semester by name in the academic data
            semester = None
            for sem in self.academic_data['semesters']:
                if sem['name'] == semester_name:
                    semester = sem
                    break
            if not semester:
                print(f"Semester '{semester_name}' not found.")
                return False

        # Get events in the semester date range
        # Google Calendar API expects ISO format with 'Z' suffix for UTC
        semester_start = semester['start'].isoformat() + 'Z'
        semester_end = semester['end'].isoformat() + 'Z'
        
        try:
            # Step 1: List all events in the semester time range from the academic calendar
            events_result = self.calendar_manager.service.events().list(
                calendarId=self.academic_calendar_id,
                timeMin=semester_start,
                timeMax=semester_end,
                singleEvents=True,  # Expand recurring events into individual instances
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            deleted_count = 0
            
            # Step 2: Delete each event found in the time range
            for event in events:
                try:
                    self.calendar_manager.service.events().delete(
                        calendarId=self.academic_calendar_id,
                        eventId=event['id']
                    ).execute()
                    deleted_count += 1
                except Exception as e:
                    # Log individual deletion errors but continue with other events
                    print(f"Error deleting event {event.get('summary', 'Unknown')}: {e}")
                    
            print(f"Deleted {deleted_count} events for {semester['name']} from academic calendar")
            return True
            
        except Exception as e:
            print(f"Error retrieving events for deletion: {e}")
            return False

    def delete_academic_calendar(self):
        """
        Delete the entire academic calendar.
        WARNING: This will permanently delete all events in the academic calendar.
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if self.academic_calendar_id and self.academic_calendar_id != 'primary':
            return self.calendar_manager.delete_calendar(self.academic_calendar_id)
        else:
            print("Cannot delete primary calendar or invalid calendar ID")
            return False