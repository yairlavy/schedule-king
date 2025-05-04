from PyQt5.QtWidgets import (
    QListWidget, QAbstractItemView, QListWidgetItem, QVBoxLayout,
    QPushButton, QWidget, QHBoxLayout, QSizePolicy, QLabel, QLineEdit, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap
from typing import List
from src.models.course import Course


class CourseSelector(QWidget):
    coursesSelected = pyqtSignal(list)
    coursesSubmitted = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E3F2FD, stop:1 #F0F7FF); border-radius: 10px;")

        # === Main Layout ===
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(16)

        # === Banner Image ===
        banner = QLabel()
        banner.setPixmap(QPixmap("assets/schedule_banner.png").scaledToWidth(300, Qt.SmoothTransformation))
        banner.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(banner)

        # === Title ===
        self.title_label = QLabel("Available Courses")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #1A237E;
                font-size: 34px;
                font-weight: 800;
                font-family: 'Segoe UI', sans-serif;
                border-bottom: 3px solid #C5CAE9;
                padding-bottom: 12px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # === Instruction Label ===
        instruction = QLabel("Select your desired courses from the list below and click 'Generate Schedules'")
        instruction.setStyleSheet("color: #3A3A3A; font-size: 12pt; font-style: italic;")
        instruction.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(instruction)

        # === Search Bar ===
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search courses...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 12pt;
                border: 2px solid #C5CAE9;
                border-radius: 8px;
            }
        """)
        self.search_bar.textChanged.connect(self._filter_courses)
        self.layout.addWidget(self.search_bar)

        # === Side-by-Side Layout ===
        self.split_layout = QHBoxLayout()
        self.layout.addLayout(self.split_layout)

        # === List Widget ===
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSpacing(6)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Medium)
        self.list_widget.setFont(font)
        self.split_layout.addWidget(self.list_widget, 3)

        # === Selected Courses Panel ===
        self.selected_courses_panel = QLabel("<b>Selected Courses:</b>")
        self.selected_courses_panel.setWordWrap(True)
        self.selected_courses_panel.setAlignment(Qt.AlignTop)
        self.selected_courses_panel.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                border: 1px solid #BBDEFB;
                padding: 12px;
                font-size: 10.5pt;
                border-radius: 6px;
                color: #0D47A1;
                min-width: 240px;
            }
        """)
        self.split_layout.addWidget(self.selected_courses_panel, 2)

        # === Buttons ===
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(15)
        self.button_layout.setAlignment(Qt.AlignCenter)

        self.clear_button = QPushButton("Clear All")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setStyleSheet(self._red_button_style())

        self.submit_button = QPushButton("Generate Schedules")
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setStyleSheet(self._green_button_style())

        self.load_button = QPushButton("Load Courses")
        self.load_button.setCursor(Qt.PointingHandCursor)
        self.load_button.setStyleSheet(self._blue_button_style())
        self.load_button.clicked.connect(self._emit_load_request)

        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.submit_button)
        self.button_layout.addWidget(self.load_button)
        self.layout.addLayout(self.button_layout)

        # === Footer ===
        footer = QLabel("\U0001F537 Records made by the Schedule Kings")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #78909C; font-size: 10pt; margin-top: 20px;")
        self.layout.addWidget(footer)

        # === Internal State ===
        self.courses: List[Course] = []
        self.filtered_courses: List[Course] = []
        self.selected_course_codes: set = set()

        self.list_widget.itemSelectionChanged.connect(self._handle_selection_changed)
        self.submit_button.clicked.connect(self._handle_submit)
        self.clear_button.clicked.connect(self._handle_clear)

    def populate_courses(self, courses: List[Course]):
        self.courses = courses
        self.selected_course_codes.clear()
        self._update_course_list(courses)
        self.title_label.setText(f"Available Courses ({len(courses)} total)")

    def _filter_courses(self, text: str):
        text = text.strip().lower()
        filtered = [
            course for course in self.courses
            if text in course.name.lower() or text in course.course_code.lower()
        ]
        self._update_course_list(filtered)
        self.title_label.setText(f"Available Courses ({len(filtered)} shown)")

    def _update_course_list(self, course_list: List[Course]):
        self.list_widget.clear()
        self.filtered_courses = course_list

        for course in course_list:
            item = QListWidgetItem(f"{course.course_code} - {course.name}")
            item.setData(Qt.UserRole, self.courses.index(course))

            details = [
                f"<b>{course.course_code}</b>: {course.name}",
                f"Instructor: {course.instructor}",
                f"Lectures: {len(course.lectures)} | Tirguls: {len(course.tirguls)} | Labs: {len(course.maabadas)}",
            ]
            for slot in course.lectures:
                details.append(f"<span style='color:#1976D2'>\u25A0 Lecture:</span> {slot}")
            for slot in course.tirguls:
                details.append(f"<span style='color:#388E3C'>\u25A0 Tirgul:</span> {slot}")
            for slot in course.maabadas:
                details.append(f"<span style='color:#7B1FA2'>\u25A0 Lab:</span> {slot}")

            item.setToolTip("<br>".join(details))

            if course.course_code in self.selected_course_codes:
                item.setSelected(True)
            self.list_widget.addItem(item)

    def _handle_selection_changed(self):
        selected = self.get_selected_courses()
        self.selected_course_codes = {course.course_code for course in selected}
        self.title_label.setText(f"Available Courses ({len(selected)} selected)")

        if selected:
            course_lines = [
                f"<b>{course.course_code}</b>: {course.name} <i>({course.instructor})</i>"
                for course in selected
            ]
            self.selected_courses_panel.setText("<br><br>".join(course_lines))
        else:
            self.selected_courses_panel.setText("<b>Selected Courses:</b>")

        self.coursesSelected.emit(selected)

    def _handle_submit(self):
        self.coursesSubmitted.emit(self.get_selected_courses())

    def _handle_clear(self):
        self.list_widget.clearSelection()
        self.selected_course_codes.clear()
        self.title_label.setText(f"Available Courses ({len(self.courses)} total)")
        self.selected_courses_panel.setText("<b>Selected Courses:</b>")
        self.coursesSelected.emit([])

    def _emit_load_request(self):
        from PyQt5.QtWidgets import QApplication, QMainWindow
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow) and hasattr(widget, 'load_courses_from_file'):
                widget.load_courses_from_file()
                break

    def get_selected_courses(self) -> List[Course]:
        return [
            self.courses[item.data(Qt.UserRole)]
            for item in self.list_widget.selectedItems()
            if 0 <= item.data(Qt.UserRole) < len(self.courses)
        ]

    def set_selected_courses(self, course_codes: List[str]):
        self.list_widget.clearSelection()
        self.selected_course_codes = set(course_codes)
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            index = item.data(Qt.UserRole)
            if self.courses[index].course_code in course_codes:
                item.setSelected(True)

    def _red_button_style(self):
        return """
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """

    def _green_button_style(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """

    def _blue_button_style(self):
        return """
            QPushButton {
                background-color: #3949AB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #1A237E;
            }
        """