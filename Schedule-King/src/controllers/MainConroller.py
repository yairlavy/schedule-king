# src/controllers/main_controller.py

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
        self.schedule_window = None  # <-- שים לב: לא יוצרים ScheduleWindow בהתחלה!

        # קישור callbackים
        self.course_window.on_courses_loaded = self.on_file_selected
        self.course_window.on_continue = self.on_courses_selected

    def start_application(self):
        self.course_window.show()

    def on_file_selected(self, file_path: str):
        courses = self.course_controller.get_courses_names(file_path)
        self.course_window.displayCourses(courses)

    def on_courses_selected(self, selected_courses: List[Course]):
        self.course_controller.set_selected_courses(selected_courses)
        schedules = self.schedule_controller.generate_schedules(selected_courses)

        # עכשיו יוצרים את ScheduleWindow רק כשצריך
        self.schedule_window = ScheduleWindow(schedules, self.api)
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
        self.course_window.show()
