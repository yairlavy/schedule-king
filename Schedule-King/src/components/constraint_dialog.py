from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from src.components.time_constraint_table import TimeConstraintTable
from src.styles.ui_styles import red_button_style, green_button_style, blue_button_style


class ConstraintDialog(QDialog):
    def __init__(self, parent=None, initial_forbidden=None, initial_preferred=None):
        super().__init__(parent)
        self.setWindowTitle("Select Time Constraints")
        self.setMinimumSize(950, 600)

        layout = QVBoxLayout()
        # === Summary label ===
        self.summary_label = QLabel("")
        self.summary_label.setAlignment(Qt.AlignCenter)
        font = self.summary_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.summary_label.setFont(font)
        layout.addWidget(self.summary_label)

        # === Time slot table ===
        self.table = TimeConstraintTable()
        self.table.cell_toggled.connect(self.update_summary)

        if initial_forbidden:
            for row, col in initial_forbidden:
                self.table.set_forbidden_cell(row, col)

        if initial_preferred:
            for row, col in initial_preferred:
                self.table.set_preferred_cell(row, col)

        layout.addWidget(self.table)

        # === Mode toggle ===
        self.mode_toggle_btn = QPushButton("Mode: ❌ Forbidden")
        self.mode_toggle_btn.setCheckable(True)
        self.mode_toggle_btn.setChecked(False)  # Default mode
        self.mode_toggle_btn.clicked.connect(self.toggle_mode)
        layout.addWidget(self.mode_toggle_btn)

        # === Buttons ===
        btns = QHBoxLayout()

        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.setStyleSheet(blue_button_style())
        self.clear_all_btn.setCursor(Qt.PointingHandCursor)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet(green_button_style())

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(red_button_style())

        btns.addWidget(self.clear_all_btn)
        btns.addWidget(self.ok_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)

        self.setLayout(layout)

        # === Connections ===
        self.clear_all_btn.clicked.connect(self._clear_all_constraints)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        self.update_summary()
        self.toggle_mode()  # apply default style


    def toggle_mode(self):
        """Toggle between forbidden and preferred mode."""
        if self.mode_toggle_btn.isChecked():
            self.table.mark_mode = 'preferred'
            self.mode_toggle_btn.setText("Mode: ✅ Preferred")
            self.mode_toggle_btn.setStyleSheet("background-color: rgb(144, 238, 144); color: white; font-weight: bold;")
        else:
            self.table.mark_mode = 'forbidden'
            self.mode_toggle_btn.setText("Mode: ❌ Forbidden")
            self.mode_toggle_btn.setStyleSheet("background-color: rgb(255, 105, 97); color: white; font-weight: bold;")
    def _clear_all_constraints(self):
        """Clear all cell markings."""
        self.table.clear_constraints()
        self.update_summary()

    def update_summary(self):
        """Update the label showing how many cells are selected per type."""
        forbidden_count = len(self.table.forbidden)
        preferred_count = len(self.table.preferred)
        self.summary_label.setText(f"❌ Forbidden: {forbidden_count}    ✅ Preferred: {preferred_count}")
        self.summary_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")

    def get_forbidden(self):
        return set(self.table.forbidden)

    def get_preferred(self):
        return set(self.table.preferred)
