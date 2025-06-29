from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QWidget, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap

class UserGuideDialog(QDialog):
    """
    User guide dialog with language toggle functionality.
    Shows step-by-step instructions for using the Schedule King application.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_language = "EN"  # Default to English
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Schedule King - User Guide")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumSize(700, 600)
        self.setMaximumSize(800, 700)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with title and language toggle
        header_layout = QHBoxLayout()
        
        # Title
        self.title_label = QLabel()
        title_font = QFont("Arial", 18, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #1A237E; margin-bottom: 10px;")
        
        # Language toggle button
        self.lang_toggle_btn = QPushButton()
        self.lang_toggle_btn.setFixedSize(50, 50)
        self.lang_toggle_btn.setCheckable(True)
        self.lang_toggle_btn.setChecked(False)  # Default to English
        self.lang_toggle_btn.clicked.connect(self.toggle_language)
        self.update_language_button()
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.lang_toggle_btn)
        layout.addLayout(header_layout)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(15)
        
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
        
        # Initialize with English content
        self.update_content()
        
    def toggle_language(self):
        """Toggle between Hebrew and English"""
        self.current_language = "HE" if self.current_language == "EN" else "EN"
        self.update_language_button()
        self.update_content()
        
    def update_language_button(self):
        """Update the language toggle button appearance"""
        if self.current_language == "EN":
            self.lang_toggle_btn.setText("EN")
            self.lang_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
            """)
        else:
            self.lang_toggle_btn.setText("עב")
            self.lang_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            
    def create_step_widget(self, step_num, title, description, icon_emoji="📋"):
        """Create a styled step widget"""
        step_frame = QFrame()
        step_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 2px solid #E3F2FD;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        step_layout = QVBoxLayout(step_frame)
        step_layout.setContentsMargins(15, 15, 15, 15)
        step_layout.setSpacing(8)
        
        # Step header
        header_layout = QHBoxLayout()
        
        # Step number and icon
        step_header = QLabel(f"{icon_emoji} {step_num}. {title}")
        step_header.setFont(QFont("Arial", 14, QFont.Bold))
        step_header.setStyleSheet("color: #1976D2; margin-bottom: 5px;")
        
        header_layout.addWidget(step_header)
        header_layout.addStretch()
        step_layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Arial", 11))
        desc_label.setStyleSheet("color: #424242; line-height: 1.4;")
        step_layout.addWidget(desc_label)
        
        return step_frame
        
    def update_content(self):
        """Update the content based on current language"""
        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
            
        if self.current_language == "EN":
            self.show_english_content()
        else:
            self.show_hebrew_content()
            
    def show_english_content(self):
        """Show English content"""
        self.title_label.setText("How to Use Schedule King")
        
        steps = [
            {
                "num": 1,
                "title": "Load Course Data",
                "desc": "Click 'Load Data' button. Choose:\n• Local File: Load from your computer (Excel/Text file)\n• Global Database: Load from ChoiceFreak online database",
                "icon": "📂"
            },
            {
                "num": 2,
                "title": "Select Your Courses",
                "desc": "Browse the course list and click on courses you want to take. You can select up to 7 courses. Use the search bar to find specific courses quickly.",
                "icon": "📚"
            },
            {
                "num": 3,
                "title": "Set Time Constraints (Optional)",
                "desc": "Click 'Set Time Constraints' to mark:\n• Red slots: Times when you're NOT available\n• Green slots: Times you PREFER to have classes\nThis helps create schedules that fit your needs.",
                "icon": "⏰"
            },
            {
                "num": 4,
                "title": "Generate Schedules",
                "desc": "Click 'Generate Schedules' to create all possible timetables. The system will find combinations that don't have conflicts and rank them by your preferences.",
                "icon": "🔄"
            },
            {
                "num": 5,
                "title": "Browse & Export Results",
                "desc": "Use navigation arrows to browse through generated schedules. Sort by different criteria (gaps, start time, etc.). Export your favorite schedule to Excel or text file.",
                "icon": "📊"
            }
        ]
        
        for step in steps:
            step_widget = self.create_step_widget(
                step["num"], step["title"], step["desc"], step["icon"]
            )
            self.content_layout.addWidget(step_widget)
            
        # Add tips section
        tips_frame = QFrame()
        tips_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F5E8;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        tips_layout = QVBoxLayout(tips_frame)
        tips_layout.setContentsMargins(15, 15, 15, 15)
        
        tips_title = QLabel("💡King/Queen Tips")
        tips_title.setFont(QFont("Arial", 14, QFont.Bold))
        tips_title.setStyleSheet("color: #2E7D32;")
        tips_layout.addWidget(tips_title)
        
        tips_text = QLabel(
            "• Start with fewer courses (3-4) to get more schedule options\n"
            "• Use time constraints to avoid early morning or late evening classes\n"
            "• Check course details carefully - some courses have multiple components\n"
            "• Export multiple schedule options to compare them later"
        )
        tips_text.setWordWrap(True)
        tips_text.setFont(QFont("Arial", 11))
        tips_text.setStyleSheet("color: #424242;")
        tips_layout.addWidget(tips_text)
        
        self.content_layout.addWidget(tips_frame)
        
    def show_hebrew_content(self):
        """Show Hebrew content"""
        self.title_label.setText("איך להשתמש ב-Schedule King")
        
        steps = [
            {
                "num": 1,
                "title": "טעינת מידע על קורסים",
                "desc": "לחץ על 'Load Data'. בחר:\n• קובץ מקומי: טען מהמחשב שלך (Excel/Text)\n• מסד נתונים גלובלי: טען מבסיס הנתונים המקוון ChoiceFreak",
                "icon": "📂"
            },
            {
                "num": 2,
                "title": "בחירת קורסים",
                "desc": "עיין ברשימת הקורסים ולחץ על הקורסים שאתה רוצה לקחת. ניתן לבחור עד 7 קורסים. השתמש בחיפוש כדי למצוא קורסים ספציפיים במהירות.",
                "icon": "📚"
            },
            {
                "num": 3,
                "title": "הגדרת אילוצי זמן (אופציונלי)",
                "desc": "לחץ 'Set Time Constraints' כדי לסמן:\n• משבצות אדומות: זמנים שבהם אתה לא זמין\n• משבצות ירוקות: זמנים שאתה מעדיף לקיים שיעורים\nזה עוזר ליצור מערכות שמתאימות לצרכים שלך.",
                "icon": "⏰"
            },
            {
                "num": 4,
                "title": "יצירת מערכות שעות",
                "desc": "לחץ 'Generate Schedules' כדי ליצור את כל מערכות השעות האפשריות. המערכת תמצא צירופים ללא התנגשויות ותדרג אותם לפי ההעדפות שלך.",
                "icon": "🔄"
            },
            {
                "num": 5,
                "title": "עיון וייצוא תוצאות",
                "desc": "השתמש בחצי הניווט כדי לעיין במערכות השעות שנוצרו. מיין לפי קריטריונים שונים (פערים, שעת התחלה וכו'). יצא את מערכת השעות המועדפת עליך ל-Excel או קובץ טקסט.",
                "icon": "📊"
            }
        ]
        
        for step in steps:
            step_widget = self.create_step_widget(
                step["num"], step["title"], step["desc"], step["icon"]
            )
            self.content_layout.addWidget(step_widget)
            
        # Add tips section in Hebrew
        tips_frame = QFrame()
        tips_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F5E8;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        tips_layout = QVBoxLayout(tips_frame)
        tips_layout.setContentsMargins(15, 15, 15, 15)
        
        tips_title = QLabel("💡טיפים לנסיך/נסיכת הלוזים")
        tips_title.setFont(QFont("Arial", 14, QFont.Bold))
        tips_title.setStyleSheet("color: #2E7D32;")
        tips_layout.addWidget(tips_title)
        
        tips_text = QLabel(
            "• התחל עם פחות קורסים (3-4) כדי לקבל יותר אפשרויות מערכת\n"
            "• השתמש באילוצי זמן כדי להימנע משיעורים מוקדם בבוקר או מאוחר בערב\n"
            "• בדוק בקפידה פרטי קורסים - לחלק מהקורסים יש מספר רכיבים\n"
            "• יצא מספר אפשרויות מערכת כדי להשוות ביניהן מאוחר יותר"
        )
        tips_text.setWordWrap(True)
        tips_text.setFont(QFont("Arial", 11))
        tips_text.setStyleSheet("color: #424242;")
        tips_layout.addWidget(tips_text)
        
        self.content_layout.addWidget(tips_frame)