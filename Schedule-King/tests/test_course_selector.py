import pytest
from PyQt5.QtWidgets import QApplication
from src.componnents.course_selector import CourseSelector  
from src.models.course import Course


@pytest.fixture
def sample_courses():
    # Fixture to provide a sample list of courses for testing
    return [
        Course("Intro to CS", "CS101", "Dr. Smith"),
        Course("Calculus", "MATH201", "Dr. Jones"),
        Course("Physics", "PHYS101", "Dr. Brown")
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
    assert selector.list_widget.count() == len(sample_courses)
    # Verify that the title label starts with "Available Courses"
    assert selector.title_label.text().startswith("Available Courses")


def test_selection_emits_signal(qtbot, selector, sample_courses):
    # Test that selecting a course emits the `coursesSelected` signal
    with qtbot.waitSignal(selector.coursesSelected, timeout=500) as signal:
        # Select the first item in the list
        item = selector.list_widget.item(0)
        item.setSelected(True)

    # Verify that the emitted signal contains the correct course
    selected = signal.args[0]
    assert len(selected) == 1
    assert selected[0].course_code == sample_courses[0].course_code


def test_submit_emits_signal(qtbot, selector, sample_courses):
    # Test that clicking the submit button emits the `coursesSubmitted` signal
    # Select two items in the list
    selector.list_widget.item(0).setSelected(True)
    selector.list_widget.item(2).setSelected(True)

    with qtbot.waitSignal(selector.coursesSubmitted, timeout=500) as signal:
        # Simulate clicking the submit button
        selector.submit_button.click()

    # Verify that the emitted signal contains the correct courses
    submitted = signal.args[0]
    assert len(submitted) == 2
    assert submitted[0].course_code == sample_courses[0].course_code


def test_clear_button_clears_selection(qtbot, selector):
    # Test that clicking the clear button clears all selected courses
    # Select all items in the list
    for i in range(selector.list_widget.count()):
        selector.list_widget.item(i).setSelected(True)

    # Simulate clicking the clear button
    selector.clear_button.click()
    # Verify that no courses are selected
    selected = selector.get_selected_courses()

    assert len(selected) == 0
    # Verify that the title label reflects the cleared state
    assert selector.title_label.text().endswith("total)")
