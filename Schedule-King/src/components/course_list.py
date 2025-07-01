from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem, QVBoxLayout, QWidget, QSizePolicy, QComboBox, QToolTip
from PyQt5.QtCore import pyqtSignal, Qt, QEvent, QTimer
from PyQt5.QtGui import QFont, QCursor
from typing import List, Dict, Optional, Set
from src.models.course import Course

class CourseListWidget(QListWidget):
    tooltipRequested = pyqtSignal(Course)  # Changed from str to Course

    def __init__(self, parent=None):
        super().__init__(parent)
        self.viewport().installEventFilter(self)
        self.setMouseTracking(True)
        self.viewport().setAttribute(Qt.WA_Hover, True)
        # Cache for course lookup
        self._course_cache: Dict[str, Course] = {}

    def set_course_cache(self, course_cache: Dict[str, Course]):
        """Set the course cache for efficient lookups."""
        self._course_cache = course_cache

    def eventFilter(self, obj, event):
        if obj is self.viewport() and event.type() == QEvent.ToolTip:
            item = self.itemAt(event.pos())
            if item:
                course_code = item.data(Qt.UserRole)
                if course_code and course_code in self._course_cache:
                    course = self._course_cache[course_code]
                    if not course.is_detailed:
                        self.tooltipRequested.emit(course)
            return False
        return super().eventFilter(obj, event)

class CourseList(QWidget):
    selectionChanged = pyqtSignal(list)
    tooltipRequested = pyqtSignal(Course)  # Changed from str to Course

    def __init__(self, parent=None):
        super().__init__(parent)
        self.courses: List[Course] = []
        self.filtered_courses: List[Course] = []
        self.selected_course_codes: Set[str] = set()
        # Cache for performance
        self._course_lookup: Dict[str, Course] = {}
        self._item_lookup: Dict[str, QListWidgetItem] = {}
        self._categories_cache: List[str] = []
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.category_filter = QComboBox()
        self.category_filter.setObjectName("category_filter")
        self.category_filter.addItem("All Categories")
        layout.addWidget(self.category_filter)
        self.list_widget = CourseListWidget()
        self._configure_list_widget()
        layout.addWidget(self.list_widget)

    def _configure_list_widget(self):
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSpacing(6)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Medium)
        self.list_widget.setFont(font)
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

    def _connect_signals(self):
        self.category_filter.currentIndexChanged.connect(self._apply_filters)
        self.list_widget.itemSelectionChanged.connect(self._handle_selection_changed)
        self.list_widget.tooltipRequested.connect(self.tooltipRequested)

    def populate_courses(self, courses: List[Course]):
        self.courses = courses
        self.filtered_courses = courses
        self.selected_course_codes.clear()
        self._course_lookup = {course.course_code: course for course in courses}
        self._item_lookup.clear()
        self.list_widget.set_course_cache(self._course_lookup)
        self._update_category_filter(courses)
        self._update_course_list(courses)

    def _update_category_filter(self, courses: List[Course]):
        new_categories = sorted(set(course.category for course in courses))
        if new_categories != self._categories_cache:
            self._categories_cache = new_categories
            self.category_filter.blockSignals(True)
            self.category_filter.clear()
            self.category_filter.addItem("All Categories")
            self.category_filter.addItems(new_categories)
            self.category_filter.blockSignals(False)

    def _update_course_list(self, course_list: List[Course]):
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        self._item_lookup.clear()
        filtered_lookup = {course.course_code: course for course in course_list}
        self.list_widget.set_course_cache(filtered_lookup)
        items_to_select = []
        for course in course_list:
            item = self._create_course_item(course)
            self.list_widget.addItem(item)
            self._item_lookup[course.course_code] = item
            if course.course_code in self.selected_course_codes:
                items_to_select.append(item)
        for item in items_to_select:
            item.setSelected(True)
        self.list_widget.blockSignals(False)

    def _create_course_item(self, course: Course) -> QListWidgetItem:
        item = QListWidgetItem(f"{course.course_code} - {course.name}")
        item.setData(Qt.UserRole, course.course_code)
        tooltip_text = self._generate_tooltip_text(course)
        item.setToolTip(tooltip_text)
        return item

    def _generate_tooltip_text(self, course: Course) -> str:
        if not course.is_detailed:
            return f"<b>{course.course_code}</b>: {course.name}<br>Loading ..."
        details = [
            f"<b>{course.course_code}</b>: {course.name}",
            f"Category: {course.category}",
            f"Instructor: {course.instructor}",
            (f"Lectures: {sum(1 for lec in course.lectures if lec)} | "
            f"Tirguls: {sum(1 for tir in course.tirguls if tir)} | "
            f"Labs: {sum(1 for lab in course.maabadas if lab)}"),
        ]
        self._format_slot_groups(course.lectures, "Lecture", "#1976D2", details)
        self._format_slot_groups(course.tirguls, "Tirgul", "#FF9800", details)
        self._format_slot_groups(course.maabadas, "Maabada", "#4CAF50", details)
        return "<br>".join(details)

    def _format_slot_groups(self, slot_groups, label: str, color: str, details: List[str]):
        for group in slot_groups:
            if not group:
                continue
            details.append(f"<span style='color:{color}'>\u25A0 {label}:</span>")
            if isinstance(group, list):
                for slot in group:
                    details.append(f"&nbsp;&nbsp;&bull; {slot}")
            else:
                details.append(f"&nbsp;&nbsp;&bull; {group}")

    def _handle_selection_changed(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            code = item.data(Qt.UserRole)
            if item.isSelected():
                self.selected_course_codes.add(code)
            else:
                self.selected_course_codes.discard(code)
        selected_courses = [
            self._course_lookup[code] 
            for code in self.selected_course_codes 
            if code in self._course_lookup
        ]
        self.selectionChanged.emit(selected_courses)

    def get_selected_courses(self) -> List[Course]:
        return [
            self._course_lookup[code] 
            for code in self.selected_course_codes 
            if code in self._course_lookup
        ]

    def clear_selection(self):
        self.list_widget.clearSelection()
        self.selected_course_codes.clear()
        self.selectionChanged.emit([])

    def filter_courses(self, text: str):
        text = text.strip().lower()
        selected_category = self.category_filter.currentText()
        self.filtered_courses = [
            course for course in self.courses
            if self._matches_filter(course, text, selected_category)
        ]
        self._update_course_list(self.filtered_courses)
        self._handle_selection_changed()

    def _matches_filter(self, course: Course, text: str, category: str) -> bool:
        text_match = (not text or 
                     text in course.name.lower() or 
                     text in course.course_code.lower())
        category_match = (category == "All Categories" or 
                         course.category == category)
        return text_match and category_match

    def _apply_filters(self):
        self.filter_courses("")

    def update_course_tooltip(self, course: Course):
        item = self._item_lookup.get(course.course_code)
        if not item:
            return
        tooltip_text = self._generate_tooltip_text(course)
        item.setToolTip(tooltip_text)
        if self._is_mouse_over_item(item):
            self._refresh_tooltip(tooltip_text)

    def _is_mouse_over_item(self, item: QListWidgetItem) -> bool:
        current_pos = self.list_widget.mapFromGlobal(QCursor.pos())
        hovered_item = self.list_widget.itemAt(current_pos)
        return hovered_item is item

    def _refresh_tooltip(self, tooltip_text: str):
        QToolTip.hideText()
        QTimer.singleShot(50, lambda: QToolTip.showText(QCursor.pos(), tooltip_text, self.list_widget))