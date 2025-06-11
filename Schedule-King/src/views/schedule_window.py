from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QFileDialog, QMessageBox,
    QHBoxLayout, QFrame, QPushButton, QSpacerItem, QSizePolicy, QProgressBar, QLabel, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QPixmap
from src.components.navigator import Navigator
from src.components.schedule_table import ScheduleTable
from src.components.schedule_header import ScheduleHeader
from src.components.schedule_progress import ScheduleProgress
from src.components.full_size_window import FullSizeWindow
from src.components.ScheduleMetrics import ScheduleMetrics
from src.models.schedule import Schedule
from src.controllers.ScheduleController import ScheduleController
from src.components.ranking_controls import RankingControls
from typing import List, Optional
import os

class ScheduleWindow(QMainWindow):
    """
    Main window for displaying and managing generated schedules.
    Uses modular components for better maintainability.
    """
    def __init__(self, controller: ScheduleController, maximize_on_start=True, show_progress_on_start=True):
        super().__init__()
        self.setup_window()  # Set up window properties and layout
        self.setup_components(-1, controller)  # Set up all UI components
        self.setup_connections()  # Connect signals and slots
        self.setWindowState(Qt.WindowMaximized)
        self.show()

    def setup_window(self):
        """Initialize window properties and layout"""
        # Set window properties
        self.setObjectName("ScheduleWindow")
        self.setWindowTitle("Schedule King")
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Create main layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.setCentralWidget(self.central_widget)
        
        # Set window size
        self.setMinimumSize(800, 600)
        self.resize(1920, 1080)
        
    def setup_components(self, schedules: int , controller: ScheduleController):
        """Initialize and setup all window components"""
        # Store references
        self.controller = controller
        self.schedules = schedules
        self.first_schedule_shown = False
        self.full_size_window = None
        self.on_back = lambda: None  # Default no-op callback for navigation back to course selection

        # Create header and metrics components
        # ScheduleHeader components (back_button, title_container, export_controls) are now public attributes
        self.header = ScheduleHeader(self.controller, self.handle_export)
        self.metrics_widget = ScheduleMetrics(Schedule([])) # Initialize with empty schedule

        # Create a horizontal layout for the top section (Back, Header Title, Metrics, Export)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Add Back button
        top_layout.addWidget(self.header.back_button)

        # Add Header Title container and center it with stretches
        top_layout.addStretch(1)
        top_layout.addWidget(self.header.title_container)
        top_layout.addStretch(1)

        # Add Metrics widget
        top_layout.addWidget(self.metrics_widget)

        # Add Export controls
        top_layout.addWidget(self.header.export_controls)

        # Add the top layout to the main vertical layout (wrap in QWidget for styling if needed)
        top_widget_container = QWidget()
        top_widget_container.setObjectName("schedule_top_bar") # Add object name for styling if needed
        top_widget_container.setLayout(top_layout)
        self.main_layout.addWidget(top_widget_container)

        # Add separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("separator_line")
        self.main_layout.addWidget(line)

        # Create navigation section (progress, navigator, ranking controls, full size, refresh)
        nav_container = QHBoxLayout()
        nav_container.setSpacing(10)

        # Add progress component
        self.progress = ScheduleProgress()
        nav_container.addWidget(self.progress)

        # Add navigator
        self.navigator = Navigator(-1)
        self.navigator.setObjectName("compact_navigator")
        nav_container.addWidget(self.navigator)

        # Add ranking controls
        self.ranking_controls = RankingControls()
        self.ranking_controls.setObjectName("ranking_controls")
        nav_container.addWidget(self.ranking_controls)

        # Add full size button
        self.full_size_button = QPushButton()
        self.full_size_button.setObjectName("nav_button")
        self.full_size_button.setFixedSize(36, 36)
        full_size_icon = QIcon(os.path.join(os.path.dirname(__file__), "../assets/full_size.png"))
        if not full_size_icon.isNull():
            self.full_size_button.setIcon(full_size_icon)
            self.full_size_button.setIconSize(self.full_size_button.size())
            self.full_size_button.setText("")
        else:
            self.full_size_button.setText("⛶")
            self.full_size_button.setFont(QFont("Arial", 14))

        nav_container.addSpacing(10)
        nav_container.addWidget(self.full_size_button)

        # Add refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.setObjectName("nav_button") # Use same object name for styling consistency
        self.refresh_button.setFixedSize(36, 36)
        refresh_icon_path = os.path.join(os.path.dirname(__file__), "../assets/refresh.png")
        refresh_icon = QIcon(refresh_icon_path)
        if not refresh_icon.isNull():
            self.refresh_button.setIcon(refresh_icon)
            self.refresh_button.setIconSize(self.refresh_button.size())
            self.refresh_button.setText("")
        else:
            self.refresh_button.setText("↻") # Fallback text
            self.refresh_button.setFont(QFont("Arial", 14))

        nav_container.addWidget(self.refresh_button)

        # Add dummy spacer to balance progress width
        dummy = QSpacerItem(250, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        nav_container.addSpacerItem(dummy)

        # Center the navigation section
        wrapper = QHBoxLayout()
        wrapper.addStretch(1)
        wrapper.addLayout(nav_container)
        wrapper.addStretch(1)
        self.main_layout.addLayout(wrapper)

        # Create schedule table (Keep existing setup)
        self.schedule_table = ScheduleTable()
        self.schedule_table.setObjectName("enhanced_table")
        self.main_layout.addWidget(self.schedule_table, 1)
        
    def setup_connections(self):
        """Setup signal connections between components"""
        # Connect navigator signals
        self.navigator.schedule_changed.connect(self.on_schedule_changed)
        
        # Connect header buttons
        self.header.back_button.clicked.connect(self.navigateToCourseWindow)
        
        # Connect full size button
        self.full_size_button.clicked.connect(self.open_full_size)
        
        # Connect refresh button
        self.refresh_button.clicked.connect(self.on_refresh_button_clicked)
        
        # Connect controller callbacks
        self.controller.on_schedules_generated = self.on_schedule_generated
        self.controller.on_progress_updated = self.progress.update_progress

        # Connect ranking controls to controller
        self.ranking_controls.preference_changed.connect(self.on_preference_changed)
        
    def show_initial_schedule(self):
        """Display the first schedule if available"""
        # Force window to be maximized

        self.setWindowState(Qt.WindowMaximized)
        
    # Properties for backward compatibility with tests
    @property
    def export_button(self):
        """Access to export button for backward compatibility"""
        return self.header.export_controls.export_button
        
    @property
    def back_button(self):
        """Access to back button for backward compatibility"""
        return self.header.back_button
        
    @property
    def export_visible_only(self):
        """Access to export checkbox for backward compatibility"""
        return self.header.export_controls.export_visible_only
        
    def displaySchedules(self, schedules: List[Schedule]):
        """
        Updates the navigator and table with new schedules.
        For backward compatibility.
        """
        self.schedules = schedules
        self.navigator.set_schedules(schedules)
        if schedules:
            self.on_schedule_changed(0)
            # Enable refresh button if schedules are displayed
            self.refresh_button.setEnabled(True)
        else:
            self.schedule_table.clearContents()
            # Update export controls with empty data
            self.header.export_controls.update_data([], 0)
            # Disable refresh button if no schedules are displayed
            self.refresh_button.setEnabled(False)

    def on_schedule_changed(self, index: int):
        """
        Handle schedule change event from navigator and preference controls.
        Updates the table, metrics, and export controls.
        """
        if 0 <= index < self.schedules:
            try:
                # Get the ranked schedule based on current preference
                schedule = self.controller.get_kth_schedule(index)
                self.current_schedule = schedule  # Store current schedule for full size window
                self.schedule_table.display_schedule(schedule)
                # Update export controls with current schedules and index
                self.header.export_controls.update_data(index)
                self.header.export_controls.export_button.setEnabled(True)
                self.header.back_button.setEnabled(True)

                # Update the metrics widget with the new schedule data
                # Find the top layout containing the metrics widget
                top_widget_container = self.main_layout.itemAt(0).widget()
                if top_widget_container and isinstance(top_widget_container.layout(), QHBoxLayout):
                    top_layout = top_widget_container.layout()

                    # Remove the old metrics widget from its parent layout
                    # Check if the old metrics widget is still in the layout before removing
                    if top_layout.indexOf(self.metrics_widget) != -1:
                         top_layout.removeWidget(self.metrics_widget)
                         # Delete the old widget to free up resources
                         self.metrics_widget.deleteLater()

                # Create a new metrics widget with the updated schedule
                self.metrics_widget = ScheduleMetrics(schedule)

                # Add the new metrics widget to the top layout
                if top_widget_container and isinstance(top_widget_container.layout(), QHBoxLayout):
                    top_layout = top_widget_container.layout()
                    # Insert at index 3 (after back_button, title_container_stretch, title_container_widget, title_container_stretch)
                    top_layout.insertWidget(3, self.metrics_widget) # Insert at index 3

                # Enable the refresh button since a schedule is displayed
                self.refresh_button.setEnabled(True)

            except IndexError:
                self.schedule_table.clearContents()
                self.header.export_controls.update_data(0)
                self.header.export_controls.export_button.setEnabled(False)
                self.header.back_button.setEnabled(False)
                # Disable the refresh button when there's an error or no schedules
                self.refresh_button.setEnabled(False)
        
    def on_schedule_generated(self, schedules_num: int = 0):
        """
        Handle new schedule generation.
        Updates the navigator, table, and export controls.
        """
        self.navigator.set_schedules(schedules_num)
        if self.schedules != schedules_num:
            self.schedules = schedules_num
            if schedules_num > 0 and not self.first_schedule_shown:
                self.navigator.current_index = 0
                self.on_schedule_changed(0)
                self.first_schedule_shown = True
                # Enable refresh button if schedules are generated
                self.refresh_button.setEnabled(True)
            elif schedules_num <= 0:
                self.schedule_table.clearContents()
                # Update export controls with empty data
                self.header.export_controls.update_data(0)
                # Disable refresh button if no schedules are generated
                self.refresh_button.setEnabled(False)
                
        if not self.controller.generation_active and  schedules_num<=0:
            self.progress.hide_progress()

    def on_preference_changed(self, metric, ascending):
        """
        Handle changes in ranking preferences.
        Updates the controller and refreshes the schedule display.
        """
        if metric is None:
            # Clear preference
            self.controller.clear_preference()
        else:
            # Set new preference
            self.controller.set_preference(metric, ascending)
        
        # Refresh the schedules display
        if self.navigator.current_index < self.schedules:
            self.on_schedule_changed(self.navigator.current_index)
            
    def navigateToCourseWindow(self):
        """
        Navigate back to course selection.
        Stops schedule generation and hides progress.
        """
        self.controller.stop_schedules_generation()
        self.progress.hide_progress()
        self.on_back()
        
    def handle_export(self, file_path: str, schedules_to_export: Optional[List[Schedule]]):
        """
        Handle export request from ExportControls.
        Calls the controller's export method.
        """
        if not self.schedules or self.navigator.current_index >= self.schedules:
            QMessageBox.warning(self, "No Schedule", "No schedule is currently selected.")
            return
            
        if schedules_to_export is None:
            # Export only the currently displayed schedule
            self.controller.export_schedules(file_path, [self.current_schedule])
        else:
            # Export specific schedules
            self.controller.export_schedules(file_path, schedules_to_export)
                
    def open_full_size(self):
        """
        Open current schedule in full-size window.
        Shows a warning if no schedule is selected.
        """
        if not self.schedules or self.navigator.current_index >= self.schedules:
            QMessageBox.warning(self, "No Schedule", "No schedule is currently selected.")
            return
            
        if self.full_size_window is not None:
            self.full_size_window.close()
            
        self.full_size_window = FullSizeWindow(
            self.current_schedule,
            self.navigator.current_index
        )

    def on_refresh_button_clicked(self):
        """
        Handle refresh button click: reload the current schedule.
        Only attempts to refresh if there are schedules to display.
        """
        current_index = self.navigator.current_index
        # Only attempt to refresh if there are schedules to display
        if 0 <= current_index < self.schedules:
            self.on_schedule_changed(current_index)
        # No else needed, as the button should be disabled if there are no schedules