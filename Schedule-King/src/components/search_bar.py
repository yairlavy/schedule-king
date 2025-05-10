from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal

class SearchBar(QWidget):
    searchTextChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search courses...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 12pt;
                border: 2px solid #C5CAE9;
                border-radius: 8px;
            }
        """)
        self.search_input.textChanged.connect(self._handle_text_changed)
        
        layout.addWidget(self.search_input)

    def _handle_text_changed(self, text: str):
        self.searchTextChanged.emit(text)

    def clear(self):
        self.search_input.clear() 