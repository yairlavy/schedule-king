from PyQt5.QtCore import QThread, pyqtSignal
from src.services.schedule_event_maker import ScheduleEventMaker

class CalendarExportWorker(QThread):
    """
    Worker thread for calendar export to avoid blocking the UI.
    """
    # Signal emitted when export is finished: (success: bool, message: str)
    export_finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, schedule, semester=None):
        """
        Initialize the worker with a schedule and semester.
        """
        super().__init__()
        self.schedule = schedule      # The schedule object to export
        self.semester = semester      # The semester to export for
        self.event_maker = None      # Placeholder for the event maker instance
    
    @staticmethod
    def export_to_calendar(schedule , semester = None) -> tuple:
        """
        Exports a given schedule as events to the user's Google Calendar.
        Returns (success: bool, message: str)
        """
        try:
            # Initialize the ScheduleEventMaker if it hasn't been created yet
            try:
                event_maker = ScheduleEventMaker(semester=semester)
            except FileNotFoundError:
                # Credentials file missing
                return False, "Google Calendar credentials file not found. Please ensure 'credentials.json' is in the project root directory."
            except PermissionError:
                # Permission error accessing credentials
                return False, "Permission denied accessing Google Calendar credentials. Please check file permissions."
            except ImportError as e:
                # Missing required dependencies
                return False, f"Missing required Google Calendar dependencies: {e}. Please install required packages."
            except Exception as e:
                # Other initialization errors
                return False, f"Failed to initialize Google Calendar connection: {e}"
            # Attempt to create calendar events for the given schedule
            created = event_maker.create_events(schedule)
            if created:
                # Events created successfully
                return True, "Schedule successfully exported to Google Calendar."
            else:
                # Failed to create events (possibly no semester)
                return False, "Failed to create calendar events. Please check if you're currently in a semester period."
        except Exception as e:
            # Handle various known error types for user-friendly messages
            error_msg = str(e).lower()
            if "quota" in error_msg or "rate limit" in error_msg:
                return False, "Google Calendar API quota exceeded. Please try again later."
            elif "authentication" in error_msg or "credentials" in error_msg or "token" in error_msg:
                return False, "Google Calendar authentication failed. Please re-authenticate your Google account."
            elif "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                return False, "Network connection error. Please check your internet connection and try again."
            elif "calendar" in error_msg and "not found" in error_msg:
                return False, "Google Calendar not found or access denied. Please check your calendar permissions."
            elif "invalid" in error_msg and "time" in error_msg:
                return False, "Invalid time format in schedule. Please check your schedule data."
            elif "semester" in error_msg or "academic" in error_msg:
                return False, "Academic calendar data error. Please check if you're in a valid semester period."
            elif "permission" in error_msg or "access" in error_msg:
                return False, "Permission denied. Please check your Google Calendar access permissions."
            elif "service" in error_msg and "unavailable" in error_msg:
                return False, "Google Calendar service temporarily unavailable. Please try again later."
            elif "file" in error_msg and "not found" in error_msg:
                return False, "Required configuration files not found. Please check your installation."
            else:
                # Unknown error
                return False, f"Failed to export to Google Calendar: {e}"

    def run(self):
        """Run the export operation in a separate thread."""
        try:
            # Validate schedule before export
            if not self.schedule or not hasattr(self.schedule, 'extract_by_day'):
                # Schedule is invalid or missing required method
                self.export_finished.emit(False, "Invalid schedule data. Please select a valid schedule.")
                return
            # Check if schedule has any courses
            daily_slots = self.schedule.extract_by_day()
            if not daily_slots:
                # No courses in the schedule
                self.export_finished.emit(False, "Schedule is empty. Please select a schedule with courses.")
                return
            # Use the worker's export method and emit the result
            success, message = self.export_to_calendar(self.schedule, self.semester)
            self.export_finished.emit(success, message)
        except Exception as e:
            # Handle threading and memory errors gracefully
            error_msg = str(e).lower()
            if "memory" in error_msg:
                self.export_finished.emit(False, "Insufficient memory to process schedule. Please try with fewer courses.")
            elif "thread" in error_msg:
                self.export_finished.emit(False, "Threading error occurred. Please try again.")
            else:
                # Unknown error during export
                self.export_finished.emit(False, f"Unexpected error during export: {e}") 