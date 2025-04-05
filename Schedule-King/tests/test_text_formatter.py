import os
import pytest
from src.data.formatters.text_formatter import TextFormatter
from src.data.models.schedule import Schedule
from src.data.models.lecture_group import LectureGroup
from src.data.models.time_slot import TimeSlot


# ---------------- Fixtures ----------------

@pytest.fixture
def time_slots():
    return [
        TimeSlot("2", "16:00", "17:00", "1100", "22"),
        TimeSlot("5", "10:00", "16:00", "605", "061"),
        TimeSlot("1", "14:00", "16:00", "1401", "4"),
        TimeSlot("3", "09:00", "11:00", "303", "12"),
        TimeSlot("4", "13:00", "15:00", "404", "18"),
        TimeSlot("2", "08:00", "09:30", "606", "7"),
        TimeSlot("3", "11:30", "13:00", "707", "15"),
    ]


@pytest.fixture
def lecture_groups(time_slots):
    return [
        LectureGroup("Calculus 1", "00001", "Prof. O. Some", time_slots[0], [], []),
        LectureGroup("Software Project", "83533", "Dr. Terry Bell", time_slots[1], [], []),
        LectureGroup("Calculus 1 (eng)", "83112", "Dr. Erez Scheiner", time_slots[2], time_slots[0], []),
        LectureGroup("Physics 1", "12345", "Dr. Isaac Newton", time_slots[3], [], []),
        LectureGroup("Linear Algebra", "67890", "Prof. Alan Turing", time_slots[4], [], []),
        LectureGroup("Data Structures", "54321", "Dr. Grace Hopper", time_slots[5], [], []),
        LectureGroup("Algorithms", "98765", "Prof. Donald Knuth", time_slots[6], [], []),
    ]


@pytest.fixture
def sample_schedule(lecture_groups):
    return Schedule(lecture_groups=lecture_groups)


@pytest.fixture
def more_then_one_schedule(lecture_groups):
    return [
        Schedule(lecture_groups=[lecture_groups[0], lecture_groups[1]]),
        Schedule(lecture_groups=[lecture_groups[2], lecture_groups[3]]),
        Schedule(lecture_groups=[lecture_groups[4], lecture_groups[5]]),
        Schedule(lecture_groups=[lecture_groups[6]]),
    ]


# ---------------- Tests ----------------

def test_format_single_schedule_to_text(sample_schedule):
    formatter = TextFormatter(path="unused.txt")
    output = formatter.formatText([sample_schedule])

    assert "Schedule 1" in output, "Missing schedule label"
    assert "Calculus 1" in output
    assert any(day in output for day in ["Sunday", "Monday", "Tuesday"]), "No valid days found"
    assert "[Lecture]" in output
    assert "Room" in output and "Building" in output


def test_format_multiple_schedules_to_text(more_then_one_schedule):
    formatter = TextFormatter(path="unused.txt")
    output = formatter.formatText(more_then_one_schedule)

    assert output.count("Schedule") == 4, "Not all schedules included"
    course_names = ["Calculus 1", "Software Project", "Calculus 1 (eng)",
                    "Physics 1", "Linear Algebra", "Data Structures", "Algorithms"]
    for name in course_names:
        assert name in output, f"Missing course: {name}"


def test_format_raises_on_empty_schedule():
    formatter = TextFormatter(path="temp.txt")
    with pytest.raises(ValueError, match="No schedules available to format"):
        formatter.format([])


def test_schedule_to_text_days_are_valid(sample_schedule):
    formatter = TextFormatter(path="unused.txt")
    output = formatter.scheduleToText(sample_schedule)

    for line in output.splitlines():
        if line.endswith(":"):
            day = line.strip(":")
            assert day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], f"Invalid day: {day}"


def test_export_creates_file(tmp_path, more_then_one_schedule):
    file_path = tmp_path / "output_schedule.txt"
    formatter = TextFormatter(path=str(file_path))
    formatter.format(more_then_one_schedule)

    assert file_path.exists(), "File was not created"
    content = file_path.read_text(encoding="utf-8")
    assert "Schedule 1" in content
    assert "Algorithms" in content

def test_text_formatter_repr(sample_schedule):
    formatter = TextFormatter(path="unused.txt")
    formatter.schedules = [sample_schedule] * 2
    assert repr(formatter) == "<TextFormatter with 2 schedules>"
