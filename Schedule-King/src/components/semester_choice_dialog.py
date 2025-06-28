from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt

class SemesterChoiceDialog(QDialog):
    def __init__(self, parent=None, semesters=None, title="בחר סמסטר", subtitle="לאיזה סמסטר לייצא את לוח השנה?"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.selected_semester = None
        if semesters is None:
            semesters = ["סמסטר א'", "סמסטר ב'","סמסטר קיץ"]
        self.semesters = semesters
        self.setup_ui(subtitle)

    def setup_ui(self, subtitle):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Title label
        title_label = QLabel(self.windowTitle())
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #1976D2;")
        layout.addWidget(title_label)

        # Subtitle label
        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 16px; color: #333; margin-bottom: 10px;")
        layout.addWidget(subtitle_label)

        # Semester buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.setAlignment(Qt.AlignCenter)

        for sem in self.semesters:
            btn = QPushButton(sem)
            btn.setFixedSize(160, 60)
            btn.setStyleSheet('''
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 18px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
            ''')
            btn.clicked.connect(lambda checked, s=sem: self.choose_semester(s))
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # Cancel button
        cancel_btn = QPushButton("ביטול")
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.setStyleSheet('''
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        ''')
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn, alignment=Qt.AlignCenter)

    def choose_semester(self, semester):
        self.selected_semester = semester
        self.accept()

    @staticmethod
    def get_semester(parent=None, semesters=None):
        dialog = SemesterChoiceDialog(parent, semesters)
        result = dialog.exec_()
        return dialog.selected_semester, bool(result) 