import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.services import token_fetcher as tf
import json

def test_fetch_success(monkeypatch):
    # Patch requests.post to return a mocked auth_url and state
    monkeypatch.setattr(tf, 'requests', MagicMock())
    tf.requests.post.return_value.json.return_value = {'auth_url': 'http://auth', 'state': 'abc'}
    tf.requests.post.return_value.raise_for_status = lambda: None
    # Patch webbrowser.open to prevent real browser opening
    monkeypatch.setattr(tf, 'webbrowser', MagicMock())
    # Patch polling: first call returns 202, second returns 200 with token
    poll_responses = [
        MagicMock(status_code=202, text='wait'),
        MagicMock(status_code=200, text='ok', json=lambda: {'token': json.dumps({'a': 1})})
    ]
    def poll(*a, **k):
        return poll_responses.pop(0)
    tf.requests.get.side_effect = poll
    # Patch Credentials.from_authorized_user_info to return dummy creds
    monkeypatch.setattr(tf, 'Credentials', MagicMock())
    tf.Credentials.from_authorized_user_info.return_value = 'creds'
    # Patch open for writing to a file
    m = mock_open()
    monkeypatch.setattr('builtins.open', m)
    # Run fetch and check that browser and file open were called
    tf.fetch()
    tf.webbrowser.open.assert_called_once()
    m.assert_called_once()

def test_fetch_error(monkeypatch):
    # Patch requests.post to raise an exception
    monkeypatch.setattr(tf, 'requests', MagicMock())
    tf.requests.post.side_effect = Exception('fail')
    tf.webbrowser = MagicMock()
    # Patch open to prevent file I/O
    with patch('builtins.open', mock_open()):
        tf.fetch()  # Should print error, not raise

def test_fetch_poll_error(monkeypatch):
    # Patch requests.post to return mocked auth_url and state
    monkeypatch.setattr(tf, 'requests', MagicMock())
    tf.requests.post.return_value.json.return_value = {'auth_url': 'http://auth', 'state': 'abc'}
    tf.requests.post.return_value.raise_for_status = lambda: None
    tf.webbrowser = MagicMock()
    # Patch requests.get to return error status code
    tf.requests.get.return_value = MagicMock(status_code=400, text='bad')
    # Patch open to prevent file I/O
    with patch('builtins.open', mock_open()):
        tf.fetch()  # Should print error, not raise

def test_fetch_file_write_error(monkeypatch):
    # Patch requests.post to return mocked auth_url and state
    monkeypatch.setattr(tf, 'requests', MagicMock())
    tf.requests.post.return_value.json.return_value = {'auth_url': 'http://auth', 'state': 'abc'}
    tf.requests.post.return_value.raise_for_status = lambda: None
    tf.webbrowser = MagicMock()
    # Patch polling to return token immediately
    poll_responses = [MagicMock(status_code=200, text='ok', json=lambda: {'token': json.dumps({'a': 1})})]
    tf.requests.get.side_effect = lambda *a, **k: poll_responses.pop(0)
    # Patch Credentials.from_authorized_user_info to return dummy creds
    monkeypatch.setattr(tf, 'Credentials', MagicMock())
    tf.Credentials.from_authorized_user_info.return_value = 'creds'
    # Patch open to raise exception on file write
    m = mock_open()
    m.side_effect = Exception('fail')
    monkeypatch.setattr('builtins.open', m)
    tf.fetch()  # Should print error, not raise 