from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from src.models.schedule import Schedule
from src.controllers.ScheduleController import ScheduleController
from typing import List, Callable, Optional
import os

class ExportControls(QWidget):
    """
    Export controls component containing:
    - Export button
    - Export visible only checkbox
    - Export functionality
    """
    def __init__(self, controller: ScheduleController, export_handler: Callable[[str, Optional[List[Schedule]]], None]):
        super().__init__()
        self.export_handler = export_handler
        self.controller = controller  # Reference to the controller for handling export logic
        self.current_index = 0  # Store current index
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize and setup the export controls UI"""
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(5)
        self.setLayout(layout)
        
        # Export button
        self.export_button = QPushButton("  Export Schedule")
        self.export_button.setObjectName("top_action_button")
        export_icon = QIcon(os.path.join(os.path.dirname(__file__), "../assets/export.png"))
        if not export_icon.isNull():
            self.export_button.setIcon(export_icon)
        else:
            self.export_button.setText("Export Schedule")
            
        # Export visible only checkbox
        self.export_visible_only = QCheckBox("Export visible schedule only")
        self.export_visible_only.setObjectName("export_checkbox")
        
        # Add components to layout
        layout.addWidget(self.export_button)
        layout.addWidget(self.export_visible_only)
        
        # Connect button click
        self.export_button.clicked.connect(self.export_to_file)
        
    def update_data(self, current_index: int):
        """
        Update the stored schedules and current index.
        
        Args:
            schedules (List[Schedule]): List of all schedules
            current_index (int): Index of currently visible schedule
        """
        self.current_index = current_index
        
    def export_to_file(self):
        """Handle export button click"""
        size = self.controller.ranker.size()
        if self.current_index < 0 or self.current_index >= size :
            QMessageBox.warning(self, "No Schedules", "No schedules available to export.")
            return
            
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
                if self.export_visible_only.isChecked() and 0 <= self.current_index < size:
                    # Export only the visible schedule
                    self.export_handler(file_path,None)
                elif size > 100:
                    # Export to Excel only the last 100 schedules - import is slow
                    QMessageBox.warning(
                        self, "Export Warning",
                        "Exporting only the last 100 schedules for performance reasons."
                    )   
                    self.export_handler(file_path, self.controller.get_ranked_schedules(self.current_index,100))
                else:
                    # Export all schedules - call with just file path to match original behavior
                    self.export_handler(file_path, None)
                    
                QMessageBox.information(
                    self, "Export Successful",
                    f"Schedules were saved successfully to:\n{file_path}"
                )
            except Exception as e:
                error_msg = str(e)
                print(f"Export error: {error_msg}")
                QMessageBox.critical(
                    self, "Export Failed",
                    f"Failed to export schedules:\n{error_msg}"
                ) 