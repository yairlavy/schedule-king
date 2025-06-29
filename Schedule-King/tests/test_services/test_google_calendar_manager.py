import pytest
from unittest.mock import MagicMock, patch
from src.services.GoogleCalenderManager import GoogleCalendarManager

# Fixture to mock authentication and verification methods
@pytest.fixture
def mock_auth(monkeypatch):
    # Patch authentication and verification
    monkeypatch.setattr('src.services.GoogleCalenderManager.authenticate_google_account', lambda: 'creds')
    monkeypatch.setattr('src.services.GoogleCalenderManager.verify_credentials', lambda creds: True)
    monkeypatch.setattr('src.services.GoogleCalenderManager.force_reauthentication', lambda: True)

# Fixture to mock the Google API service build
@pytest.fixture
def mock_service(monkeypatch):
    # Patch build to return a mock service
    mock_service = MagicMock()
    monkeypatch.setattr('src.services.GoogleCalenderManager.build', lambda *a, **k: mock_service)
    return mock_service

# Test successful initialization of GoogleCalendarManager
def test_init_success(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    assert mgr.creds == 'creds'
    assert mgr.service is mock_service

# Test initialization with reauthentication after failed verification
def test_init_reauth_success(monkeypatch, mock_service):
    # First verify fails, then succeeds after reauth
    monkeypatch.setattr('src.services.GoogleCalenderManager.authenticate_google_account', lambda: 'creds')
    monkeypatch.setattr('src.services.GoogleCalenderManager.verify_credentials', lambda creds: False)
    monkeypatch.setattr('src.services.GoogleCalenderManager.force_reauthentication', lambda: True)
    # After reauth, verify returns True
    calls = {'count': 0}
    def verify(creds):
        calls['count'] += 1
        return calls['count'] > 1
    monkeypatch.setattr('src.services.GoogleCalenderManager.verify_credentials', verify)
    mgr = GoogleCalendarManager()
    assert mgr.creds == 'creds'
    assert mgr.service is mock_service

# Test initialization failure when authentication fails
def test_init_auth_fail(monkeypatch):
    monkeypatch.setattr('src.services.GoogleCalenderManager.authenticate_google_account', lambda: 'creds')
    monkeypatch.setattr('src.services.GoogleCalenderManager.verify_credentials', lambda creds: False)
    monkeypatch.setattr('src.services.GoogleCalenderManager.force_reauthentication', lambda: False)
    with patch('src.services.GoogleCalenderManager.build'):
        with pytest.raises(Exception):
            GoogleCalendarManager()

# Test successful creation of an academic calendar
def test_create_academic_calendar_success(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.calendars().insert().execute.return_value = {'id': 'calid'}
    calid = mgr.create_academic_calendar('TestCal', 'desc')
    assert calid == 'calid'

# Test failure to create an academic calendar
def test_create_academic_calendar_fail(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.calendars().insert().execute.side_effect = Exception('fail')
    calid = mgr.create_academic_calendar('TestCal', 'desc')
    assert calid is None

# Test finding an existing academic calendar
def test_get_or_create_academic_calendar_found(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.calendarList().list().execute.return_value = {'items': [{'summary': 'TestCal', 'id': 'calid'}]}
    calid = mgr.get_or_create_academic_calendar('TestCal')
    assert calid == 'calid'

# Test creating a new academic calendar when not found
def test_get_or_create_academic_calendar_create(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.calendarList().list().execute.return_value = {'items': []}
    mgr.create_academic_calendar = MagicMock(return_value='newid')
    calid = mgr.get_or_create_academic_calendar('TestCal')
    assert calid == 'newid'

# Test error handling when listing calendars fails
def test_get_or_create_academic_calendar_error(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.calendarList().list().execute.side_effect = Exception('fail')
    calid = mgr.get_or_create_academic_calendar('TestCal')
    assert calid is None

# Test successful deletion of a calendar
def test_delete_calendar_success(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    result = mgr.delete_calendar('calid')
    assert result is True

# Test failure to delete a calendar
def test_delete_calendar_fail(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.calendars().delete().execute.side_effect = Exception('fail')
    result = mgr.delete_calendar('calid')
    assert result is False

# Test successful creation of an event
def test_create_event_success(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.events().insert().execute.return_value = {'htmlLink': 'link'}
    event = mgr.create_event('sum', 'desc', '2024-01-01T10:00:00', '2024-01-01T11:00:00', 'calid', '5')
    assert event['htmlLink'] == 'link'

# Test failure to create an event
def test_create_event_fail(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.events().insert().execute.side_effect = Exception('fail')
    event = mgr.create_event('sum', 'desc', '2024-01-01T10:00:00', '2024-01-01T11:00:00', 'calid', '5')
    assert event is None

# Test successful deletion of an event
def test_delete_event_success(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    result = mgr.delete_event('eid', 'calid')
    assert result is True

# Test failure to delete an event
def test_delete_event_fail(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.events().delete().execute.side_effect = Exception('fail')
    result = mgr.delete_event('eid', 'calid')
    assert result is False

# Test successful connection test to Google Calendar
def test_test_connection_success(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.calendars().get().execute.return_value = {'summary': 'Primary'}
    assert mgr.test_connection() is True

# Test failed connection test to Google Calendar
def test_test_connection_fail(mock_auth, mock_service):
    mgr = GoogleCalendarManager()
    mock_service.calendars().get().execute.side_effect = Exception('fail')
    assert mgr.test_connection() is False 