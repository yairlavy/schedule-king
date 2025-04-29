# course_selector.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from src.models.course import Course
from typing import List

class CourseSelector(QListWidget):
    def __init__(self, courses: List[Course]):
        super().__init__()
        self.load_courses(courses)

    def load_courses(self, courses: List[Course]):
        self.clear()
        for course in courses:
            item = QListWidgetItem(f"{course.name} ({course.course_code})")
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, course)  # שמירת Course בתוך ה-item
            self.addItem(item)

    def get_selected_courses(self) -> List[Course]:
        selected = []
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() == Qt.Checked:
                course = item.data(Qt.UserRole)  # שולף את הקורס מה-item
                if course:
                    selected.append(course)
        return selected

    def select_course(self, course: Course):
        for i in range(self.count()):
            item = self.item(i)
            course_obj = item.data(Qt.UserRole)
            if course_obj and course_obj.course_code == course.course_code:
                item.setCheckState(Qt.Checked)
