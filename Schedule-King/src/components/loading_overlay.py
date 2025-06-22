from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog
from PyQt5.QtCore import Qt, QTimer

class LoadingOverlay(QDialog):
    """
    A loading overlay widget that displays a loading animation and message.
    """
    def __init__(self, parent=None, message="Loading..."):
        super().__init__(parent)
        self.message = message
        self.setup_ui()  # Initialize the UI components
        
    def setup_ui(self):
        """Setup the loading overlay UI"""
        # Set dialog properties
        self.setModal(False)  # Non-blocking dialog
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # No window frame, always on top
        
        # Professional dark semi-transparent background
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(0, 0, 0, 0.85);
                border: none;
                border-radius: 15px;
            }
        """)
        
        # Set a fixed size for testing
        self.resize(400, 300)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)  # Center contents
        layout.setSpacing(20)  # Space between widgets
        
        # Create spinner label
        self.spinner_label = QLabel()
        self.spinner_label.setFixedSize(60, 60)  # Spinner size
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #4CAF50;
                font-size: 32px;
                font-weight: bold;
            }
        """)
        
        # Create loading label
        self.loading_label = QLabel(self.message)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 500;
                background: transparent;
                padding: 10px;
            }
        """)
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(self.spinner_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.loading_label, alignment=Qt.AlignCenter)
        
        # Start spinner animation
        self.start_spinner()
        
    def show(self):
        """Override show method to add debug info"""
        super().show()
        
    def start_spinner(self):
        """Start the spinner animation"""
        # Modern spinner characters (braille dots)
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_index = 0  # Current spinner character index
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.update_spinner)  # Update spinner on timeout
        self.spinner_timer.start(80)  # Faster animation (80ms instead of 100ms)
        
    def update_spinner(self):
        """Update the spinner animation"""
        self.spinner_label.setText(self.spinner_chars[self.spinner_index])  # Set next spinner char
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)  # Loop index
        
    def stop_spinner(self):
        """Stop the spinner animation"""
        if hasattr(self, 'spinner_timer'):
            self.spinner_timer.stop()
            
    def set_message(self, message: str):
        """Update the loading message"""
        self.message = message
        self.loading_label.setText(message)  # Update label text