import os
from pathlib import Path
import pytest
from unittest.mock import patch
from src.api.schedule_api import ScheduleAPI

# Fixture to load the test file and create ScheduleAPI instance
@pytest.fixture
def schedule_api(tmp_path):
    # Get absolute paths for test files
    base_dir = os.path.dirname(__file__)
    input_file_path = os.path.join(base_dir, "test_files", "input_test_api.txt")
    output_file = tmp_path / "output.txt"
    
    # Create the ScheduleAPI instance
    api = ScheduleAPI(file_path=input_file_path, output_path=str(output_file))
    return api

def test_process_single_course(schedule_api):
    print("Running test_process_single_course with course_codes=['00001']")
    output = schedule_api.process(course_codes=["00001"])  # Expecting Calculus 1
    print(f"Output for test_process_single_course:\n{output}")
    assert output is not None
    assert "Calculus 1" in output

def test_process_multiple_courses(schedule_api):
    print("Running test_process_multiple_courses with course_codes=['00001', '83533']")
    output = schedule_api.process(course_codes=["00001", "83533"])  # Expecting Calculus 1 + Software Project
    print(f"Output for test_process_multiple_courses:\n{output}")
    assert output is not None
    assert "Calculus 1" in output
    assert "Software Project" in output

def test_invalid_course_code(schedule_api, capsys):
    """
    Test behavior when an invalid course code is provided.
    First, an invalid code ("99999") is given, then a valid code ("00001") is provided.
    """
    with patch('builtins.input', side_effect=["99999", "00001"]):
        output = schedule_api.process()  # No course_codes provided; will prompt for input.
        print(f"Output for test_invalid_course_code:\n{output}")
        captured = capsys.readouterr()
        # Check that the error message was printed
        assert "Warning: Course code '99999' not found. Skipping." in captured.out

        # After correction, the output should include Calculus 1.
        assert output is not None
        assert "Calculus 1" in output

def test_exceed_course_limit(schedule_api, capsys):
    """
    Simulate too many course codes being entered, then retry with valid codes.
    The first input exceeds the limit of 7 courses, which return none.
    The second input is valid and should succeed.
    """
    # First input: 8 courses (invalid), triggers re-prompt
    # Second input: 3 courses (valid), should pass
    inputs = [
        "00001 83533 83112 10001 10002 10003 10004 10005",  # invalid: 8 courses
        "00001 83533 83112"  # valid: 3 courses
    ]

    with patch("builtins.input", side_effect=inputs):
        schedule_api.process()
        captured = capsys.readouterr()

        # Check that error message was printed
        assert "Error: Cannot select more than 7 courses." in captured.out
        
        assert "Selected Courses:" in captured.out
        assert "Calculus 1" in captured.out
        assert "Software Project" in captured.out
        assert "Calculus 1 (eng)" in captured.out

def test_output_file_contains_all_schedules(schedule_api):
    """
    Test that after processing, the output file contains all the generated schedules.
    """
    schedule_api.process(course_codes=["00001"])
    output_file = Path(schedule_api.file_handler.formatter.path)
    content = output_file.read_text(encoding="utf-8")
    print(f"File content for test_output_file_contains_all_schedules:\n{content}")
    # Check that the file content contains schedule separators and schedule labels.
    assert "Schedule 1:" in content
    # Check for at least one valid day label.
    assert any(day in content for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])


def test_output_matches_expected(tmp_path):
    # Get absolute paths for test files
    base_dir = os.path.dirname(__file__)
    input_file_path = os.path.join(base_dir, "test_files", "input_test_api.txt")
    expected_output = os.path.join(base_dir, "test_files", "expected_test_api_output.txt")
    actual_output = tmp_path / "actual_output.txt"

    # Create the ScheduleAPI instance
    schedule_api = ScheduleAPI(file_path=input_file_path, output_path=actual_output)

    # Patch input to simulate user entering 3 course codes
    with patch("builtins.input", return_value="00001 83533 83112"):
        schedule_api.process()

        # Read the content of both files
    with open(actual_output, "r", encoding="utf-8") as actual_file:
        actual_content = actual_file.read()

    with open(expected_output, "r", encoding="utf-8") as expected_file:
        expected_content = expected_file.read()

    # Compare actual output file to expected file
    assert actual_content == expected_content

    with patch("builtins.input", return_value="83533 83112"):
        schedule_api.process()

    # Read the content of both files again
    with open(actual_output, "r", encoding="utf-8") as actual_file:
        actual_content = actual_file.read()
    
    assert actual_content != expected_content