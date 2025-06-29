import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from src.services.schedule_event_maker import ScheduleEventMaker

# Fixture providing minimal academic data for testing
@pytest.fixture
def mock_academic_data():
    return {
        'semesters': [
            {'name': 'Semester A', 'start': datetime(2024, 3, 1), 'end': datetime(2024, 6, 30)},
            {'name': 'Semester B', 'start': datetime(2024, 10, 1), 'end': datetime(2025, 1, 31)},
        ],
        'holidays': [
            {'title': 'Holiday X', 'start': datetime(2024, 4, 10), 'end': datetime(2024, 4, 12)},
            {'title': 'Holiday Y', 'start': datetime(2024, 5, 1), 'end': datetime(2024, 5, 2)},
        ]
    }

# Fixture to patch GoogleCalendarManager with a mock
@pytest.fixture
def patch_gcal_manager(monkeypatch):
    mock_manager = MagicMock()
    mock_manager.get_or_create_academic_calendar.return_value = 'mock_calendar_id'
    mock_manager.service.events.return_value.insert.return_value.execute.return_value = {'id': 'event_id'}
    monkeypatch.setattr('src.services.schedule_event_maker.GoogleCalendarManager', lambda: mock_manager)
    return mock_manager

# Fixture to patch the academic year parser to return mock data
@pytest.fixture
def patch_academic_parser(monkeypatch, mock_academic_data):
    monkeypatch.setattr('src.services.schedule_event_maker.get_full_academic_year', lambda: mock_academic_data)

# Fixture to create a ScheduleEventMaker instance with dependencies patched
@pytest.fixture
def event_maker(patch_gcal_manager, patch_academic_parser):
    return ScheduleEventMaker(semester='Semester A')

# Test getting the current semester by name
def test_get_current_semester_by_name(event_maker):
    sem = event_maker._get_current_semester()
    assert sem['name'] == 'Semester A'

# Test getting the current semester by date (patching datetime.now)
def test_get_current_semester_by_date(patch_gcal_manager, patch_academic_parser):
    em = ScheduleEventMaker()
    # Patch datetime.now to a date in Semester B
    with patch('src.services.schedule_event_maker.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2024, 10, 15)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        sem = em._get_current_semester()
        assert sem['name'] == 'Semester B'

# Test if a date is recognized as a holiday
def test_is_holiday_date(event_maker):
    # Date in Holiday X
    holiday = event_maker._is_holiday_date(datetime(2024, 4, 11))
    assert holiday['title'] == 'Holiday X'
    # Date not in any holiday
    assert event_maker._is_holiday_date(datetime(2024, 3, 15)) is None

# Test getting all holiday dates within a semester
def test_get_all_holiday_dates_in_semester(event_maker, mock_academic_data):
    semester = mock_academic_data['semesters'][0]
    holiday_dates = event_maker._get_all_holiday_dates_in_semester(semester)
    # Should include all dates in Holiday X and Y that are within semester
    assert datetime(2024, 4, 10).date() in holiday_dates
    assert datetime(2024, 4, 12).date() in holiday_dates
    assert datetime(2024, 5, 1).date() in holiday_dates
    assert datetime(2024, 5, 2).date() in holiday_dates
    # Should not include dates outside holidays
    assert datetime(2024, 3, 15).date() not in holiday_dates

# Test that create_events calls Google Calendar API for event creation
def test_create_events_calls_gcal(event_maker):
    # Mock schedule with extract_by_day
    mock_schedule = MagicMock()
    # One lesson on Monday (day '2')
    slot = MagicMock()
    slot.start_time = datetime.strptime('10:00', '%H:%M').time()
    slot.end_time = datetime.strptime('12:00', '%H:%M').time()
    slot.building = 'Bldg'
    slot.room = '101'
    slot.lecturer = 'Dr. X'
    mock_schedule.extract_by_day.return_value = {
        '2': [('Lecture', 'Test Course', 'C101', slot)]
    }
    # Should return True and call insert
    result = event_maker.create_events(mock_schedule)
    assert result is True
    # Check that GoogleCalendarManager's insert was called (holiday + lesson + semester events)
    calls = event_maker.calendar_manager.service.events().insert.call_args_list
    assert any('Test Course' in str(call) for call in calls)

# Test create_events returns False if no semester is found
def test_create_events_no_semester(event_maker, monkeypatch):
    # Patch _get_current_semester to return None
    monkeypatch.setattr(event_maker, '_get_current_semester', lambda: None)
    mock_schedule = MagicMock()
    result = event_maker.create_events(mock_schedule)
    assert result is False 