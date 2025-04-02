import pytest
from unittest.mock import Mock
from src.data.file_handler import FileHandler
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup
from src.data.models.schedule import Schedule

@pytest.fixture
def mock_parser():
    parser = Mock()
    parser.parse.return_value = (
        [Course("Math", "M101", "Dr. X", [], [], [])],
        [LectureGroup("Math", "M101", "Dr. X", None, None, None)]
    )
    return parser

@pytest.fixture
def mock_formatter():
    formatter = Mock()
    formatter.format.return_value = "Formatted Schedule Output"
    return formatter

@pytest.fixture
def file_handler(mock_parser, mock_formatter):
    return FileHandler(parser=mock_parser, formatter=mock_formatter)

def test_parse_returns_expected_data(file_handler, mock_parser):
    raw_data = "dummy input"
    courses, groups = file_handler.parse(raw_data)

    mock_parser.parse.assert_called_once_with(raw_data)

    assert isinstance(courses, list)
    assert isinstance(groups, list)
    assert isinstance(courses[0], Course)
    assert isinstance(groups[0], LectureGroup)

def test_format_returns_expected_string(file_handler, mock_formatter):
    dummy_schedule = [Mock(spec=Schedule)]
    output = file_handler.format(dummy_schedule)

    mock_formatter.format.assert_called_once_with(dummy_schedule)
    assert output == "Formatted Schedule Output"
