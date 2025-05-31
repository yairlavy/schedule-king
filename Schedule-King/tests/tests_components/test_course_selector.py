import pytest
from src.components.course_selector import CourseSelector  
from src.models.course import Course
from unittest.mock import patch


@pytest.fixture
def sample_courses():
    # Fixture to provide a sample list of courses for testing
    return [
        Course("Intro to CS", "CS101", "Dr. Smith", lectures=[], tirguls=[], maabadas=[]),
        Course("Calculus", "MATH201", "Dr. Jones", lectures=[], tirguls=[], maabadas=[]),
        Course("Physics", "PHYS101", "Dr. Brown", lectures=[], tirguls=[], maabadas=[])
    ]


@pytest.fixture
def selector(qtbot, sample_courses):
    # Fixture to create and initialize the CourseSelector widget
    widget = CourseSelector()
    widget.populate_courses(sample_courses)
    qtbot.addWidget(widget)
    return widget


def test_initial_population(selector, sample_courses):
    # Test that the CourseSelector is populated with the correct number of courses
    assert selector.course_list.list_widget.count() == len(sample_courses)
    # Verify that the title label starts with "Available Courses"
    assert selector.title_label.text().startswith("Available Courses")


def test_selection_emits_signal(qtbot, selector, sample_courses):
    # Test that selecting a course emits the `coursesSelected` signal
    with qtbot.waitSignal(selector.coursesSelected, timeout=500) as signal:
        # Use the public API to select the first course
        selector.select_courses_by_code([sample_courses[0].course_code])
        qtbot.wait(100)

    # Verify that the emitted signal contains the correct course
    selected = signal.args[0]
    assert len(selected) == 1
    assert selected[0].course_code == sample_courses[0].course_code


def test_submit_emits_signal(qtbot, selector, sample_courses):
    selector.select_courses_by_code([sample_courses[0].course_code, sample_courses[2].course_code])
    qtbot.wait(100)
    # Test that clicking the submit button emits the `coursesSubmitted` signal
    with patch.object(selector, 'show_progress_bar', return_value=None):
        with qtbot.waitSignal(selector.coursesSubmitted, timeout=500) as signal:
            selector.submit_button.click()
    # Verify that the emitted signal contains the correct courses
    submitted = signal.args[0]
    assert len(submitted) == 2
    assert submitted[0].course_code == sample_courses[0].course_code

def test_clear_button_clears_selection(qtbot, selector, sample_courses):
    # Test that clicking the clear button clears all selected courses
    # Use the public API to select all courses
    selector.select_courses_by_code([c.course_code for c in sample_courses])
    qtbot.wait(100)

    # Simulate clicking the clear button
    selector.clear_button.click()
    # Verify that no courses are selected
    selected = selector.get_selected_courses()

    assert len(selected) == 0
    # Verify that the title label reflects the cleared state
    assert selector.title_label.text().endswith("total)")
