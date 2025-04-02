import pytest
from unittest.mock import Mock
from src.api.schedule_api import ScheduleAPI
from src.data.models.course import Course
from src.data.models.schedule import Schedule

@pytest.fixture
def mock_file_handler():
    handler = Mock()
    handler.parse.return_value = (
        [Course("Math", "M101", "Dr. A", [], [], [])],
        []  # Lecture groups (not used)
    )
    handler.format.return_value = "Formatted output"
    return handler

@pytest.fixture
def mock_scheduler():
    scheduler = Mock()
    scheduler.generate.return_value = [Mock(spec=Schedule)]
    return scheduler

def test_process_runs_correctly(mock_file_handler, mock_scheduler):
    api = ScheduleAPI(file_handler=mock_file_handler, scheduler=mock_scheduler)

    raw_data = "some raw text from file"
    result = api.process(raw_data)

    # Validate method calls
    mock_file_handler.parse.assert_called_once_with(raw_data)
    mock_scheduler.generate.assert_called_once()
    mock_file_handler.format.assert_called_once()

    # Validate returned result
    assert result == "Formatted output"
