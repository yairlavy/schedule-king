from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt

class ScheduleProgress(QWidget):
    """
    Progress component for the schedule window containing:
    - Progress label
    - Progress bar
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize and setup the progress UI components"""
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(2)
        self.setLayout(layout)
        
        # Progress label
        self.progress_label = QLabel("Generating schedules...")
        self.progress_label.setObjectName("progress_label")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setVisible(False)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("schedule_progress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m schedules")
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setVisible(False)
        
        # Add components to layout
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        
    def update_progress(self, current: int, estimated: int):
        """
        Updates the progress bar with the current and estimated schedule counts.
        Shows a determinate or indeterminate progress bar based on estimate availability.
        """
        # Make sure progress controls are visible when active generation is happening
        self.progress_label.setVisible(True)
        self.progress_bar.setVisible(True)
        
        try:
            if estimated > 0:
                # We have an estimated total - show determinate progress
                self.progress_bar.setMaximum(estimated)
                self.progress_bar.setValue(current)
    
                self.progress_label.setText(f"Generating schedules... {estimated} total estimated")
                # If we're done (current >= estimated), update text accordingly
                if current >= estimated:
                    self.progress_label.setText(f"Completed! Generated {current} schedules")
            else:
                # No estimate available - show indeterminate progress for ongoing generation
                # or determinate if we're at the end (setting both current and max to the same value)
                self.progress_bar.setMaximum(0)  # Indeterminate mode
                self.progress_label.setText(f"Generating schedules... ({current} generated)")
                
            # Force update the UI
            self.progress_bar.repaint()
            self.progress_label.repaint()
        except Exception as e:
            print(f"Estimate error: {estimated}")  # Log the error
            print(f"Current error: {current}")  # Log the error
            print(f"Error updating progress: {str(e)}")
            
    def hide_progress(self):
        """Hide the progress indicators"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False) 