import pytest
from src.api.schedule_api import ScheduleAPI
from src.data.file_handler import FileHandler
from src.core.scheduler import Scheduler
from src.core.all_strategy import AllStrategy
from src.core.conflict_checker import ConflictChecker
from src.data.parsers.text_parser import TextParser
from src.data.formatters.text_formatter import TextFormatter

@pytest.fixture
def real_api():
    # Use actual implementations
    parser = TextParser("data/generated_courses.txt")
    formatter = TextFormatter()
    file_handler = FileHandler(parser, formatter)

    # Scheduler will get updated by the API later
    scheduler = Scheduler([], AllStrategy([], ConflictChecker()))

    return ScheduleAPI(file_handler, scheduler)

def test_APP_INTEG_FLOW_001(real_api):
    """
    Test Case ID: APP_INTEG_FLOW_001
    Type: Integration

    Ensures the app reads input, parses courses and lecture groups, 
    and delegates to Scheduler for schedule generation.
    """
    with open("data/generated_courses.txt", "r") as f:
        raw_data = f.read()

    output = real_api.process(raw_data)

    # We expect output to be a non-empty string (indicating scheduling and formatting occurred)
    assert isinstance(output, str)
    assert len(output.strip()) > 0

def test_APP_END_TO_END_001(real_api):
    """
    Test Case ID: APP_END_TO_END_001
    Type: End-to-End

    Validates that the full workflow from reading a file to formatting output 
    returns a string that includes expected course identifiers.
    """
    with open("data/generated_courses.txt", "r") as f:
        raw_data = f.read()

    output = real_api.process(raw_data)

    # Example: Check that the formatted output includes known course codes or names
    assert "Math" in output or "M101" in output or "Schedule" in output
