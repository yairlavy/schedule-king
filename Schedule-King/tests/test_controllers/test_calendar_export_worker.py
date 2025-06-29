import pytest
from unittest.mock import MagicMock, patch
from src.controllers.calendar_export_worker import CalendarExportWorker

# Dummy schedule class for testing
class DummySchedule:
    def extract_by_day(self):
        # Returns a mock schedule dictionary
        return {'2': [('Lecture', 'Test Course', 'C101', MagicMock())]}

def test_export_to_calendar_success(monkeypatch):
    # Patch ScheduleEventMaker to simulate successful event creation
    monkeypatch.setattr(
        'src.controllers.calendar_export_worker.ScheduleEventMaker',
        lambda semester=None: MagicMock(create_events=lambda s: True)
    )
    success, msg = CalendarExportWorker.export_to_calendar(DummySchedule(), 'Semester A')
    assert success is True
    assert 'successfully' in msg.lower()

def test_export_to_calendar_missing_credentials(monkeypatch):
    # Patch ScheduleEventMaker to raise FileNotFoundError (missing credentials)
    def raise_fnf(*a, **k): raise FileNotFoundError
    monkeypatch.setattr(
        'src.controllers.calendar_export_worker.ScheduleEventMaker',
        lambda semester=None: raise_fnf()
    )
    success, msg = CalendarExportWorker.export_to_calendar(DummySchedule(), 'Semester A')
    assert not success
    assert 'credentials' in msg.lower()

def test_export_to_calendar_permission_error(monkeypatch):
    # Patch ScheduleEventMaker to raise PermissionError
    def raise_perm(*a, **k): raise PermissionError
    monkeypatch.setattr(
        'src.controllers.calendar_export_worker.ScheduleEventMaker',
        lambda semester=None: raise_perm()
    )
    success, msg = CalendarExportWorker.export_to_calendar(DummySchedule(), 'Semester A')
    assert not success
    assert 'permission' in msg.lower()

def test_export_to_calendar_import_error(monkeypatch):
    # Patch ScheduleEventMaker to raise ImportError (missing dependencies)
    def raise_import(*a, **k): raise ImportError('google-api')
    monkeypatch.setattr(
        'src.controllers.calendar_export_worker.ScheduleEventMaker',
        lambda semester=None: raise_import()
    )
    success, msg = CalendarExportWorker.export_to_calendar(DummySchedule(), 'Semester A')
    assert not success
    assert 'missing required google calendar dependencies' in msg.lower()

def test_export_to_calendar_generic_error(monkeypatch):
    # Patch ScheduleEventMaker to raise a generic Exception
    def raise_other(*a, **k): raise Exception('other error')
    monkeypatch.setattr(
        'src.controllers.calendar_export_worker.ScheduleEventMaker',
        lambda semester=None: raise_other()
    )
    success, msg = CalendarExportWorker.export_to_calendar(DummySchedule(), 'Semester A')
    assert not success
    assert 'failed to initialize' in msg.lower() or 'failed to export' in msg.lower()

def test_run_invalid_schedule(monkeypatch):
    # Test run() with invalid (None) schedule
    worker = CalendarExportWorker(None)
    worker.export_finished = MagicMock()
    worker.run()
    worker.export_finished.emit.assert_called_with(
        False, 'Invalid schedule data. Please select a valid schedule.'
    )

def test_run_empty_schedule(monkeypatch):
    # Test run() with an empty schedule
    class EmptySchedule:
        def extract_by_day(self): return {}
    worker = CalendarExportWorker(EmptySchedule())
    worker.export_finished = MagicMock()
    worker.run()
    worker.export_finished.emit.assert_called_with(
        False, 'Schedule is empty. Please select a schedule with courses.'
    )

def test_run_success(monkeypatch):
    # Patch export_to_calendar to simulate a successful export
    monkeypatch.setattr(
        CalendarExportWorker,
        'export_to_calendar',
        staticmethod(lambda s, semester=None: (True, 'ok'))
    )
    worker = CalendarExportWorker(DummySchedule())
    worker.export_finished = MagicMock()
    worker.run()
    worker.export_finished.emit.assert_called_with(True, 'ok')

def test_run_interrupted(monkeypatch):
    # Test run() when the operation is interrupted by the user
    worker = CalendarExportWorker(DummySchedule())
    worker.export_finished = MagicMock()
    worker.isInterruptionRequested = MagicMock(return_value=True)
    worker.run()
    worker.export_finished.emit.assert_called_with(False, 'Export cancelled by user.')