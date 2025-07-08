import pytest
from datetime import datetime
from src.services.academic_calender_parser import get_full_academic_year 

# List of expected events for parameterized testing
expected_events = [
    {"title": "חופשת חנוכה", "start": datetime(2024, 12, 29), "end": datetime(2024, 12, 30)},
    {"title": "צום י׳ בטבת", "start": datetime(2025, 1, 10), "end": datetime(2025, 1, 10)},
    {"title": "חופשת פורים", "start": datetime(2025, 3, 13), "end": datetime(2025, 3, 14)},
    {"title": "חופשת פסח", "start": datetime(2025, 4, 9), "end": datetime(2025, 4, 20)},
    {"title": "יום הזיכרון ויום העצמאות", "start": datetime(2025, 4, 30), "end": datetime(2025, 5, 1)},
    {"title": "חופשת יום ירושלים", "start": datetime(2025, 5, 26), "end": datetime(2025, 5, 26)},
    {"title": "חופשת חג שבועות", "start": datetime(2025, 6, 1), "end": datetime(2025, 6, 3)},
    {"title": "יום הסטודנט", "start": datetime(2025, 6, 5), "end": datetime(2025, 6, 5)},
    {"title": "צום י\"ז תמוז", "start": datetime(2025, 7, 13), "end": datetime(2025, 7, 13)},
    {"title": "צום ט׳ באב", "start": datetime(2025, 8, 3), "end": datetime(2025, 8, 3)},
]

def normalize(text):
    """Normalize text for comparison (e.g. geresh variations, extra spaces)"""
    return text.replace("״", "\"").replace("׳", "'").replace("״", '"').strip()

# Test the general structure of the function's output
def test_structure_of_result():
    """
    Ensure the output of get_full_academic_year is a dictionary
    containing 'semesters' and 'holidays' as lists.
    """
    data = get_full_academic_year()
    assert isinstance(data, dict), "Output should be a dictionary"
    assert "semesters" in data and "holidays" in data, "Should contain 'semesters' and 'holidays' keys"
    assert isinstance(data["semesters"], list), "'semesters' should be a list"
    assert isinstance(data["holidays"], list), "'holidays' should be a list"

# Test the structure and content of each semester
def test_semester_entries():
    """
    Check that each semester entry has the correct structure and valid dates.
    """
    data = get_full_academic_year()
    for sem in data["semesters"]:
        assert set(sem.keys()) == {"name", "start", "end"}, "Semester structure is invalid"
        assert isinstance(sem["name"], str), "Semester name should be a string"
        assert isinstance(sem["start"], datetime), "Semester start date should be datetime"
        assert isinstance(sem["end"], datetime), "Semester end date should be datetime"
        assert sem["start"] <= sem["end"], "Semester start date should be before end date"

# Test the structure and content of each holiday
def test_holiday_entries():
    """
    Check that each holiday entry has the correct structure and valid dates.
    """
    data = get_full_academic_year()
    for h in data["holidays"]:
        assert set(h.keys()) == {"title", "start", "end"}, "Holiday structure is invalid"
        assert isinstance(h["title"], str), "Holiday title should be a string"
        assert isinstance(h["start"], datetime), "Holiday start date should be datetime"
        assert isinstance(h["end"], datetime), "Holiday end date should be datetime"
        assert h["start"] <= h["end"], "Holiday start date should be before end date"

# Test that semester names include the expected ones
def test_expected_semesters_names():
    """
    Ensure that the expected semester names are present in the result.
    """
    data = get_full_academic_year()
    names = {s["name"] for s in data["semesters"]}
    expected = {"סמסטר א'", "סמסטר ב'", "סמסטר קיץ"}
    assert names.intersection(expected), "Expected semester names not found"

# Test that holiday titles include the expected ones
def test_expected_holidays_titles():
    """
    Ensure that the expected holiday titles are present in the result.
    """
    data = get_full_academic_year()
    titles = {h["title"] for h in data["holidays"]}
    expected = {
        "חופשת פורים",
        "חופשת פסח",
        "יום הזיכרון",
        "יום הזיכרון ויום העצמאות",
        "חופשת חג שבועות",
        "צום י\"ז תמוז",
        "צום ט' באב",
        "יום ירושלים"
    }
    matched = expected.intersection(titles)
    assert matched, f"Expected holiday titles not found. Found: {titles}"

@pytest.mark.parametrize("expected", expected_events)
def test_event_in_scraping_result(expected):
    """
    For each expected event, check that it appears in the holidays or semesters
    with the correct title and dates.
    """
    result = get_full_academic_year()
    actual_events = result["holidays"] + result["semesters"]

    match = next((
        e for e in actual_events
        if normalize(e.get("title", e.get("name", ""))) == normalize(expected["title"])
        and e["start"] == expected["start"]
        and e["end"] == expected["end"]
    ), None)

    assert match is not None, f"Event not found: {expected['title']} on dates {expected['start']} - {expected['end']}"
