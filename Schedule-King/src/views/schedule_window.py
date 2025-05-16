from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox,
    QHBoxLayout, QLabel, QFrame, QProgressBar, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont , QTransform
from src.components.navigator import Navigator
from src.components.schedule_table import ScheduleTable
from src.models.schedule import Schedule
from src.controllers.ScheduleController import ScheduleController
from typing import List, Callable
import os
from src.models.course import Course
from PyQt5.QtWidgets import QProgressDialog

class ScheduleWindow(QMainWindow):
    """
    An improved window for displaying and managing generated schedules.
    Features a modern UI with icons, better layout, and enhanced visual design.
    """
    def __init__(self, schedules: List[Schedule], controller: ScheduleController):
        """
        Initializes the ScheduleWindow with enhanced UI.

        Args:
            schedules (List[Schedule]): List of schedules to display.
            controller (ScheduleController): Controller for schedule operations.
        """
        super().__init__()
        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Set window properties
        self.setObjectName("ScheduleWindow")
        self.setWindowTitle("Schedule King")
        self.showMaximized()  # Start maximized for better visibility
        self.controller = controller  # Store controller for operations
        self.schedules = schedules    # Store list of schedules
        self.course_selector_ref = None # Reference to the course selector window
        self.on_back = lambda: None  # Default no-op callback for navigation back to course selection
        self.controller.on_schedules_generated = self.on_schedule_generated
        self.controller.on_progress_updated = self.update_progress
        
        # Initialize progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("schedule_progress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m schedules")
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setVisible(False)  # Initially hidden
        
        # Initialize progress label
        self.progress_label = QLabel("Generating schedules...")
        self.progress_label.setObjectName("progress_label")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setVisible(False)  # Initially hidden
        
        # --- MAIN LAYOUT SETUP ---
        # Create the main container widget and layout with proper spacing
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)  # Space between major sections
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # Margins around the window
        
        # --- HEADER SECTION ---
        # The header is divided into three sections: back button (left), title (center), export button (right)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Left section: Back button with icon
        self.back_button = QPushButton("  Back to Course Selection")
        self.back_button.setObjectName("top_action_button")
        back_icon = QIcon(os.path.join(os.path.dirname(__file__), "../assets/back.png"))
        if not back_icon.isNull():
            self.back_button.setIcon(back_icon)
            self.back_button.setText(" Back to Course Selection")
        else:
            self.back_button.setText("← Back to Course Selection")
        
        # Center section: Title with crown icon and subtitle
        title_container = QWidget()
        title_container.setObjectName("title_container")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(15, 10, 15, 10)
        title_layout.setSpacing(0)
        
        # Create crown icon (or emoji fallback) for the title
        crown_label = QLabel()
        crown_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "../assets/king.png"))
        if not crown_pixmap.isNull():
            crown_label.setPixmap(crown_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            crown_label = QLabel("👑")
            crown_label.setFont(QFont("Segoe UI Emoji", 36))
        
        crown_label.setAlignment(Qt.AlignCenter)
        crown_label.setMaximumWidth(60)  # Larger crown
        
        # Title and subtitle
        title_text_layout = QVBoxLayout()
        self.headline = QLabel("Schedule King")
        self.headline.setObjectName("headline_label")
        self.headline.setFont(QFont("Arial", 24, QFont.Bold))  # Larger font for headline
        
        self.subtitle = QLabel("Plan Your Study Schedule Like a King")
        self.subtitle.setObjectName("subtitle_label")
        self.subtitle.setFont(QFont("Arial", 16))  # Larger font for subtitle
        
        title_text_layout.addWidget(self.headline)
        title_text_layout.addWidget(self.subtitle)
        
        # Add crown and text to title container
        title_row = QHBoxLayout()
        title_row.addWidget(crown_label)
        title_row.addLayout(title_text_layout)
        title_row.addStretch(1)
        title_layout.addLayout(title_row)
        
        # Export button (right side)
        export_container = QWidget()
        export_layout = QVBoxLayout(export_container)
        export_layout.setSpacing(5)
        
        self.export_button = QPushButton("  Export Schedule")
        self.export_button.setObjectName("top_action_button")
        export_icon = QIcon(os.path.join(os.path.dirname(__file__), "../assets/export.png"))
        if not export_icon.isNull():
            self.export_button.setIcon(export_icon)
        else:
            # Use text-based icon as fallback
            self.export_button.setText("Export Schedule")
            
        self.export_visible_only = QCheckBox("Export visible schedule only")
        self.export_visible_only.setObjectName("export_checkbox")
        
        export_layout.addWidget(self.export_button)
        export_layout.addWidget(self.export_visible_only)
        
        # Assemble header with proper alignment
        header_layout.addWidget(self.back_button)  # Left aligned
        header_layout.addStretch(1)  # Push to left
        header_layout.addWidget(title_container)  # Center
        header_layout.addStretch(1)  # Push to right
        header_layout.addWidget(export_container)  # Right aligned
        
        self.main_layout.addLayout(header_layout)
        
        # Connect button actions
        self.export_button.clicked.connect(self.export_to_file)
        self.back_button.clicked.connect(self.navigateToCourseWindow)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("separator_line")
        self.main_layout.addWidget(line)
        
        # --- NAVIGATION SECTION ---
        # Create the navigator component for browsing through schedules
        self.navigator = Navigator(schedules)
        self.navigator.setObjectName("compact_navigator")
        
        # Connect navigator's schedule change signal to update the table
        self.navigator.schedule_changed.connect(self.on_schedule_changed)
        
        # Add the navigator to the main layout
        self.main_layout.addWidget(self.navigator)

        # --- PROGRESS BAR SECTION ---
        progress_container = QVBoxLayout()
        progress_container.setContentsMargins(10, 0, 10, 10)
        progress_container.setSpacing(5)
        
        # Add progress elements to container
        progress_container.addWidget(self.progress_label, alignment=Qt.AlignCenter)
        progress_container.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # Add both navigation and progress sections to main layout
        self.main_layout.addLayout(progress_container)
        
        
        # --- SCHEDULE TABLE ---
        # Create the main schedule display table
        self.schedule_table = ScheduleTable()
        self.schedule_table.setObjectName("enhanced_table")
        
        # Add the schedule table to the main layout with stretch factor 1
        # This makes it take up most of the available vertical space
        self.main_layout.addWidget(self.schedule_table, 1)

        # Set the central widget of the main window
        self.setCentralWidget(self.central_widget)
        
        # Display the first schedule if available
        if schedules:
            self.on_schedule_changed(0)

    def update_progress(self, current: int, estimated: int):
        """
        Updates the progress bar with the current and estimated schedule counts.
        """
        # Ensure progress bar exists
        if not hasattr(self, 'progress_bar') or self.progress_bar is None:
            print("Reinitializing progress bar...")
            self.progress_bar = QProgressBar()
            self.progress_bar.setObjectName("schedule_progress")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setFormat("%v / %m schedules")
            self.progress_bar.setFixedWidth(300)
            
            # Add to layout if not already there
            if not self.progress_bar.parent():
                progress_container = self.findChild(QVBoxLayout, "progress_container")
                if progress_container:
                    progress_container.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
                else:
                    print("Warning: Could not find progress container")

        # Ensure progress label exists
        if not hasattr(self, 'progress_label') or self.progress_label is None:
            print("Reinitializing progress label...")
            self.progress_label = QLabel("Generating schedules...")
            self.progress_label.setObjectName("progress_label")
            self.progress_label.setAlignment(Qt.AlignCenter)
            
            # Add to layout if not already there
            if not self.progress_label.parent():
                progress_container = self.findChild(QVBoxLayout, "progress_container")
                if progress_container:
                    progress_container.addWidget(self.progress_label, alignment=Qt.AlignCenter)
                else:
                    print("Warning: Could not find progress container")

        try:
            if estimated > 0:
                self.progress_bar.setMaximum(estimated)
                self.progress_bar.setValue(current)
                self.progress_label.setText(f"Generating schedules... ({current}/{estimated})")
                self.progress_label.setVisible(True)
                self.progress_bar.setVisible(True)
            else:
                self.progress_bar.setMaximum(0)
                self.progress_label.setText(f"Generating schedules... ({current} generated)")
                self.progress_label.setVisible(True)
                self.progress_bar.setVisible(True)
                
            # Force update the UI
            self.progress_bar.repaint()
            self.progress_label.repaint()
        except Exception as e:
            print(f"Error updating progress: {str(e)}")
            # Try to recover by reinitializing
            self.progress_bar = None
            self.progress_label = None

    def on_schedule_generated(self, schedules: List[Schedule]):
        """
        Updates the UI when new schedules are generated.
        This method is called by the controller during schedule generation.
        """
        # Always update the navigator to refresh the count display
        self.navigator.set_schedules(schedules)
        
        # Only update schedules and current display if they've actually changed
        if self.schedules != schedules:
            self.schedules = schedules
            
            # Only update current schedule if we don't have one displayed
            if schedules and self.navigator.current_index == -1:
                self.navigator.current_index = 0
                self.on_schedule_changed(0)
            elif not schedules:
                self.schedule_table.clearContents()

    def displaySchedules(self, schedules: List[Schedule]):
        """Updates the navigator and table with new schedules."""
        self.schedules = schedules
        self.navigator.set_schedules(schedules)
        if not schedules:
            self.schedule_table.clearContents()

    def navigateToCourseWindow(self):
        """Navigates back to the course selection window."""
        # Close any progress bar if it was used
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
        self.on_back()

    def export_to_file(self):
        """
        Exports schedules to a file in the selected format.
        Shows success/error messages to the user.
        """
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Schedules", "", 
            "Text Files (*.txt);;Excel Files (*.xlsx);;All Files (*)"
        )
        if file_path:
            # Add extension based on selected filter if not already present
            if selected_filter == "Text Files (*.txt)" and not file_path.endswith('.txt'):
                file_path += '.txt'
            elif selected_filter == "Excel Files (*.xlsx)" and not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            try:
                # Get current schedule index from navigator
                current_index = self.navigator.current_index
                
                # Use the controller to handle the export
                if self.export_visible_only.isChecked() and 0 <= current_index < len(self.schedules):
                    # Export only the visible schedule
                    self.controller.export_schedules(file_path, [self.schedules[current_index]])
                else:
                    # Export all schedules
                    if file_path.endswith('.xlsx') and len(self.schedules) > 100:
                        # Export to Excel only the last 100 schedules - excel import is slow
                        QMessageBox.warning(
                            self, "excel Export Warning",
                            "Exporting only the last 100 schedules to Excel for performance reasons."
                        )   
                        self.controller.export_schedules(file_path, self.schedules[current_index:current_index+100])
                    else:
                        self.controller.export_schedules(file_path)
                    
                QMessageBox.information(
                    self, "Export Successful",
                    f"Schedules were saved successfully to:\n{file_path}"
                )
            except Exception as e:
                error_msg = str(e)
                print(f"Export error: {error_msg}")  # Log the error
                QMessageBox.critical(
                    self, "Export Failed",
                    f"Failed to export schedules:\n{error_msg}"
                )
    def on_schedule_changed(self, index: int):
        """
        Updates the schedule table when the selected schedule changes.
        This is called when the user navigates to a different schedule.
        """
        if 0 <= index < len(self.schedules):
            self.schedule_table.display_schedule(self.schedules[index])
        self.export_button.setEnabled(True)
        self.back_button.setEnabled(True)
