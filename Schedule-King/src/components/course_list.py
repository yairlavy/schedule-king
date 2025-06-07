from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem, QVBoxLayout, QWidget, QSizePolicy, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from typing import List
from src.models.course import Course

class CourseList(QWidget):
    selectionChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.courses: List[Course] = []  # All courses
        self.filtered_courses: List[Course] = []  # Currently displayed courses
        self.selected_course_codes: set = set()

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSpacing(6)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set font
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Medium)
        self.list_widget.setFont(font)

        # Apply styles
        self.list_widget.setStyleSheet("""
            QListWidget {
                padding: 15px;
                border: 2px solid #C5CAE9;
                border-radius: 12px;
                background-color: #E8EAF6;
                font-size: 13pt;
                color: #283593;
            }
            QListWidget::item {
                padding: 12px;
                margin: 5px;
                border: 1px solid #C5CAE9;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            QListWidget::item:selected {
                background-color: #5C6BC0;
                color: white;
                border: 1px solid #3949AB;
            }
            QListWidget::item:hover {
                background-color: #9FA8DA;
                color: #1A237E;
            }
        """)

        layout.addWidget(self.list_widget)
        self.list_widget.itemSelectionChanged.connect(self._handle_selection_changed)

    def populate_courses(self, courses: List[Course]):
        self.courses = courses
        self.filtered_courses = courses
        self.selected_course_codes.clear()
        self._update_course_list(courses)

    def _update_course_list(self, course_list: List[Course]):
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        items_to_select = []

        for course in course_list:
            item = QListWidgetItem(f"{course.course_code} - {course.name}")
            item.setData(Qt.UserRole, course.course_code)

            # Basic course info
            details = [
                f"<b>{course.course_code}</b>: {course.name}",
                f"Instructor: {course.instructor}",
                f"Lectures: {len(course.lectures)} | Tirguls: {len(course.tirguls)} | Labs: {len(course.maabadas)}",
            ]

            # Helper function to format slot groups
            def format_slot_groups(slot_groups, label, color):
                for group in slot_groups:
                    if not group:
                        continue
                    details.append(f"<span style='color:{color}'>\u25A0 {label}:</span>")
                    if isinstance(group, list):
                        for slot in group:
                            details.append(f"&nbsp;&nbsp;&bull; {slot}")
                    else:
                        # if group is a single slot
                        details.append(f"&nbsp;&nbsp;&bull; {group}")

            format_slot_groups(course.lectures, "Lecture", "#1976D2")
            format_slot_groups(course.tirguls, "Tirgul", "#388E3C")
            format_slot_groups(course.maabadas, "Lab", "#7B1FA2")

            item.setToolTip("<br>".join(details))
            self.list_widget.addItem(item)

            if course.course_code in self.selected_course_codes:
                items_to_select.append(item)

        for item in items_to_select:
            item.setSelected(True)
            self.list_widget.scrollToItem(item)

        self.list_widget.blockSignals(False)

    def _handle_selection_changed(self):
        # Always update selected_course_codes from the visible selection
        selected_items = self.list_widget.selectedItems()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            code = item.data(Qt.UserRole)
            if item.isSelected():
                self.selected_course_codes.add(code)
            else:
                self.selected_course_codes.discard(code)
        # Always emit the full selection (from all courses, not just visible)
        selected = [course for course in self.courses if course.course_code in self.selected_course_codes]
        self.selectionChanged.emit(selected)

    def get_selected_courses(self) -> List[Course]:
        # Always return all courses whose codes are in selected_course_codes
        return [
            course for course in self.courses
            if course.course_code in self.selected_course_codes
        ]

    def clear_selection(self):
        self.list_widget.clearSelection()
        self.selected_course_codes.clear()
        self.selectionChanged.emit([])

    def filter_courses(self, text: str):
        text = text.strip().lower()
        self.filtered_courses = [
            course for course in self.courses
            if text in course.name.lower() or text in course.course_code.lower()
        ]
        # Store current selections before updating
        current_selections = self.selected_course_codes.copy()
        self._update_course_list(self.filtered_courses)
        # Restore selections after updating
        self.selected_course_codes = current_selections
        # Emit selection changed to update the selected courses panel
        self._handle_selection_changed() 