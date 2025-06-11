import os
import pytest
from unittest.mock import patch
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QMessageBox
from src.views.course_window import CourseWindow
from src.models.course import Course
import src.components.course_selector as course_selector

# ——— RAW_DATA ———————————————————————————————————————————
RAW_DATA = """
$$$$
Calculus 1
00001
Prof. O. Some
L S,2,16:00,17:00,1100,22 S,3,17:00,18:00,1100,42
T S,2,18:00,19:00,1100,22
T S,3,19:00,20:00,1100,42
$$$$
Software Project
83533
Dr. Terry Bell
L S,5,10:00,16:00,605,061
T S,5,16:00,17:00,605,061
$$$$
Calculus 1 (eng)
83112
Dr. Erez Scheiner
L S,1,14:00,16:00,1401,4 S,2,14:00,16:00,1401,4
T S,1,16:00,18:00,1104,42
""".strip()

# ——— Fixtures ——————————————————————————————————————————
@pytest.fixture
def courses_txt(tmp_path):
    f = tmp_path / "courses.txt"
    f.write_text(RAW_DATA, encoding="utf-8")
    return str(f)

@pytest.fixture
def courses():
    return [
        Course("Calculus 1", "00001", "Prof. O. Some"),
        Course("Software Project", "83533", "Dr. Terry Bell"),
        Course("Calculus 1 (eng)", "83112", "Dr. Erez Scheiner")
    ]

@pytest.fixture
def loaded_window(qtbot, courses_txt, courses):
    """
    Fixture for creating a CourseWindow safely, ensuring:
    - QFileDialog is patched BEFORE CourseWindow is instantiated.
    - Course loading callback is patched BEFORE any interaction.
    - Avoids race conditions, crashes and Windows access violations.
    """
    with patch.object(QFileDialog, "getOpenFileName", return_value=(courses_txt, "")):
        window = CourseWindow(maximize_on_start=False)  # Disable maximize to avoid access violation during tests
        qtbot.addWidget(window)

        # Ensure courses are loaded safely
        window.on_courses_loaded = lambda path: window.displayCourses(courses)

        # Trigger load button AFTER patch and handler are safely set
        qtbot.mouseClick(window.courseSelector.load_button, Qt.LeftButton)

        return window

def get_wait_time():
    return int(os.environ.get("WAIT_TIME", 0))

# ——— Tests ————————————————————————————————————————————

def test_load_courses(loaded_window, courses):
    list_widget = loaded_window.courseSelector.findChild(QListWidget)
    assert list_widget.count() == len(courses)
    assert list_widget.item(0).text() == "00001 - Calculus 1"
    assert list_widget.item(1).text() == "83533 - Software Project"
    assert list_widget.item(2).text() == "83112 - Calculus 1 (eng)"
    assert loaded_window.courseSelector.title_label.text() == "Available Courses (3 total)"

def test_select_and_clear_courses(loaded_window, qtbot):
    list_widget = loaded_window.courseSelector.findChild(QListWidget)
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        list_widget.scrollToItem(item)
        qtbot.mouseClick(list_widget.viewport(), Qt.LeftButton, pos=list_widget.visualItemRect(item).center())
        qtbot.wait(get_wait_time())

    assert loaded_window.courseSelector.title_label.text() == "Available Courses (3 selected)"

    qtbot.mouseClick(loaded_window.courseSelector.clear_button, Qt.LeftButton)
    assert not list_widget.selectedItems()
    assert loaded_window.courseSelector.title_label.text() == "Available Courses (3 total)"

def test_submit_selection(loaded_window, qtbot):
    list_widget = loaded_window.courseSelector.findChild(QListWidget)
    captured_selections = []

    def capture_selections(selected):
        captured_selections.extend(selected)

    loaded_window.on_continue = capture_selections

    # Patch the progress bar to prevent GUI issues during test
    import src.components.course_selector as course_selector_module
    with patch.object(course_selector_module.CourseSelector, "show_progress_bar", return_value=None):
        list_widget.item(0).setSelected(True)
        qtbot.mouseClick(loaded_window.courseSelector.submit_button, Qt.LeftButton)

    assert len(captured_selections) == 1
    assert captured_selections[0].course_code == "00001"

    captured_selections.clear()
    list_widget.clearSelection()

    with patch.object(QMessageBox, "critical") as mock_critical:
        qtbot.mouseClick(loaded_window.courseSelector.submit_button, Qt.LeftButton)
        mock_critical.assert_called_once()
        assert captured_selections == []
