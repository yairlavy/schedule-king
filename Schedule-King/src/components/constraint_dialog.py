from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from src.components.time_constraint_table import TimeConstraintTable
from src.styles.ui_styles import red_button_style, green_button_style

class ConstraintDialog(QDialog):
    def __init__(self, parent=None, initial_forbidden=None):
        super().__init__(parent)
        self.setWindowTitle("Select Forbidden Time Slots")
        self.setMinimumSize(950, 600)

        self.table = TimeConstraintTable()
        if initial_forbidden:
            # Set the forbidden slots directly and display them
            for row, col in initial_forbidden:
                self.table.set_forbidden_cell(row, col)

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        btns = QHBoxLayout()
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.setStyleSheet(red_button_style())
        self.clear_all_btn.setCursor(Qt.PointingHandCursor)
        
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        btns.addWidget(self.clear_all_btn)
        btns.addWidget(self.ok_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)
        self.ok_btn.setStyleSheet(green_button_style())
        self.cancel_btn.setStyleSheet(green_button_style())

        self.setLayout(layout)
        self.clear_all_btn.clicked.connect(self._clear_all_constraints)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _clear_all_constraints(self):
        """Clear all time constraints from the table"""
        self.table.clear_constraints()

    def get_constraints(self):
        return set(self.table.forbidden) 