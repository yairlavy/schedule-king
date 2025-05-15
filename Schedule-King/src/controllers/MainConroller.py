from PyQt5.QtWidgets import QMessageBox
from src.controllers.CourseController import CourseController
from src.controllers.ScheduleController import ScheduleController
from src.views.course_window import CourseWindow
from src.views.schedule_window import ScheduleWindow
from src.services.schedule_api import ScheduleAPI
from src.models.course import Course
from typing import List

class MainController:
    def __init__(self, api: ScheduleAPI):
        # Initialize the main controller with the API instance
        self.api = api

        # Initialize course and schedule controllers
        self.course_controller = CourseController(api)
        self.schedule_controller = ScheduleController(api)

        # Initialize the course window and set up event handlers
        self.course_window = CourseWindow()
        self.schedule_window = None  # Schedule window will be created later

        # Set up event handlers for the course window
        self.course_window.on_courses_loaded = self.on_file_selected
        self.course_window.on_continue = self.on_courses_selected

    def start_application(self):
        # Show the course window to start the application
        self.course_window.show()

    def on_file_selected(self, file_path: str):
        # Handle the event when a file is selected
        try:
            # Get course names from the selected file
            courses = self.course_controller.get_courses_names(file_path)
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

    def on_courses_selected(self, selected_courses: List[Course]):
        # Handle the event when courses are selected
        if not selected_courses:
            # Show a warning if no courses are selected
            QMessageBox.warning(
                self.course_window,
                "No Courses Selected",
                "Please select at least one course before proceeding."
            )
            return

        # Set the selected courses in the course controller
        self.course_controller.set_selected_courses(selected_courses)
        # Initialize the schedule window with the generated schedules
        self.schedule_window = ScheduleWindow([], self.schedule_controller)
        # Generate schedules based on the selected courses
        self.schedule_controller.generate_schedules(selected_courses)
        # Set up the back navigation event handler
        self.schedule_window.on_back = self.on_navigate_back_to_courses

        # Hide the course window and show the schedule window
        self.course_window.hide()
        self.schedule_window.show()

    def on_generate_schedules(self):
        # Generate schedules for the currently selected courses
        selected_courses = self.course_controller.get_selected_courses()
        schedules = self.schedule_controller.generate_schedules(selected_courses)
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
