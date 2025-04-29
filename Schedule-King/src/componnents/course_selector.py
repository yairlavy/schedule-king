from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSizePolicy
from typing import List
from src.models.course import Course


class CourseSelector(QListWidget):
    """
    A custom QListWidget component that allows users to select courses
    from a list and emits signals when selections change.
    """
    
    # Define custom signals
    coursesSelected = pyqtSignal(list)  # Signal emitted when course selection changes
    
    def __init__(self, parent=None):
        """
        Initialize the CourseSelector widget with custom styles and settings.
        
        Args:
            parent: The parent widget (optional).
        """
        super().__init__(parent)

        # Set selection mode to allow multiple selections
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        
        # Enable alternating row colors for better readability
        self.setAlternatingRowColors(True)
        
        # Optimize item rendering by using uniform item sizes
        self.setUniformItemSizes(True)
        
        # Set spacing between items
        self.setSpacing(5)
        
        # Make the widget resize dynamically with the window
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set the font for the list widget
        font = QFont("Segoe UI", 11)
        self.setFont(font)

        # Apply custom styles using a stylesheet
        self.setStyleSheet("""
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #388E3C;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #C8E6C9;
                color: black;
            }
            QListWidget {
                padding: 12px;
                border: 2px solid #BDBDBD;
                border-radius: 12px;
                background-color: #F5F5F5;
                font-size: 12pt;
                color: #424242;
            }
            QListWidget::item {
                padding: 10px;
                margin: 6px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                background-color: #FFFFFF;
            }
            QListWidget::item:!selected {
                background-color: #FAFAFA;
            }
        """)

        # Initialize the list of courses
        self.courses = []
        
        # Connect the item selection change signal to the handler
        self.itemSelectionChanged.connect(self._handle_selection_changed)

    def populate_courses(self, courses: List):
        """
        Populate the list widget with course items.
        
        Args:
            courses: List of Course objects to display.
        """
        # Clear existing items in the list widget
        self.clear()
        
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
            self.addItem(item)

    def _handle_selection_changed(self):
        """
        Handle the selection change and emit the coursesSelected signal
        with the list of selected Course objects.
        """
        # Initialize a list to store selected courses
        selected_courses = []
        
        # Iterate through all selected items
        for item in self.selectedItems():
            # Get the course index from the item data
            index = item.data(Qt.UserRole)
            
            # Add the corresponding Course object to the list if valid
            if 0 <= index < len(self.courses):
                selected_courses.append(self.courses[index])
        
        # Emit the signal with the selected courses
        self.coursesSelected.emit(selected_courses)

    def get_selected_courses(self) -> List:
        """
        Get the currently selected Course objects.
        
        Returns:
            List of selected Course objects.
        """
        # Initialize a list to store selected courses
        selected_courses = []
        
        # Iterate through all selected items
        for item in self.selectedItems():
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
        self.clearSelection()
        
        # Iterate through all items in the list widget
        for i in range(self.count()):
            # Get the item at the current index
            item = self.item(i)
            
            # Get the course index from the item data
            index = item.data(Qt.UserRole)
            
            # Get the course at this index
            if 0 <= index < len(self.courses):
                course = self.courses[index]
                
                # Select the item if its course number is in the list
                if course.number in course_numbers:
                    item.setSelected(True)


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

    # Run the application event loop
    sys.exit(app.exec_())
