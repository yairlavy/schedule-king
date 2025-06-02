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
    def __init__(self, schedules: List[Schedule], controller: ScheduleController, maximize_on_start=True, show_progress_on_start=True):
        super().__init__()
        self.setup_window()
        self.setup_components(schedules, controller)
        self.setup_connections()
        self.show_initial_schedule(schedules)
        
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
        
    def setup_components(self, schedules: List[Schedule], controller: ScheduleController):
        """Initialize and setup all window components"""
        # Store references
        self.controller = controller
        self.schedules = schedules
        self.first_schedule_shown = False
        self.full_size_window = None
        self.on_back = lambda: None  # Default no-op callback for navigation back to course selection
        
        # Create header with export handler
        self.header = ScheduleHeader(self.controller,self.handle_export)
        self.main_layout.addWidget(self.header)
        self.metrics_widget = ScheduleMetrics(schedules[0] if schedules else Schedule([]))

        # Create top bar with back button, metrics and export controls
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(15)

        # Back button
        top_bar.addWidget(self.header.back_button)

        # Metrics (centered with stretch)
        self.metrics_widget = ScheduleMetrics(schedules[0] if schedules else Schedule([]))
        top_bar.addStretch(1)
        top_bar.addWidget(self.metrics_widget)
        top_bar.addStretch(1)

        # Export controls
        export_controls_layout = QVBoxLayout()
        export_controls_layout.addWidget(self.header.export_controls.export_button)
        export_controls_layout.addWidget(self.header.export_controls.export_visible_only)
        top_bar.addLayout(export_controls_layout)

        # Wrap everything in a container and add to layout
        top_bar_container = QWidget()
        top_bar_container.setLayout(top_bar)
        self.main_layout.addWidget(top_bar_container)

        # Add separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("separator_line")
        self.main_layout.addWidget(line)
        
        # Create navigation section
        nav_container = QHBoxLayout()
        nav_container.setSpacing(10)
        
        # Add progress component
        self.progress = ScheduleProgress()
        nav_container.addWidget(self.progress)
        
        # Add navigator
        self.navigator = Navigator(schedules)
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
        
        # Add dummy spacer to balance progress width
        dummy = QSpacerItem(250, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        nav_container.addSpacerItem(dummy)
        
        # Center the navigation section
        wrapper = QHBoxLayout()
        wrapper.addStretch(1)
        wrapper.addLayout(nav_container)
        wrapper.addStretch(1)
        self.main_layout.addLayout(wrapper)
        
        # Create schedule table
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
        
        # Connect controller callbacks
        self.controller.on_schedules_generated = self.on_schedule_generated
        self.controller.on_progress_updated = self.progress.update_progress

        # Connect ranking controls to controller
        self.ranking_controls.preference_changed.connect(self.on_preference_changed)
        
    def show_initial_schedule(self, schedules: List[Schedule]):
        """Display the first schedule if available"""
        if schedules:
            self.on_schedule_changed(0)
            
        # Force window to be maximized
        self.setWindowState(Qt.WindowMaximized)
        self.show()
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
        """Updates the navigator and table with new schedules - for backward compatibility"""
        self.schedules = schedules
        self.navigator.set_schedules(schedules)
        if schedules:
            self.on_schedule_changed(0)
        else:
            self.schedule_table.clearContents()
            # Update export controls with empty data
            self.header.export_controls.update_data([], 0)
    def on_schedule_changed(self, index: int):
        """Handle schedule change event from navigator and preference controls"""

        if 0 <= index < len(self.schedules):
            try:
                #Get the ranked schedule based on current preference
                schedule = self.controller.get_kth_schedule(index)
                self.schedule_table.display_schedule(schedule)
                # Update export controls with current schedules and index
                current_schedules = self.controller.get_schedules()
                self.header.export_controls.update_data(current_schedules, index)
                self.header.export_controls.export_button.setEnabled(True)
                self.header.back_button.setEnabled(True)
                # Update metrics widget
                self.metrics_widget.setParent(None)
                self.metrics_widget = ScheduleMetrics(schedule)
                 # Find the top bar container and update the metrics widget
                top_bar_widget = self.main_layout.itemAt(1).widget()  # The top bar container
                top_bar_layout = top_bar_widget.layout()
                # Replace the metrics widget (it should be at index 2 between the stretches)
                old_metrics = top_bar_layout.itemAt(2).widget()
                if old_metrics:
                    old_metrics.setParent(None)
                top_bar_layout.insertWidget(2, self.metrics_widget)
            except IndexError:
                self.schedule_table.clearContents()
                self.header.export_controls.update_data([], 0)
                self.header.export_controls.export_button.setEnabled(False)
        
    def on_schedule_generated(self, schedules: List[Schedule]):
        """Handle new schedule generation"""
        self.navigator.set_schedules(schedules)
        if self.schedules != schedules:
            self.schedules = schedules
            if schedules and not self.first_schedule_shown:
                self.navigator.current_index = 0
                self.on_schedule_changed(0)
                self.first_schedule_shown = True
            elif not schedules:
                self.schedule_table.clearContents()
                # Update export controls with empty data
                self.header.export_controls.update_data([], 0)
                
        if not self.controller.generation_active and not schedules:
            self.progress.hide_progress()

    def on_preference_changed(self, metric, ascending):
        """Handle changes in ranking preferences"""
        if metric is None:
            # Clear preference
            self.controller.clear_preference()
        else:
            # Set new preference
            self.controller.set_preference(metric, ascending)
        
        # Refresh the schedules display
        if self.navigator.current_index < len(self.schedules):
            self.on_schedule_changed(self.navigator.current_index)
            
    def navigateToCourseWindow(self):
        """Navigate back to course selection"""
        self.controller.stop_schedules_generation()
        self.progress.hide_progress()
        self.on_back()
        
    def handle_export(self, file_path: str, schedules_to_export: Optional[List[Schedule]]):
        """Handle export request from ExportControls"""
        if schedules_to_export is None:
            # Export all schedules - call with just file path
            self.controller.export_schedules(file_path)
        else:
            # Export specific schedules
            self.controller.export_schedules(file_path, schedules_to_export)
                
    def open_full_size(self):
        """Open current schedule in full-size window"""
        if not self.schedules or self.navigator.current_index >= len(self.schedules):
            QMessageBox.warning(self, "No Schedule", "No schedule is currently selected.")
            return
            
        if self.full_size_window is not None:
            self.full_size_window.close()
            
        self.full_size_window = FullSizeWindow(
            self.schedules[self.navigator.current_index],
            self.navigator.current_index
        )