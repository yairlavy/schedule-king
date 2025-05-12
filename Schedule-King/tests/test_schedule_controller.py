import pytest
from src.controllers.ScheduleController import ScheduleController
from src.services.schedule_api import ScheduleAPI
from src.models.course import Course
from src.models.schedule import Schedule

# ——— RAW_DATA ————————————————————————————————
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
""".strip()

# ——— Fixtures ——————————————————————————————————————————

@pytest.fixture
def courses_txt(tmp_path):
    f = tmp_path / "courses.txt"
    f.write_text(RAW_DATA, encoding="utf-8")
    return str(f)

@pytest.fixture
def api():
    return ScheduleAPI()

@pytest.fixture
def controller(api):
    return ScheduleController(api)

# ——— Tests ————————————————————————————————————————————

def test_generate_schedules(controller, api, courses_txt):
    # parse courses from file
    courses = api.get_courses(courses_txt)

    # should be 2 courses from RAW_DATA
    assert len(courses) == 2

    schedules = controller.generate_schedules(courses)

    # check that the schedules are generated
    assert isinstance(schedules, list)
    assert all(isinstance(s, Schedule) for s in schedules)
    assert len(schedules) == 4

    # check that the schedules are stored in the controller
    assert controller.get_schedules() == schedules

def test_generate_schedules_empty_data(controller):
    #Passing empty course list should return empty schedule
    schedules = controller.generate_schedules([])
    assert schedules == []
    assert controller.get_schedules() == []

def test_export_schedules_format(controller, api, courses_txt, tmp_path):
    #Parse the course
    courses = api.get_courses(courses_txt)
    assert len(courses) == 2

    #Generate schedules
    schedules = controller.generate_schedules(courses)
    assert len(schedules) == 4

    #Export the schedules to a file
    export_path = tmp_path / "exported.txt"
    controller.export_schedules(str(export_path))
    assert export_path.exists()

    #Read and exported file
    content = export_path.read_text(encoding="utf-8")
    lines = content.strip().splitlines()

    # Check that the file has the correct format
    assert lines[0].startswith("------------------------------------------------------")
    assert "Schedule 1:" in lines[1]
    assert any("Monday:" in line for line in lines)
    assert any("[Lecture]" in line or "[Tirgul]" in line for line in lines)
    assert any("Room" in line and "Building" in line for line in lines)

    # Check that all schedules are printed
    schedule_count = content.count("Schedule ")
    assert schedule_count == len(schedules)