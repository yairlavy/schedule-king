import os
import time
import random
import pytest
from PyQt5.QtWidgets import QMessageBox, QListWidget
from src.services.schedule_api import ScheduleAPI
from src.controllers.MainConroller import MainController
from PyQt5.QtCore import Qt

# ——— Helper func ———————————————————————————————————————————————
# This function generates a course file with random data for testing.
# It creates a file with a specified number of courses, lectures, tirguls, and maabadas.
# The file is saved to the given path and returns the path.
# The courses are generated with random days and times for lectures, tirguls, and maabadas.
def write_course_file(path: str,
                      num_courses: int = 1,
                      lectures_per_course: int = 1,
                      tirguls_per_course: int = 0,
                      maabadas_per_course: int = 0):
    
    days = list(range(1, 7))
    lines = []

    # Header between every course
    for i in range(num_courses):
        course_code = f"C{i:03d}"
        lines += ["$$$$", f"Course {i}", course_code, f"Prof {i}"]

        # Lectures
        lec = []
        for _ in range(lectures_per_course):
            d = random.choice(days)
            s = random.randint(8, 18)
            e = s + random.choice([1, 2])
            lec.append(f"S,{d},{s:02d}:00,{e:02d}:00,100,10{i}")
        lines.append("L " + " ".join(lec))

        # Tirguls
        trg = []
        for _ in range(tirguls_per_course):
            d = random.choice(days)
            s = random.randint(8, 18)
            e = s + random.choice([1, 2]) # Random end time 1-2 hours later from start
            trg.append(f"S,{d},{s:02d}:00,{e:02d}:00,200,20{i}")
        lines.append("T " + " ".join(trg))

        # Maabadas
        mab = []
        for _ in range(maabadas_per_course):
            d = random.choice(days)
            s = random.randint(8, 18)
            e = s + random.choice([1, 2])
            mab.append(f"S,{d},{s:02d}:00,{e:02d}:00,300,30{i}")
        lines.append("M " + " ".join(mab))

    # Write to file and return path
    content = "\n".join(lines)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

# ——— Fixtures ——————————————————————————————————————————————

@pytest.fixture
def api():
    return ScheduleAPI()

@pytest.fixture
def controller(api, qtbot):
    controller = MainController(api)
    controller.course_window.show = lambda: None
    controller.course_window.hide = lambda: None
    return controller

# ——— Tests ——————————————————————————————————————————————
def test_the_program_flow(controller, tmp_path):
    # write & load
    f = write_course_file(str(tmp_path/"courses.txt"), num_courses=2, lectures_per_course=1, tirguls_per_course=0, maabadas_per_course=0)
    controller.on_file_selected(f)
    loaded = controller.course_controller.courses
    assert len(loaded)==2

    # continue → schedule window
    controller.on_courses_selected(loaded)
    assert controller.schedule_window is not None

    # back
    controller.on_navigate_back_to_courses()
    assert controller.schedule_window is None

def test_no_courses_selected_shows_warning(controller, monkeypatch):
    # mock QMessageBox.warning to avoid showing the the popup
    # and to capture the arguments passed to it
    warn = {}
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: warn.setdefault("last", (args[1], args[2])) or QMessageBox.Ok)

    # Simulate no courses selected that would trigger the warning
    controller.on_courses_selected([])
    assert controller.schedule_window is None

    # Assert that the warning was shown with correct title and text
    title, text = warn["last"]
    assert title == "No Courses Selected"
    assert "select at least one course" in text.lower()

def test_export_file(controller, tmp_path):
    #This test checks if the export file is created correctly
    f = write_course_file(str(tmp_path/"courses.txt"), num_courses=2, lectures_per_course=1, tirguls_per_course=0, maabadas_per_course=0)
    controller.on_file_selected(f)
    loaded = controller.course_controller.courses
    controller.on_courses_selected(loaded)
    out = tmp_path/"output"/"courses.txt"
    controller.schedule_controller.export_schedules(str(out))
    assert out.exists()
    txt = out.read_text()
    assert "Schedule 1" in txt
    assert any(c.course_code in txt for c in loaded)

# ——— Performance Test ——————————————————————————————————————————————

# Parmetrize is used to run the test with different parameters
# This test checks the performance of the program by measuring the time it takes to generate schedules
@pytest.mark.parametrize("num,lec,trg,mab", [
    (3, 3, 3, 3),   # small fast
    (5, 4, 3, 2),   # heavy
])
def test_performance(controller, tmp_path, qtbot, api, num, lec, trg, mab):
    # Write heavy file
    heavy = write_course_file(str(tmp_path/"heavy.txt"), num, lec, trg, mab)
    assert os.path.exists(heavy)

    controller.course_window.show()
    qtbot.addWidget(controller.course_window)

    # Load the file
    controller.on_file_selected(heavy)
    
    # Select all by clicking on them
    course_list_widget = controller.course_window.findChild(QListWidget)
    for i in range(num):
        item=course_list_widget.item(i)
        qtbot.mouseClick(course_list_widget.viewport(), Qt.LeftButton, pos=course_list_widget.visualItemRect(item).center())    
    assert len(course_list_widget.selectedItems())==num

    qtbot.wait(1000)
    
    # Continue + measure time
    start=time.perf_counter()
    controller.course_window.navigateToSchedulesWindow()
    qtbot.waitUntil(lambda: controller.schedule_window is not None, timeout=10000)
    dur=time.perf_counter()-start

        # Access and print how many schedules were created
    print(f"\nGenerated {len(controller.schedule_window.schedules)} schedules.")
    print(f"performance: {dur:.2f}s")

    qtbot.wait(2000)    
    
    # close the schedule window so the next param run starts fresh
    controller.schedule_window.close()
    controller.schedule_window = None