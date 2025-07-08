from PyQt5.QtWidgets import QDialog, QFormLayout, QComboBox, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal

class ChoiceFreakLoaderDialog(QDialog):
    selectionMade = pyqtSignal(str, str)  # university, period

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChoiceFreakLoaderDialog")
        self.setWindowTitle("Load Courses from ChoiceFreak")
        layout = QFormLayout(self)

        # Mapping of university IDs to Hebrew names
        self.university_map = {
            "biu": "אוניברסיטת בר-אילן",
            "tau": "אוניברסיטת תל-אביב",
            "bgu": "אוניברסיטת בן-גוריון",
            "tech": "הטכניון",
            "ariel": "אוניברסיטת אריאל",
            "huji": "האוניברסיטה העברית",
            "hit": "המכון הטכנולוגי חולון",
            "haifa": "אוניברסיטת חיפה"
        }

        # Reverse mapping for translation back to IDs
        self.university_reverse_map = {v: k for k, v in self.university_map.items()}

        self.university_combo = QComboBox()
        self.university_combo.setObjectName("university_combo")
        self.university_combo.addItems(self.university_map.values())
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
        # Translate Hebrew name back to ID before emitting
        university_id = self.university_reverse_map[self.university_combo.currentText()]
        self.selectionMade.emit(university_id, self.period_combo.currentText())
        self.accept()