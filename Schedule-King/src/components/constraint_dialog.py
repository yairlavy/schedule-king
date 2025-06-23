from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QToolButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.components.time_constraint_table import TimeConstraintTable
from src.styles.ui_styles import red_button_style, green_button_style, blue_button_style


class ConstraintDialog(QDialog):
    def __init__(self, parent=None, initial_forbidden=None, initial_preferred=None):
        super().__init__(parent)
        self.setWindowTitle("Select Time Constraints")
        self.setMinimumSize(950, 600)

        layout = QVBoxLayout()
        
        # === Header with summary and help icon ===
        header_layout = QHBoxLayout()
        
        # Summary label
        self.summary_label = QLabel("")
        self.summary_label.setAlignment(Qt.AlignCenter)
        font = self.summary_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.summary_label.setFont(font)
        
        # Help button (info icon)
        self.help_btn = QToolButton()
        self.help_btn.setText("ℹ️")
        self.help_btn.setFixedSize(30, 30)
        self.help_btn.setStyleSheet("""
            QToolButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #1976D2;
            }
            QToolButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.help_btn.setToolTip("Click for scoring explanation")
        self.help_btn.clicked.connect(self.show_scoring_help)
        
        # Add to header layout
        header_layout.addStretch(1)
        header_layout.addWidget(self.summary_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.help_btn)
        
        layout.addLayout(header_layout)

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

    def show_scoring_help(self):
        """Show help dialog explaining the preference scoring system"""
        help_dialog = QMessageBox(self)
        help_dialog.setWindowTitle("Preference Scoring Explanation")
        help_dialog.setIcon(QMessageBox.Information)
        
        help_text = """
<h3>📊 How Preference Scoring Works</h3>

<p><b>🎯 Simple Formula:</b><br>
Score = (Preferred slots used ÷ Total preferred slots) × 100</p>

<p><b>📋 What this means:</b><br>
• <span style="color: #4CAF50;"><b>100%</b></span> = All your preferred time slots have classes<br>
• <span style="color: #FF9800;"><b>50%</b></span> = Half of your preferred time slots have classes<br>
• <span style="color: #F44336;"><b>1%</b></span> = None of your preferred time slots have classes</p>

<p><b>🔴 Forbidden slots:</b> Prevent classes from being scheduled (no scoring impact)</p>

<p><b>🟢 Preferred slots:</b> Count towards your preference score when filled</p>

<p><b>⚪ Neutral slots:</b> Ignored in scoring (neither help nor hurt your score)</p>

<p><b>📈 Example:</b><br>
You mark 10 preferred slots → System schedules 7 classes in preferred slots → Score = 70%</p>
        """
        
        help_dialog.setText(help_text)
        help_dialog.setTextFormat(Qt.RichText)
        
        # Make dialog wider to accommodate the text
        help_dialog.setStyleSheet("QMessageBox { min-width: 500px; }")
        
        help_dialog.exec_()

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