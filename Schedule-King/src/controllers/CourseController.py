from src.services.schedule_api import ScheduleAPI
from src.models.course import Course
from typing import List, Optional
from src.models.time_slot import TimeSlot
from src.services.choicefreak.choicefreak_api import ChoiceFreakApi
from src.services.choicefreak.choicefreak_parser import ChoiceFreakParser
from src.controllers.CourseFiller import CourseFillingWorker
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from collections import defaultdict
import time

class FillSignalEmitter(QObject):
    fillRequested = pyqtSignal(list, str)

class CourseController:
    def __init__(self, api: ScheduleAPI):
        self.api = api
        self.courses: List[Course] = []
        self.selected_courses: List[Course] = []
        self.forbidden_slots: List[TimeSlot] = []  # Add storage for forbidden slots
        self.preferred_slots: List[TimeSlot] = []
        self.worker = CourseFillingWorker()
        self.period = "2025-2"  # Default period, can be changed later
        # Connect the signal
        self.worker.courseFilled.connect(self.on_course_filled)

        # Signal emitter
        self.signal_emitter = FillSignalEmitter()
        self.signal_emitter.fillRequested.connect(self.worker.fill_courses)

        self.university_courses = {}  # Cache for courses by university
        self.update_ui_course_filled = None
        self.running = False
    
    def start_thread(self):
        if not self.running:
            self.thread = QThread()
            self.worker.moveToThread(self.thread)
            self.thread.start()
            self.running = True
    
    def get_courses_names(self, file_path: str) -> List[Course]:
        """
        Loads the courses from the file path using the ScheduleAPI.
        """
        self.courses = self.api.get_courses(file_path)
        return self.courses
    def set_selected_courses(self, selected: List[Course], forbidden_slots: Optional[List[TimeSlot]] = None,
                            preferred_slots: Optional[List[TimeSlot]] = None) -> None:
        self.selected_courses = selected
        self.forbidden_slots = forbidden_slots or []
        self.preferred_slots = preferred_slots or []


    def get_selected_courses(self) -> List[Course]:
        """
        Returns the courses selected by the user.
        """
        return self.selected_courses

    def get_forbidden_slots(self) -> List[TimeSlot]:
        """
        Returns the forbidden time slots.
        """
        return self.forbidden_slots

    def get_courses_of_category(self, category: str) -> List[Course]:
        """
        Returns a list of courses for the given category.
        This method is used to fetch courses from the cached university courses.
        """
        if not self.university_courses:
            raise ValueError("No university courses available. Please update the university courses first.")
        
        # Assuming the first university in the cache is the one we want
        university = next(iter(self.university_courses))
        return self.fetch_choicefreak_courses(university, self.period)

    def fetch_choicefreak_courses(self, university, period: str) -> List[Course]:
        """Return a list of Course objects for the given university and category from ChoiceFreak."""
        ChoiceFreakApi.session_manager.get_cookie()  # Ensure the session cookie is loaded
        self.period = period  # Update the period for future calls
        index = ChoiceFreakApi.get_courses_by_category(university, period)

        courses = []
        # Fetch courses from all categories
        for cat, raw_courses in index.items():
            courses.extend(
                [Course(course_name=c.get('title', ''), course_code=str(c.get('id', '')), instructor="", is_detailed=False, category=cat, university=university) for c in raw_courses]
            )

        return courses
    
    def on_choicefreak_selection(self, university: str, category: str):
        """
        Handle the selection of a category from ChoiceFreak.
        Fetch and display courses for the selected university and category.
        """
        courses = self.fetch_choicefreak_courses(university, category)
        if not courses:
            print(f"No courses found for {university} in category {category}")
            return

    def on_course_filled(self, result):
        """
        Handle the filled course signal from the worker.
        This method can be used to update the UI or store the filled course.
        """
        course, filled_course = result
        course.copy(filled_course)
        if self.update_ui_course_filled:
            self.update_ui_course_filled(course)

    def fill_courses(self, courses: List['Course']):
        """
        Request the worker to fill courses without blocking.
        """
        # only fill undetailed courses
        undetailed_courses = [c for c in courses if not c.is_detailed]
        if not undetailed_courses:
            return
        self.signal_emitter.fillRequested.emit(undetailed_courses, self.period)
