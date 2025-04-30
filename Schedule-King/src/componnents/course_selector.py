from PyQt5.QtWidgets import (QListWidget, QAbstractItemView, QListWidgetItem,
                     QVBoxLayout, QPushButton, QWidget, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSizePolicy, QLabel, QFrame
from typing import List
from src.models.course import Course


class CourseSelector(QWidget):
    """
    A custom widget that allows users to select courses from a list,
    submit their selection, or clear all selections.
    """
    
    # Define custom signals
    coursesSelected = pyqtSignal(list)  # Signal emitted when course selection changes
    coursesSubmitted = pyqtSignal(list)  # Signal emitted when submission button is clicked
    
    def __init__(self, parent=None):
        """
        Initialize the CourseSelector widget with custom styles and settings.
        
        Args:
            parent: The parent widget (optional).
        """
        super().__init__(parent)
        
        # Set the overall widget background
        self.setStyleSheet("""
            QWidget {
                background-color: #F0F7FF;  /* Light blue background */
                border-radius: 15px;
            }
        """)
        
        # Create the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)  # Increase margins slightly
        self.layout.setSpacing(10)  # Reduce spacing between widgets
        
        # Add a title label
        self.title_label = QLabel("Available Courses")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #1A237E;
                font-size: 18pt;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        
        # Add a separator line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.separator.setStyleSheet("background-color: #C5CAE9;")
        self.layout.addWidget(self.separator)
        
        # Create the list widget
        self.list_widget = QListWidget()
        
        # Set selection mode to allow multiple selections
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

        
        # Optimize item rendering by using uniform item sizes
        self.list_widget.setUniformItemSizes(True)
        
        # Set spacing between items
        self.list_widget.setSpacing(6)
        
        # Make the widget resize dynamically with the window
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the font for the list widget
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Medium)
        self.list_widget.setFont(font)

        # Apply custom styles using a stylesheet
        self.list_widget.setStyleSheet("""
            QListWidget::item:selected {
                background-color: #5C6BC0;  /* Indigo color */
                color: white;
                border: 1px solid #3949AB;
                border-radius: 8px;
            }
            QListWidget::item:hover {
                background-color: #9FA8DA;  /* Lighter indigo */
                color: #1A237E;
            }
            QListWidget {
                padding: 15px;
                border: 2px solid #C5CAE9;
                border-radius: 12px;
                background-color: #E8EAF6;  /* Light indigo background */
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
        """)
        
        # Add the list widget to the layout
        self.layout.addWidget(self.list_widget)
        
        # Add a spacer to push buttons to the bottom
        # self.layout.addStretch(1)
        
        # Create a horizontal layout for buttons with right alignment
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)  # Push buttons to the right
        
        # Create Submit button
        self.submit_button = QPushButton("Submit Selection")
        self.submit_button.setCursor(Qt.PointingHandCursor)  # Change cursor to hand when hovering
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5;  /* Indigo */
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
            QPushButton:pressed {
                background-color: #1A237E;
            }
        """)
        
        # Create Clear All button
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setCursor(Qt.PointingHandCursor)  # Change cursor to hand when hovering
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;  /* Red */
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
        """)
        
        # Add buttons to the button layout
        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.submit_button)
        
        # Add the button layout to the main layout with minimal space
        self.layout.addLayout(self.button_layout)
        
        # Initialize the list of courses
        self.courses = []
        
        # Connect signals to slots
        self.list_widget.itemSelectionChanged.connect(self._handle_selection_changed)
        self.submit_button.clicked.connect(self._handle_submit)
        self.clear_button.clicked.connect(self._handle_clear)
    
    def populate_courses(self, courses: List):
        """
        Populate the list widget with course items.
        
        Args:
            courses: List of Course objects to display.
        """
        # Clear existing items in the list widget
        self.list_widget.clear()
        
        # Store the provided courses
        self.courses = courses
        
        # Add each course to the list widget
        for course in courses:
            # Create display text with course code and name
            display_text = f"{course.course_code} - {course.name}"
            
            # Create a list item with the display text
            item = QListWidgetItem(display_text)
            
            # Store the course index as item data for reference
            item.setData(Qt.UserRole, self.courses.index(course))
            
            # Add the item to the list widget
            self.list_widget.addItem(item)
        
        # Update the title with course count
        self.title_label.setText(f"Available Courses ({len(courses)})")

    def _handle_selection_changed(self):
        """
        Handle the selection change and emit the coursesSelected signal
        with the list of selected Course objects.
        """
        # Initialize a list to store selected courses
        selected_courses = self.get_selected_courses()
        
        # Update title to show selection count
        if selected_courses:
            self.title_label.setText(f"Available Courses ({len(selected_courses)} selected)")
        else:
            self.title_label.setText(f"Available Courses ({len(self.courses)} total)")
            
        # Emit the signal with the selected courses
        self.coursesSelected.emit(selected_courses)
    
    def _handle_submit(self):
        """
        Handle the submit button click and emit the coursesSubmitted signal
        with the list of selected Course objects.
        """
        # Get the selected courses
        selected_courses = self.get_selected_courses()
        
        # Emit the signal with the selected courses
        self.coursesSubmitted.emit(selected_courses)
    
    def _handle_clear(self):
        """
        Handle the clear button click by clearing all selections.
        """
        # Clear all selections
        self.list_widget.clearSelection()
        
        # Reset the title
        self.title_label.setText(f"Available Courses ({len(self.courses)} total)")
        
        # Emit the selection changed signal with an empty list
        self.coursesSelected.emit([])

    def get_selected_courses(self) -> List[Course]:
        """
        Get the currently selected Course objects.
        
        Returns:
            List of selected Course objects.
        """
        # Initialize a list to store selected courses
        selected_courses: List[Course] = []
        
        # Iterate through all selected items
        for item in self.list_widget.selectedItems():
            # Get the course index from the item data
            index = item.data(Qt.UserRole)
            
            # Add the corresponding Course object to the list if valid
            if 0 <= index < len(self.courses):
                selected_courses.append(self.courses[index])
        
        return selected_courses
        
    def set_selected_courses(self, course_numbers: List[str]):
        """
        Set specific courses as selected based on their course numbers.
        
        Args:
            course_numbers: List of course numbers to select.
        """
        # Clear the current selection
        self.list_widget.clearSelection()
        
        # Iterate through all items in the list widget
        for i in range(self.list_widget.count()):
            # Get the item at the current index
            item = self.list_widget.item(i)
            
            # Get the course index from the item data
            index = item.data(Qt.UserRole)
            
            # Get the course at this index
            if 0 <= index < len(self.courses):
                course = self.courses[index]
                
                # Select the item if its course number is in the list
                if course.number in course_numbers:
                    item.setSelected(True)
        
        # Update title to show selection count
        selected_count = len(self.get_selected_courses())
        if selected_count > 0:
            self.title_label.setText(f"Available Courses ({selected_count} selected)")


# main for testing purposes TODO: remove this when integrating into the main application
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    # Sample data
    sample_courses = [
        Course("Introduction to Computer Science", "CS101", "Dr. Smith"),
        Course("Calculus II", "MATH202", "Dr. Johnson"),
        Course("Physics I", "PHYS101", "Dr. Brown"),
        Course("Technical Writing", "ENG205", "Dr. Taylor"),
        Course("Data Structures", "CS202", "Dr. Davis")
    ]
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the CourseSelector
    selector = CourseSelector()
    selector.populate_courses(sample_courses)
    selector.show()
    
    # Example of connecting to the coursesSubmitted signal
    def on_courses_submitted(courses):
        print("Courses submitted:")
        for course in courses:
            print(f"- {course.course_code}: {course.name}")
    
    selector.coursesSubmitted.connect(on_courses_submitted)

    # Run the application event loop
    sys.exit(app.exec_())