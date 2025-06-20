from src.services.GoogleCalenderManager import GoogleCalendarManager
from src.models.schedule import Schedule
from datetime import datetime, timedelta

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
    "Maabada": "10"    # Light green
}
class ScheduleEventMaker :

    def __init__(self):
        # Ensure 
        try:
            self.calendar_manger = GoogleCalendarManager()
        except Exception as e:
                raise 


    def create_events(self, schedule : Schedule) -> bool :
            # Use the existing method in the Schedule model to extract lessons by day
            daily_slots = schedule.extract_by_day()

            # Start date for export (e.g., the current week). Can be adjusted as needed.
            # Start from the upcoming Sunday.
            today = datetime.now()
            # Find the upcoming Sunday (weekday 6)
            start_date_for_export = today - timedelta(days=today.weekday()) + timedelta(days=6)
            if today.weekday() == 6:  # If today is Saturday
                start_date_for_export = today  # Start from today

            # Export events for 12 weeks ahead to create recurring events
            num_weeks_to_export = 1

            for week_offset in range(num_weeks_to_export):
                current_week_start_date = start_date_for_export + timedelta(weeks=week_offset)

                for day_num_str, slots in daily_slots.items():
                    # Calculate the specific date for the lesson day in the current week
                    day_of_week_int = day_mapping_for_weekday.get(day_num_str)
                    if day_of_week_int is None:
                        print(f"Warning: Unknown day: {day_num_str}. Skipping.")
                        continue

                    # Find the start date of the week (Monday)
                    week_start = current_week_start_date - timedelta(days=current_week_start_date.weekday())

                    # Calculate the exact date for the lesson day in this week
                    lesson_date = week_start + timedelta(days=day_of_week_int)

                    for slot_type, course_name, course_code, slot_obj in slots:
                        # Use the start and end time from slot_obj
                        # slot_obj.start_time and slot_obj.end_time are likely datetime.time objects
                        # Combine them with lesson_date to create full datetime objects

                        start_datetime = datetime.combine(lesson_date, slot_obj.start_time)
                        end_datetime = datetime.combine(lesson_date, slot_obj.end_time)

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
                        
                        # Create the event in Google Calendar with color
                        self.calendar_manger.create_event(
                            summary=title,
                            description=description,
                            start_time=start_time_iso,
                            end_time=end_time_iso,
                            color_id=color_id
                        )
            return True