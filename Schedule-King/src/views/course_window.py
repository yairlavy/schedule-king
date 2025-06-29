from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout,
    QHBoxLayout, QWidget, QSizePolicy, QMessageBox,
    QPushButton, QDialog, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor,QFont
from typing import List, Callable, Optional
import os
from src.models.course import Course
from src.models.time_slot import TimeSlot
from src.components.course_selector import CourseSelector
from src.components.choicefreak_loader_dialog import ChoiceFreakLoaderDialog
from src.components.constraint_dialog import ConstraintDialog
from src.components.CourseEditorDialog import CourseEditorDialog
from src.styles.ui_styles import blue_button_style, red_button_style
from src.components.user_guide_dialog import UserGuideDialog

class LoadCoursesDialog(QDialog):
    """Dialog with two options for loading courses: Local and ChoiceFreak"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Courses")
        self.setModal(True)
        self.setFixedSize(500, 180)  # Made wider for side-by-side layout
        
        # Result tracking
        self.result_action = None  # "local", "choicefreak", or None
        
        self._setup_ui()
    
    def _load_icon_safely(self, icon_path: str, size: tuple = (40, 40), color: str = None) -> QIcon:
        """Safely load an icon with optional color change"""
        icon = QIcon()
        try:
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        size[0], size[1], 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    
                    if color:
                        colored_pixmap = QPixmap(scaled_pixmap.size())
                        colored_pixmap.fill(Qt.transparent)
                        
                        painter = QPainter(colored_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                        painter.drawPixmap(0, 0, scaled_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                        painter.fillRect(colored_pixmap.rect(), QColor(color))
                        painter.end()
                        
                        scaled_pixmap = colored_pixmap
                    
                    icon = QIcon(scaled_pixmap)
        except Exception as e:
            print(f"❌ Error loading icon {icon_path}: {e}")
        
        return icon
    
    def _get_icon_path(self, icon_name: str) -> str:
        """Get the full path to an icon file in the assets directory"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        assets_dir = os.path.join(project_root, "src", "assets")
        return os.path.join(assets_dir, icon_name)
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Choose how to load courses:")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Buttons container - horizontal layout for side-by-side
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Local database button
        local_icon_path = self._get_icon_path("local database.png")
        local_icon = self._load_icon_safely(local_icon_path,(60, 60), "white")
        
        if not local_icon.isNull():
            self.local_button = QPushButton()
            self.local_button.setIcon(local_icon)
            self.local_button.setIconSize(QSize(60, 60))
            self.local_button.setToolTip("Load from Local File")
        else:
            self.local_button = QPushButton("Load Courses")
        
        self.local_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
                min-height: 70px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.local_button.setCursor(Qt.PointingHandCursor)
        self.local_button.clicked.connect(self._select_local)
        
        # ChoiceFreak button (Global Database)
        choicefreak_icon_path = self._get_icon_path("database-table-icon-17.png")  # Updated icon path
        choicefreak_icon = self._load_icon_safely(choicefreak_icon_path, (50, 50), "white")
        
        if not choicefreak_icon.isNull():
            self.choicefreak_button = QPushButton()
            self.choicefreak_button.setIcon(choicefreak_icon)
            self.choicefreak_button.setIconSize(QSize(50, 50))
            self.choicefreak_button.setToolTip("Load from Global Database")
        else:
            self.choicefreak_button = QPushButton("Load from ChoiceFreak")
        
        self.choicefreak_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
                min-height: 70px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """)
        self.choicefreak_button.setCursor(Qt.PointingHandCursor)
        self.choicefreak_button.clicked.connect(self._select_choicefreak)
        
        # Add buttons to horizontal layout
        buttons_layout.addWidget(self.local_button)
        buttons_layout.addWidget(self.choicefreak_button)
        layout.addLayout(buttons_layout)
    
    def _select_local(self):
        """User selected local file loading"""
        self.result_action = "local"
        self.accept()
    
    def _select_choicefreak(self):
        """User selected ChoiceFreak loading"""
        self.result_action = "choicefreak"
        self.accept()
    
    def get_selected_action(self):
        """Return the selected action"""
        return self.result_action


class CourseWindow(QMainWindow):
    choicefreakSelectionMade = pyqtSignal(str, str)  # define at class level
    def __init__(self, maximize_on_start=True, fullscreen_on_start=False):
        super().__init__()
        self.setWindowTitle("Select Courses")  # Set the window title
        self._maximize_on_start = maximize_on_start
        self._fullscreen_on_start = fullscreen_on_start
        self._first_show = True

        # Set custom icon for the window
        #icon_path = os.path.join(os.path.dirname(__file__), "../assets/logo.ico")
        #self.setWindowIcon(QIcon(icon_path))

        # === Course Selector ===
        # Initialize the course selector component
        self.courseSelector = CourseSelector()
        self.courseSelector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Connect signals from the course selector to corresponding methods
        self.courseSelector.coursesSubmitted.connect(self.navigateToSchedulesWindow)
        
        # Remove the old load connection and hide the original load button
        # self.courseSelector.loadRequested.connect(self.load_courses_from_file)
        self.courseSelector.load_button.hide()  # Hide the original load button

        # === Layout Setup ===
        # Create a vertical layout for the main content
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(50, 30, 50, 30)  # Set margins
        outer_layout.setSpacing(20)  # Set spacing between elements

        # Add courseSelector directly without extra stretching
        outer_layout.addWidget(self.courseSelector)
        # User Guide Button with info icon
        
        
        # === Add/Edit Course Button ===
        additional_buttons_layout = QHBoxLayout()
        additional_buttons_layout.addStretch(1)

        self.add_edit_course_button = QPushButton("Add/Edit Course")
        self.add_edit_course_button.setStyleSheet(blue_button_style())
        self.add_edit_course_button.setCursor(Qt.PointingHandCursor)
        self.add_edit_course_button.clicked.connect(self.open_course_editor_dialog)
        additional_buttons_layout.addWidget(self.add_edit_course_button)

        outer_layout.addLayout(additional_buttons_layout)
        self.user_guide_button = self._create_user_guide_button()
        additional_buttons_layout.addWidget(self.user_guide_button)

        # === Time Constraints Section ===
        # Store forbidden time slots
        self.forbidden_slots = set()
        self.preferred_slots = set()
        
        # Create constraint button and add it to the CourseSelector's button layout
        self.constraintBtn = self._create_time_constraints_button()
        self.constraintBtn.clicked.connect(self._open_constraint_dialog)
        self.constraintBtn.setCursor(Qt.PointingHandCursor)
        self.constraintBtn.setStyleSheet(blue_button_style())
        
        # Add the constraint button to the CourseSelector's existing button layout
        self.courseSelector.button_layout.addWidget(self.constraintBtn)

        # === NEW Load Data Button (replaces the two separate buttons) ===
        self.load_data_button = self._create_load_data_button()
        self.courseSelector.button_layout.addWidget(self.load_data_button)

        # Wrap the layout in a container widget
        container = QWidget()
        container.setLayout(outer_layout)
        self.setCentralWidget(container)  # Set the container as the central widget

        # External callbacks for handling events
        self.on_courses_loaded: Callable[[str], None] = lambda path: None  # Callback for when courses are loaded
        self.on_continue: Callable[
            [List[Course], Optional[List[TimeSlot]], Optional[List[TimeSlot]]],
            None] = lambda selected, forbidden, preferred: None

        # Note: The courseSelector.clear_button only clears course selections, not time constraints
        # Time constraints are managed independently through the constraint dialog

    def _load_icon_safely(self, icon_path: str, size: tuple = (40, 40), color: str = None) -> QIcon:
        """Safely load an icon with optional color change"""
        icon = QIcon()
        try:
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        size[0], size[1], 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    
                    if color:
                        colored_pixmap = QPixmap(scaled_pixmap.size())
                        colored_pixmap.fill(Qt.transparent)
                        
                        painter = QPainter(colored_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                        painter.drawPixmap(0, 0, scaled_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                        painter.fillRect(colored_pixmap.rect(), QColor(color))
                        painter.end()
                        
                        scaled_pixmap = colored_pixmap
                    
                    icon = QIcon(scaled_pixmap)
        except Exception as e:
            print(f"❌ Error loading icon {icon_path}: {e}")
        
        return icon

    def _get_icon_path(self, icon_name: str) -> str:
        """Get the full path to an icon file in the assets directory"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        assets_dir = os.path.join(project_root, "src", "assets")
        return os.path.join(assets_dir, icon_name)

    def _create_load_data_button(self) -> QPushButton:
        """Create the new Load Data button with icon"""
        load_data_icon_path = self._get_icon_path("loading data.png")
        load_data_icon = self._load_icon_safely(load_data_icon_path, (40, 40), "white")
        
        if not load_data_icon.isNull():
            button = QPushButton()
            button.setIcon(load_data_icon)
            button.setIconSize(QSize(40, 40))
            button.setToolTip("Load Data")
        else:
            button = QPushButton("Load Data")
        
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(blue_button_style())
        button.clicked.connect(self._open_load_dialog)
        
        return button

    def _open_load_dialog(self):
        """Open the load courses dialog"""
        dialog = LoadCoursesDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            action = dialog.get_selected_action()
            if action == "local":
                self.load_courses_from_file()
            elif action == "choicefreak":
                self.load_courses_from_choicefreak()

    def showEvent(self, event):
        super().showEvent(event)
        if self._fullscreen_on_start:
            self.showFullScreen()
        elif self._maximize_on_start:
            self.showMaximized()
        # Force layout update every time
        if self.centralWidget() and self.centralWidget().layout():
            self.centralWidget().layout().activate()
            self.centralWidget().updateGeometry()
            self.centralWidget().adjustSize()
        # Force a resize event
        self.resize(self.size())

    def _open_constraint_dialog(self):
        """Open the constraint selection dialog"""
        dialog = ConstraintDialog(self, self.forbidden_slots, self.preferred_slots)
        if dialog.exec_() == QDialog.Accepted:
            forbidden_cells = dialog.get_forbidden()
            self.preferred_slots = dialog.get_preferred()
            self.forbidden_slots = forbidden_cells
            # Update button text to show number of constraints
            count = len(self.forbidden_slots)+ len(self.preferred_slots)
            if count > 0:
                self.constraintBtn.setToolTip(f"Time Constraints ({count} slots)")
            else:
                self.constraintBtn.setToolTip("Set Time Constraints")

    def displayCourses(self, courses: List[Course]):
        """
        Populate the course selector with a list of courses.
        """
        self.courseSelector.populate_courses(courses)

    def handleSelection(self) -> List[Course]:
        """
        Retrieve the list of selected courses from the course selector.
        """
        return self.courseSelector.get_selected_courses()
    
    def navigateToSchedulesWindow(self):
        """
        Handle the event when the user submits their course selection.
        """
        if hasattr(self.courseSelector, 'close_progress_bar'):
            self.courseSelector.close_progress_bar()

        selected = self.handleSelection()
        if selected:
            if len(selected) > 7:
                QMessageBox.warning(self, "Warning", "You cannot select more than 7 courses.")
                return

        # Convert forbidden cells to TimeSlot objects
        forbidden = []
        for row, col in self.forbidden_slots:
            day_index = col + 1  # Sunday=1
            start_time = f"{8+row:02d}:00"
            end_time = f"{8+row+1:02d}:00"
            forbidden.append(TimeSlot(day=str(day_index), start_time=start_time, end_time=end_time, room="", building=""))

        # Convert preferred cells to TimeSlot objects
        preferred = []
        for row, col in self.preferred_slots:
            day_index = col + 1
            start_time = f"{8+row:02d}:00"
            end_time = f"{8+row+1:02d}:00"
            preferred.append(TimeSlot(day=str(day_index), start_time=start_time, end_time=end_time, room="", building=""))

        # Always call on_continue with all three arguments
        self.on_continue(selected, forbidden if forbidden else None, preferred if preferred else None)

    def load_courses_from_file(self):
        """
        Open a file dialog to allow the user to select a course file.
        """
        if hasattr(self.courseSelector, 'close_progress_bar'):
            self.courseSelector.close_progress_bar()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Course File",
            "",
            "Text Files (*.txt);;Excel Files (*.xlsx);;All Files (*)"
        )
        if file_path:
            self.courseSelector.close_progress_bar()
            self.courseSelector._handle_clear()
            self.on_courses_loaded(file_path)  # Trigger the courses loaded callback with the file path

    def open_course_editor_dialog(self):
        all_current_courses = self.courseSelector.get_all_courses()
        editor_dialog = CourseEditorDialog(all_current_courses, self)
        editor_dialog.courseEdited.connect(self._handle_course_edited)

        if editor_dialog.exec_() == QDialog.Accepted:
            pass
        else:
            QMessageBox.information(self, "Cancelled", "Course editing cancelled.")

    def _handle_course_edited(self, edited_course: Course):
        if edited_course:
            QMessageBox.information(self, "Course Saved", f"Course '{edited_course.name}' saved successfully.")
            if self.on_course_added_or_updated:
                self.on_course_added_or_updated(edited_course)

    def load_courses_from_choicefreak(self):
        """Load courses from ChoiceFreak (preserves original functionality)"""
        dialog = ChoiceFreakLoaderDialog(self)
        # Connect the custom signal to a handler method
        dialog.selectionMade.connect(self.on_choicefreak_selection)
        dialog.exec_()  # blocks until dialog closed

    def on_choicefreak_selection(self, university: str, period: str):
        """
        Handle the selection made in the ChoiceFreakLoaderDialog.
        This method should be implemented to fetch courses based on the selected university and period.
        """
        self.courseSelector.show_progress_bar("Loading courses from ChoiceFreak...", "Loading")
        QTimer.singleShot(1000, lambda: self.choicefreakSelectionMade.emit(university, period))
    def _create_time_constraints_button(self) -> QPushButton:
        """Create the time constraints button with thumb up/down icons"""
        # Try to load thumb icons
        thumb_up_path = self._get_icon_path("thumb_up.png")
        thumb_down_path = self._get_icon_path("thumb_down.png")
        
        thumb_up_icon = self._load_icon_safely(thumb_up_path, (25, 25), "white")
        thumb_down_icon = self._load_icon_safely(thumb_down_path, (25, 25), "white")
        
        # If both icons loaded successfully, create combined icon
        if not thumb_up_icon.isNull() and not thumb_down_icon.isNull():
            # Create combined icon with "/" separator
            combined_pixmap = QPixmap(70, 30)  # Width for two icons + separator
            combined_pixmap.fill(Qt.transparent)
            
            painter = QPainter(combined_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw thumb up icon on the left
            thumb_up_pixmap = thumb_up_icon.pixmap(25, 25)
            painter.drawPixmap(5, 2, thumb_up_pixmap)
            
            # Draw separator "/"
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Arial", 16, QFont.Bold))
            painter.drawText(32, 20, "/")
            
            # Draw thumb down icon on the right
            thumb_down_pixmap = thumb_down_icon.pixmap(25, 25)
            painter.drawPixmap(42, 2, thumb_down_pixmap)
            
            painter.end()
            
            # Create button with combined icon
            button = QPushButton()
            button.setIcon(QIcon(combined_pixmap))
            button.setIconSize(QSize(70, 30))
            button.setToolTip("Set Time Constraints")
        else:
            # Fallback to text if icons failed to load
            button = QPushButton("Set Time Constraints")
    
        return button
    def _create_constraint_button(self):
        """Create and setup the time constraints button"""
        self.constraintBtn = self._create_time_constraints_button()
        self.constraintBtn.clicked.connect(self._open_constraint_dialog)
        self.constraintBtn.setCursor(Qt.PointingHandCursor)
        self.constraintBtn.setStyleSheet(blue_button_style())
        return self.constraintBtn
    def _create_user_guide_button(self) -> QPushButton:
        """Create the user guide info button with icon"""
        # Try to load info icon
        info_icon_path = self._get_icon_path("info.png")  # You'll need to add this icon
        info_icon = self._load_icon_safely(info_icon_path, (30, 30), "white")
        
        if not info_icon.isNull():
            button = QPushButton()
            button.setIcon(info_icon)
            button.setIconSize(QSize(30, 30))
            button.setToolTip("User Guide & Instructions")
        else:
            # Fallback to info emoji if icon not found
            button = QPushButton("ℹ️")
            button.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    min-width: 40px;
                    min-height: 40px;
                }
            """)
        
        # Style the button
        button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(self._open_user_guide)
        
        return button

    def _open_user_guide(self):
        """Open the user guide dialog"""
        dialog = UserGuideDialog(self)
        dialog.exec_()