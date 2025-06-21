from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from src.services.choicefreak.choicefreak_parser import ChoiceFreakParser
import time

class CourseFillingWorker(QObject):
    # Signal: emits the filled course object
    courseFilled = pyqtSignal(object)  # you can use Course instead of object if type available

    def __init__(self):
        super().__init__()
        self.choicefreak_parser = ChoiceFreakParser("biu","2025-2")  # Initialize with default values
        self._running = True

    @pyqtSlot(list)
    def fill_courses(self, courses):
        try:
            course_ids = [c.course_code for c in courses]
            filled_courses = self.choicefreak_parser.parse_by_ids(course_ids, "biu")

            # Build a dict for quick lookup
            filled_map = {c.course_code: c for c in filled_courses}

            for course in courses:
                filled = filled_map.get(course.course_code)
                if filled:
                    self.courseFilled.emit((course, filled))
                else:
                    print(f"No filled data found for course code: {course.course_code}")
        except Exception as e:
            print(f"Failed to fill courses: {e}")


    def stop(self):
        self._running = False
