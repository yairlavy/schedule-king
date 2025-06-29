import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import pickle
from src.services import google_authenticatior as ga

# Test that verify_credentials returns True when the service call succeeds
def test_verify_credentials_success(monkeypatch):
    mock_service = MagicMock()
    mock_service.calendars().get().execute.return_value = {}
    monkeypatch.setattr(ga, 'build', lambda *a, **k: mock_service)
    creds = MagicMock()
    assert ga.verify_credentials(creds) is True

# Test that verify_credentials returns False when the service call raises an exception
def test_verify_credentials_fail(monkeypatch):
    mock_service = MagicMock()
    mock_service.calendars().get().execute.side_effect = Exception('fail')
    monkeypatch.setattr(ga, 'build', lambda *a, **k: mock_service)
    creds = MagicMock()
    assert ga.verify_credentials(creds) is False

# Test loading credentials from disk when the file exists and is valid
def test_load_creds_from_disk_success(monkeypatch):
    creds = {'token': 'abc'}
    m = mock_open(read_data=pickle.dumps(creds))
    monkeypatch.setattr('builtins.open', m)
    monkeypatch.setattr(os.path, 'exists', lambda p: True)
    assert ga._load_creds_from_disk() == creds

# Test loading credentials from disk when the file does not exist
def test_load_creds_from_disk_no_file(monkeypatch):
    monkeypatch.setattr(os.path, 'exists', lambda p: False)
    assert ga._load_creds_from_disk() is None

# Test loading credentials from disk when an exception occurs
def test_load_creds_from_disk_error(monkeypatch):
    m = mock_open()
    m.side_effect = Exception('fail')
    monkeypatch.setattr('builtins.open', m)
    monkeypatch.setattr(os.path, 'exists', lambda p: True)
    assert ga._load_creds_from_disk() is None

# Test saving credentials to disk successfully
def test_save_success(monkeypatch):
    creds = MagicMock()
    m = mock_open()
    monkeypatch.setattr('builtins.open', m)
    ga._save(creds)
    m.assert_called_once()

# Test saving credentials to disk when an exception occurs (should not raise)
def test_save_error(monkeypatch):
    creds = MagicMock()
    m = mock_open()
    m.side_effect = Exception('fail')
    monkeypatch.setattr('builtins.open', m)
    ga._save(creds)  # Should not raise

# Test force_reauthentication when file exists and remove succeeds
def test_force_reauthentication_success(monkeypatch):
    monkeypatch.setattr(os.path, 'exists', lambda p: True)
    monkeypatch.setattr(os, 'remove', lambda p: True)
    assert ga.force_reauthentication() is True

# Test force_reauthentication when remove raises an exception
def test_force_reauthentication_error(monkeypatch):
    monkeypatch.setattr(os.path, 'exists', lambda p: True)
    monkeypatch.setattr(os, 'remove', lambda p: (_ for _ in ()).throw(Exception('fail')))
    assert ga.force_reauthentication() is False

# Test authenticate_google_account returns valid creds from disk
def test_authenticate_google_account_valid(monkeypatch):
    creds = MagicMock()
    monkeypatch.setattr(ga, '_load_creds_from_disk', lambda: creds)
    monkeypatch.setattr(ga, 'verify_credentials', lambda c: True)
    assert ga.authenticate_google_account() == creds

# Test authenticate_google_account refreshes creds if not valid but has refresh_token
def test_authenticate_google_account_refresh(monkeypatch):
    creds = MagicMock()
    creds.valid = False
    creds.refresh_token = True
    monkeypatch.setattr(ga, '_load_creds_from_disk', lambda: creds)
    monkeypatch.setattr(ga, 'verify_credentials', lambda c: True)
    monkeypatch.setattr(creds, 'refresh', lambda req: None)
    monkeypatch.setattr(ga, '_save', lambda c: None)
    assert ga.authenticate_google_account() == creds

# Test authenticate_google_account fetches new creds if none are valid
def test_authenticate_google_account_fetch(monkeypatch):
    # No valid creds, fetch is called
    monkeypatch.setattr(ga, '_load_creds_from_disk', lambda: None)
    monkeypatch.setattr(ga, 'verify_credentials', lambda c: False)
    monkeypatch.setattr(ga, 'fetch', lambda: None)
    # Second call returns valid creds and verify returns True for it
    class DummyCreds:
        valid = True
        refresh_token = True
    creds = DummyCreds()
    calls = {'count': 0}
    def load():
        calls['count'] += 1
        return creds if calls['count'] > 1 else None
    monkeypatch.setattr(ga, '_load_creds_from_disk', load)
    monkeypatch.setattr(ga, 'verify_credentials', lambda c: c is creds)
    assert ga.authenticate_google_account() == creds

# Test authenticate_google_account raises RuntimeError if fetch fails
def test_authenticate_google_account_fetch_fail(monkeypatch):
    monkeypatch.setattr(ga, '_load_creds_from_disk', lambda: None)
    monkeypatch.setattr(ga, 'verify_credentials', lambda c: False)
    monkeypatch.setattr(ga, 'fetch', lambda: (_ for _ in ()).throw(Exception('fail')))
    with pytest.raises(RuntimeError):
        ga.authenticate_google_account() 