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
        self.api = api

        self.course_controller = CourseController(api)
        self.schedule_controller = ScheduleController(api)

        self.course_window = CourseWindow()
        self.schedule_window = None  

        self.course_window.on_courses_loaded = self.on_file_selected
        self.course_window.on_continue = self.on_courses_selected

    def start_application(self):
        self.course_window.show()

    def on_file_selected(self, file_path: str):
        try:
            courses = self.course_controller.get_courses_names(file_path)
            if not courses:
                QMessageBox.critical(
                    self.course_window,
                    "Invalid File Format",
                    "The selected file has an invalid format. Please make sure the file follows the correct course format."
                )
                return
            self.course_window.displayCourses(courses)
        except FileNotFoundError:
            QMessageBox.critical(
                self.course_window,
                "File Not Found",
                f"The file '{file_path}' could not be found."
            )
        except Exception as e:
            QMessageBox.critical(
                self.course_window,
                "Error Loading File",
                f"An error occurred while loading the file: {str(e)}"
            )

    def on_courses_selected(self, selected_courses: List[Course]):
        if not selected_courses:
            QMessageBox.warning(
                self.course_window,
                "No Courses Selected",
                "Please select at least one course before proceeding."
            )
            return

        self.course_controller.set_selected_courses(selected_courses)
        schedules = self.schedule_controller.generate_schedules(selected_courses)

        self.schedule_window = ScheduleWindow(schedules, self.schedule_controller)
        self.schedule_window.on_back = self.on_navigate_back_to_courses

        self.course_window.hide()
        self.schedule_window.show()

    def on_generate_schedules(self):
        selected_courses = self.course_controller.get_selected_courses()
        schedules = self.schedule_controller.generate_schedules(selected_courses)
        if self.schedule_window:
            self.schedule_window.displaySchedules(schedules)

    def on_navigate_back_to_courses(self):
        if self.schedule_window:
            self.schedule_window.hide()
            self.schedule_window = None  
        self.course_window.show()
