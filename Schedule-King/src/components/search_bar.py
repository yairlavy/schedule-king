from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal

class SearchBar(QWidget):
    # Signal emitted when the search text changes
    searchTextChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create a vertical layout for the widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the search input field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search courses...")  # Set placeholder text
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 12pt;
                border: 2px solid #C5CAE9;
                border-radius: 8px;
            }
        """)  # Apply custom styling to the input
        self.search_input.textChanged.connect(self._handle_text_changed)  # Connect text change signal
        
        layout.addWidget(self.search_input)  # Add input to the layout

    def _handle_text_changed(self, text: str):
        # Emit custom signal when the text changes
        self.searchTextChanged.emit(text)

    def clear(self):
        # Clear the search input field
        self.search_input.clear() 