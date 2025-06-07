import pytest
from src.controllers.CourseController import CourseController
from src.services.schedule_api import ScheduleAPI
from src.models.course import Course
from src.models.time_slot import TimeSlot

# ——— RAW_DATA———
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
def controller():
    return CourseController(api=ScheduleAPI())

@pytest.fixture
def courses():
    return [
        Course("Calculus 1", "00001", "Prof. O. Some"),
        Course("Software Project", "83533", "Dr. Terry Bell"),
        Course("Calculus 1 (eng)", "83112", "Dr. Erez Scheiner")
    ]

# ——— Tests ——————————————————————————

def test_get_courses_names(controller, courses_txt):
    courses = controller.get_courses_names(courses_txt)

    # two courses parsed
    assert len(courses) == 2

    c1, c2 = courses
    # first course checks
    assert c1.name == "Calculus 1"
    assert c1.course_code == "00001"
    assert c1.instructor == "Prof. O. Some"
    
    # Flatten the lectures and tirguls lists
    lectures = [ts for group in c1.lectures for ts in group]
    tirguls = [ts for group in c1.tirguls for ts in group]
    
    # lectures and tirguls counts from RAW_DATA
    assert len(lectures) == 2
    assert len(tirguls) == 2
    assert all(isinstance(ts, TimeSlot) for ts in lectures + tirguls)

    # second course checks
    assert c2.name == "Software Project"
    assert c2.course_code == "83533"
    assert c2.instructor == "Dr. Terry Bell"
    
    lectures2 = [ts for group in c2.lectures for ts in group]
    tirguls2 = [ts for group in c2.tirguls for ts in group]

    assert len(lectures2) == 1
    assert len(tirguls2) == 1

def test_get_courses_names_invalid_file(controller, tmp_path):
    missing = tmp_path / "nope.txt"
    with pytest.raises(FileNotFoundError):
        controller.get_courses_names(str(missing))

def test_set_selected_courses(controller, courses):
    controller.set_selected_courses([courses[0], courses[2]])
    # test if selected_courses updated correctly
    assert len(controller.selected_courses) == 2
    assert controller.selected_courses[0].course_code == "00001"
    assert controller.selected_courses[1].course_code == "83112"

def test_set_selected_courses_empty_list(controller):
    controller.set_selected_courses([])
    assert controller.selected_courses == []
    assert controller.get_selected_courses() == []

def test_get_selected_courses(controller, courses):
    controller.set_selected_courses([courses[1]])
    result = controller.get_selected_courses()
    assert result == [courses[1]]
    assert result[0].name == "Software Project"