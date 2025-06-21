from PyQt5.QtWidgets import QMessageBox
from src.controllers.CourseController import CourseController
from src.controllers.ScheduleController import ScheduleController
from src.views.course_window import CourseWindow
from src.views.schedule_window import ScheduleWindow
from src.services.schedule_api import ScheduleAPI
from src.models.course import Course
from typing import List, Optional
from src.models.time_slot import TimeSlot
from src.services.logger import Logger

class MainController:
    def __init__(self, api: ScheduleAPI, maximize_on_start=True):
        # Initialize the main controller with the API instance
        self.api = api
        self._maximize_on_start = maximize_on_start

        # Initialize course and schedule controllers
        self.course_controller = CourseController(api)
        self.schedule_controller = ScheduleController(api)

        # Initialize the course window and set up event handlers
        self.course_window = CourseWindow(maximize_on_start=maximize_on_start)
        self.schedule_window = None  # Schedule window will be created later

        # Set up event handlers for the course window
        self.course_window.on_courses_loaded = self.on_file_selected
        self.course_window.on_continue = self.on_courses_selected
        self.course_window.choicefreakSelectionMade.connect(self.on_choicefreak_selection)
        
    def start_application(self):
        # Show the course window to start the application
        self.course_window.show()

    def on_file_selected(self, file_path: str):
        # Handle the event when a file is selected
        try:
            # Get course names from the selected file
            courses = self.course_controller.get_courses_names(file_path)
            if Logger.inner_conflict:
                # Show an error message if there are inner conflicts
                QMessageBox.warning(
                    self.course_window,
                    "Inner Conflict Detected",
                    f"Inner conflict detected in the selected file: {Logger.inner_conflict}"
                )
                Logger.inner_conflict = ""  # Reset inner conflict message after handling it

            if not courses:
                # Show an error message if the file format is invalid
                QMessageBox.critical(
                    self.course_window,
                    "Invalid File Format",
                    "The selected file has an invalid format. Please make sure the file follows the correct course format."
                )
                return
            # Display the courses in the course window
            self.course_window.displayCourses(courses)
        except FileNotFoundError:
            # Show an error message if the file is not found
            QMessageBox.critical(
                self.course_window,
                "File Not Found",
                f"The file '{file_path}' could not be found."
            )
        except Exception as e:
            # Show a generic error message for any other exceptions
            QMessageBox.critical(
                self.course_window,
                "Error Loading File",
                f"An error occurred while loading the file: {str(e)}"
            )
    def on_choicefreak_selection(self, university: str, category: str):
        # Handle the event when a ChoiceFreak selection is made
        try:
            # Fetch courses from ChoiceFreak based on the selected university and category
            courses = self.course_controller.fetch_choicefreak_courses(university)
            print(f"Fetched {len(courses)} courses for category '{category}' in university '{university}'")
            if not courses:
                # Show a warning if no courses are found
                QMessageBox.warning(
                    self.course_window,
                    "No Courses Found",
                    f"No courses found for the selected category '{category}' in university '{university}'."
                )
                return
            # Display the fetched courses in the course window
            self.course_window.displayCourses(courses)
        except Exception as e:
            # Show an error message if there is an issue fetching courses
            QMessageBox.critical(
                self.course_window,
                "Error Fetching Courses",
                f"An error occurred while fetching courses: {str(e)}"
            )

    def on_courses_selected(self, selected_courses: List[Course], forbidden_slots: Optional[List[TimeSlot]] = None):
        # Handle the event when courses are selected
        if not selected_courses:
            # Show a warning if no courses are selected
            QMessageBox.warning(
                self.course_window,
                "No Courses Selected",
                "Please select at least one course before proceeding."
            )
            return

        # Set the selected courses and forbidden slots (if exist) in the course controller
        forbidden_slots = forbidden_slots or []
        self.course_controller.set_selected_courses(selected_courses, forbidden_slots)
       
        # Make sure any previous schedule generation is stopped if the schedule window exists
        if self.schedule_window:
            self.schedule_controller.stop_schedules_generation()
            self.schedule_controller.next = 1
        
        # Initialize the schedule window with the generated schedules
        self.schedule_window = ScheduleWindow(
                                               self.schedule_controller, 
                                              maximize_on_start=self._maximize_on_start, 
                                              show_progress_on_start=False)

        self.schedule_window.on_back = self.on_navigate_back_to_courses
        # Hide the course window and show the schedule window
        self.course_window.hide()
        self.schedule_window.show()
        # Generate schedules based on the selected courses and forbidden slots if any
        self.schedule_controller.generate_schedules(selected_courses, forbidden_slots)

    def on_generate_schedules(self):
        # Generate schedules for the currently selected courses
        selected_courses = self.course_controller.get_selected_courses()
        forbidden_slots = self.course_controller.get_forbidden_slots()
        schedules = self.schedule_controller.generate_schedules(selected_courses, forbidden_slots)
        if self.schedule_window:
            # Display the generated schedules in the schedule window
            self.schedule_window.displaySchedules(schedules)

    def on_navigate_back_to_courses(self):
        # Handle navigation back to the course selection window
        if self.schedule_window:
            # Hide the schedule window and reset it
            self.schedule_window.hide()
            self.schedule_window = None  
        # Show the course window again
        self.course_window.show()