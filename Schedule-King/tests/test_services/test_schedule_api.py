import pytest
from src.services.schedule_api import ScheduleAPI
from src.models.course import Course
from src.models.schedule import Schedule

# ——— RAW DATA ———————————————————————————————————————————
RAW_DATA = """
$$$$
Calculus 1
00001
Prof. O. Some
L S,2,10:00,11:00,1100,22 S,3,11:00,12:00,1100,42
$$$$
Software Project
83533
Dr. Terry Bell
L S,5,12:00,13:00,605,061
""".strip()

# ——— Fixtures ——————————————————————————————————————————

@pytest.fixture
def courses_file(tmp_path):
    f = tmp_path / "courses.txt"
    f.write_text(RAW_DATA, encoding="utf-8")
    return str(f)

@pytest.fixture
def api():
    return ScheduleAPI()

# ——— get_courses tests ——————————————————————————————————————

def test_get_courses_valid_file(api, courses_file):
    # Test get_courses() with a valid file
    courses = api.get_courses(courses_file)
    assert len(courses) == 2

    c1, c2 = courses
    assert isinstance(c1, Course)
    assert c1.course_code == "00001"
    assert c1.name == "Calculus 1"
    assert any(c1.lectures)
    assert c2.course_code == "83533"

def test_get_courses_nonexistent_file(api, tmp_path):
    # Test get_courses() with a nonexistent file raises FileNotFoundError
    missing = str(tmp_path / "does_not_exist.txt")
    with pytest.raises(FileNotFoundError) as exc_info:
        api.get_courses(missing)
    assert str(exc_info.value) == f"The source file '{missing}' does not exist."


def test_get_courses_parse_error_returns_empty(api, tmp_path, capsys):
    # Test get_courses() with a file that not in the the format errors
    
    # Create a file with bad content that FileHandler can't parse
    bad_file = tmp_path / "bad_courses.txt"
    bad_file.write_text("bad", encoding="utf-8")

    # Call the real method — FileHandler should raise ValueError internally
    result = api.get_courses(str(bad_file))

    # The api should catch the error and return an empty list
    assert result == []

    # Check if it printed error message in the console
    captured = capsys.readouterr()
    assert "Error parsing courses:" in captured.out
    assert "Please check the input format." in captured.out

# ——— process tests ——————————————————————————————————————————

def test_process_with_courses(api, courses_file):
    # Test process() with a valid list of courses
    courses = api.get_courses(courses_file)
    schedules = api.process(courses)
    assert schedules, "Expected at least one generated schedule"
    assert all(isinstance(s, Schedule) for s in schedules)

def test_process_empty_list(api):
    # Test process() with an empty list of courses
    schedules = api.process([])
    assert schedules == [], "No selected courses should yield no schedules"

# ——— export tests ——————————————————————————————————————————

@pytest.fixture
def courses(api, courses_file):
    courses = api.get_courses(courses_file)
    return api.process(courses)

def test_export_success(tmp_path, api, courses, capsys):
    # Test export() with a valid list of courses
    dest = tmp_path / "out" / "test.txt"
    api.export(courses, str(dest))

    # Check if the file was created
    assert dest.exists()
    txt = dest.read_text(encoding="utf-8")
    
    # Check if the file contains the expected content
    assert "Schedule 1" in txt
    assert any(code in txt for code in ("00001", "83533"))

    # Confirm printed message
    captured = capsys.readouterr()
    assert f"Schedules successfully exported to {dest}." in captured.out

def test_export_empty_schedules_does_not_throw(tmp_path, api, capsys):
    # Test export() with an empty list of courses
    dest = tmp_path / "nothing" / "empty.txt"
    api.export([], str(dest))

    # No file created
    assert not dest.exists()

    # It should have printed an error message
    captured = capsys.readouterr()
    assert "Error exporting schedules:" in captured.out
