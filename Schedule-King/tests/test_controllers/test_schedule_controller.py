import pytest
from src.controllers.ScheduleController import ScheduleController
from src.services.schedule_api import ScheduleAPI
from src.models.schedule import Schedule
from src.models.Preference import Preference, Metric

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

def wait_for_generation(controller):
    # Manually poll until generation completes
    while controller.generation_active:
        controller.check_for_schedules()

# ——— Tests ————————————————————————————————————————————
def test_generate_schedules(controller, api, courses_txt):
    # parse courses from file
    courses = api.get_courses(courses_txt)
    assert len(courses) == 2

    # Generate schedules
    controller.generate_schedules(courses)
    wait_for_generation(controller)
    schedules = controller.get_schedules()

    # Assert schedules on controller
    assert isinstance(schedules, list)
    assert all(isinstance(s, Schedule) for s in schedules)
    assert len(schedules) == 2

def test_generate_schedules_empty_data(controller):
    #Passing empty course list should return empty schedules
    schedules = controller.generate_schedules([])
    assert schedules == []
    assert controller.get_schedules() == []

def test_export_schedules_format(controller, api, courses_txt, tmp_path):
    # parse and generate
    courses = api.get_courses(courses_txt)
    assert len(courses) == 2
    controller.generate_schedules(courses)

    # generate schedules
    controller.generate_schedules(courses)
    wait_for_generation(controller)
    schedules = controller.get_schedules()
    assert len(schedules) == 2

    # export the schedules
    export_path = tmp_path / "exported.txt"
    controller.export_schedules(str(export_path), schedules)
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

def test_preference_handling(controller, api, courses_txt):
    # Setup: Generate some schedules
    courses = api.get_courses(courses_txt)
    controller.generate_schedules(courses)
    wait_for_generation(controller)
    
    # Test setting preference
    controller.set_preference(Metric.ACTIVE_DAYS, True)
    assert controller.get_current_preference() is not None
    assert controller.get_current_preference().metric == Metric.ACTIVE_DAYS
    assert controller.get_current_preference().ascending == True
    
    # Test clearing preference
    controller.clear_preference()
    assert controller.get_current_preference() is None

def test_schedule_retrieval(controller, api, courses_txt):
    # Setup: Generate some schedules
    courses = api.get_courses(courses_txt)
    controller.generate_schedules(courses)
    wait_for_generation(controller)
    
    # Test get_kth_schedule
    first_schedule = controller.get_kth_schedule(0)
    assert isinstance(first_schedule, Schedule)
    
    # Test get_ranked_schedules
    ranked_schedules = controller.get_ranked_schedules(2, 0)
    assert len(ranked_schedules) == 2
    assert all(isinstance(s, Schedule) for s in ranked_schedules)
    
    # Test out of bounds
    with pytest.raises(IndexError):
        controller.get_kth_schedule(1000)

def test_export_errors(controller, api, courses_txt):
    # Setup: Generate some schedules
    courses = api.get_courses(courses_txt)
    controller.generate_schedules(courses)
    wait_for_generation(controller)
    schedules = controller.get_schedules()
    
    # Test empty file path
    with pytest.raises(ValueError):
        controller.export_schedules("", schedules)
    
    # Test no schedules provided
    with pytest.raises(ValueError):
        controller.export_schedules("some_path.txt", [])

def test_progress_tracking(controller, api, courses_txt):
    progress_updates = []
    schedule_updates = []
    
    # Setup callbacks
    controller.on_progress_updated = lambda current, total: progress_updates.append((current, total))
    controller.on_schedules_generated = lambda count: schedule_updates.append(count)
    
    # Generate schedules
    courses = api.get_courses(courses_txt)
    controller.generate_schedules(courses)
    wait_for_generation(controller)
    
    # Verify progress updates occurred
    assert len(progress_updates) > 0
    assert len(schedule_updates) > 0
    
    # Verify final progress shows completion
    final_progress = progress_updates[-1]
    assert final_progress[0] == final_progress[1]  # current equals total