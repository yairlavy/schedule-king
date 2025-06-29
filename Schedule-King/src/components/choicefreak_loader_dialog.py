from PyQt5.QtWidgets import QDialog, QFormLayout, QComboBox, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal

class ChoiceFreakLoaderDialog(QDialog):
    selectionMade = pyqtSignal(str, str)  # university, period

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChoiceFreakLoaderDialog")
        self.setWindowTitle("Load Courses from ChoiceFreak")
        layout = QFormLayout(self)
        self.university_combo = QComboBox()
        self.university_combo.setObjectName("university_combo")
        self.university_combo.addItems(["biu", "tau", "bgu", "tech", "ariel", "huji", "hit"])
        layout.addRow("University:", self.university_combo)
        self.period_combo = QComboBox()
        self.period_combo.setObjectName("period_combo")
        self.period_combo.addItems(["2025-2", "2025-1", "2024-2", "2024-1"])
        layout.addRow("Period:", self.period_combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setObjectName("choicefreak_button_box")
        layout.addRow(buttons)
        buttons.accepted.connect(self._emit_selection)
        buttons.rejected.connect(self.reject)

    def _emit_selection(self):
        self.selectionMade.emit(self.university_combo.currentText(), self.period_combo.currentText())
        self.accept() 