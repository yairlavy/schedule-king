from src.services.GoogleCalenderManager import GoogleCalendarManager
from src.models.schedule import Schedule
from datetime import datetime, timedelta
from src.services.academic_calender_parser import get_full_academic_year  # Import the function

# Map day numbers (1-7) to English weekday numbers.
# Adjust this to match datetime.weekday() (0=Monday) and your day numbers (1=Sunday).
# Conversion: 1 (Sunday) -> 6 (Sunday), 2 (Monday) -> 0 (Monday), ..., 7 (Saturday) -> 5 (Saturday)
day_mapping_for_weekday = {
    "1": 6,  # Sunday
    "2": 0,  # Monday
    "3": 1,  # Tuesday
    "4": 2,  # Wednesday
    "5": 3,  # Thursday
    "6": 4,  # Friday
    "7": 5   # Saturday
}   

# Define a color mapping for slot types
# Google Calendar color IDs are limited to predefined palette.
# We'll map the closest Google Calendar color IDs to your desired colors:
# Light blue (Lecture)  -> colorId "9" (blue)
# Peach (Tirgul)        -> colorId "5" (yellow/orange)
# Light green (Maabada) -> colorId "10" (green)
slot_type_colors = {
    "Lecture": "9",    # Light blue
    "Tirgul": "5",     # Peach (closest: yellow/orange)
    "Maabada": "10",    # Light green
    "holiday": "11"  # Red (for holidays)
}

class ScheduleEventMaker:
    """
    Handles creation and deletion of Google Calendar events for academic schedules,
    including handling of holidays and semester boundaries.
    """

    def __init__(self):
        """
        Initialize the ScheduleEventMaker, setting up the Google Calendar manager
        and loading the academic year data (semesters and holidays).
        """
        try:
            self.calendar_manager = GoogleCalendarManager()
            # Get academic year data including holidays and semesters
            self.academic_data = get_full_academic_year()
        except Exception as e:
            raise

    def _get_current_semester(self):
        """
        Determine which semester we're currently in based on today's date.
        Returns the current semester dict or None if not in any semester.
        """
        today = datetime.now().date()
        # Loop through semesters to find the one containing today's date
        for semester in self.academic_data['semesters']:
            semester_start = semester['start'].date()
            semester_end = semester['end'].date()
            if semester_start <= today <= semester_end:
                return semester
        return None

    def _is_holiday_date(self, check_date):
        """
        Check if a given date falls within any holiday period.
        Returns the holiday dict if found, None otherwise.
        """
        check_date = check_date.date() if isinstance(check_date, datetime) else check_date
        # Loop through holidays to see if the date is within any holiday range
        for holiday in self.academic_data['holidays']:
            holiday_start = holiday['start'].date()
            holiday_end = holiday['end'].date()
            if holiday_start <= check_date <= holiday_end:
                return holiday
        return None

    def _create_holiday_event(self, holiday, date):
        """
        Create a holiday event for the given date as an all-day event in Google Calendar.
        """
        # Create all-day event
        start_time = date.isoformat()
        end_time = (date + timedelta(days=1)).isoformat()
        # Build the event dictionary for Google Calendar API
        event = {
            'summary': holiday['title'],
            'start': {
                'date': date.isoformat(),
                'timeZone': 'Asia/Jerusalem',
            },
            'end': {
                'date': (date + timedelta(days=1)).isoformat(),
                'timeZone': 'Asia/Jerusalem',
            },
            'colorId': slot_type_colors['holiday']  # Red color for holidays
        }
        # Insert the event into Google Calendar
        try:
            created_event = self.calendar_manager.service.events().insert(
                calendarId='primary', 
                body=event
            ).execute()
            print(f"Holiday event created: {holiday['title']} on {date}")
            return created_event
        except Exception as e:
            print(f"Error creating holiday event: {e}")
            return None

    def create_events(self, schedule: Schedule) -> bool:
        """
        Create recurring events for the schedule, respecting holidays and semester boundaries.
        """
        # Get current semester
        current_semester = self._get_current_semester()
        if not current_semester:
            print("Not currently in any semester period. Cannot create events.")
            return False

        print(f"Creating events for {current_semester['name']}")
        
        # Use the existing method in the Schedule model to extract lessons by day
        daily_slots = schedule.extract_by_day()

        # Get semester start and end dates
        semester_start = current_semester['start'].date()
        semester_end = current_semester['end'].date()

        # Create holiday events first (one event per holiday day in semester)
        created_holidays = set()
        for holiday in self.academic_data['holidays']:
            holiday_start = holiday['start'].date()
            holiday_end = holiday['end'].date()
            # Check if holiday overlaps with semester
            if holiday_start <= semester_end and holiday_end >= semester_start:
                # Create holiday events for each day in the holiday period
                current_holiday_date = max(holiday_start, semester_start)
                end_holiday_date = min(holiday_end, semester_end)
                while current_holiday_date <= end_holiday_date:
                    holiday_key = (holiday['title'], current_holiday_date)
                    if holiday_key not in created_holidays:
                        self._create_holiday_event(holiday, current_holiday_date)
                        created_holidays.add(holiday_key)
                    current_holiday_date += timedelta(days=1)

        # Create recurring events for each day type and course combination
        for day_num_str, slots in daily_slots.items():
            day_of_week_int = day_mapping_for_weekday.get(day_num_str)
            if day_of_week_int is None:
                print(f"Warning: Unknown day: {day_num_str}. Skipping.")
                continue

            # Find the first occurrence of this weekday in the semester
            first_week_start = semester_start - timedelta(days=semester_start.weekday())
            first_occurrence = first_week_start + timedelta(days=day_of_week_int)
            # If the first occurrence is before semester start, move to next week
            if first_occurrence < semester_start:
                first_occurrence += timedelta(weeks=1)
            # Skip if no occurrence within semester
            if first_occurrence > semester_end:
                continue

            # Create events for each slot on this day
            for slot_type, course_name, course_code, slot_obj in slots:
                # Use the start and end time from slot_obj
                start_datetime = datetime.combine(first_occurrence, slot_obj.start_time)
                end_datetime = datetime.combine(first_occurrence, slot_obj.end_time)
                # ISO 8601 format for Google API
                start_time_iso = start_datetime.isoformat()
                end_time_iso = end_datetime.isoformat()
                title = f"{course_name} - {slot_type}"
                description = f"Course: {course_name}"
                
                # Safely add location if it exists
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
                
                # Safely add lecturer if it exists
                lecturer = getattr(slot_obj, 'lecturer', None) or getattr(slot_obj, 'instructor', None)
                if lecturer:
                    description += f"\nLecturer: {lecturer}"

                color_id = slot_type_colors.get(slot_type, "1")
                
                # Calculate the number of weeks from first occurrence to semester end
                weeks_count = ((semester_end - first_occurrence).days // 7) + 1
                
                # Create list of exception dates (holidays)
                exception_dates = []
                current_check_date = first_occurrence
                while current_check_date <= semester_end:
                    if self._is_holiday_date(current_check_date):
                        exception_dates.append(current_check_date.strftime('%Y%m%d'))
                    current_check_date += timedelta(weeks=1)
                
                # Build recurrence rule
                recurrence_rules = [f'RRULE:FREQ=WEEKLY;COUNT={weeks_count}']
                if exception_dates:
                    recurrence_rules.append(f'EXDATE;TZID=Asia/Jerusalem:{",".join(exception_dates)}')
                
                # Build the event dictionary for Google Calendar API
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
                
                # Insert the event into Google Calendar
                try:
                    created_event = self.calendar_manager.service.events().insert(
                        calendarId='primary', 
                        body=event
                    ).execute()
                    print(f"Recurring event created: {title} starting {first_occurrence} (excluding {len(exception_dates)} holiday dates)")
                except Exception as e:
                    print(f"Error creating recurring event: {e}")

        return True

    def delete_semester_events(self, semester_name=None):
        """
        Delete all events for a specific semester.
        If semester_name is None, deletes events for the current semester.
        """
        if semester_name is None:
            current_semester = self._get_current_semester()
            if not current_semester:
                print("Not currently in any semester period.")
                return False
            semester = current_semester
        else:
            # Find semester by name
            semester = None
            for sem in self.academic_data['semesters']:
                if sem['name'] == semester_name:
                    semester = sem
                    break
            if not semester:
                print(f"Semester '{semester_name}' not found.")
                return False

        # Get events in the semester date range
        semester_start = semester['start'].isoformat() + 'Z'
        semester_end = semester['end'].isoformat() + 'Z'
        try:
            # List all events in the semester range
            events_result = self.calendar_manager.service.events().list(
                calendarId='primary',
                timeMin=semester_start,
                timeMax=semester_end,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            deleted_count = 0
            # Delete each event found
            for event in events:
                try:
                    self.calendar_manager.service.events().delete(
                        calendarId='primary',
                        eventId=event['id']
                    ).execute()
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting event {event.get('summary', 'Unknown')}: {e}")
            print(f"Deleted {deleted_count} events for {semester['name']}")
            return True
        except Exception as e:
            print(f"Error retrieving events for deletion: {e}")
            return False
