import sys
from unittest.mock import MagicMock, patch
import pytest
import requests
from main import format_datetime, github_user_activity


# 1. Tests for Helper Functions
def test_format_datetime_valid():
    """Test valid ISO 8601 timestamp conversion."""
    result = format_datetime("2026-08-19T02:54:48Z")
    assert result == "2026-08-19 02:54:48"


def test_format_datetime_empty():
    """Test handling of empty timestamp string."""
    assert format_datetime("") == ""


def test_format_datetime_invalid():
    """Test fallback when timestamp parsing fails."""
    invalid_str = "invalid-date-format"
    assert format_datetime(invalid_str) == invalid_str


# 2. Tests for CLI Arguments Validation
def test_cli_missing_username_argument(monkeypatch, capsys):
    """Test CLI behavior when no arguments are passed."""
    monkeypatch.setattr(sys, "argv", ["main.py"])

    with pytest.raises(SystemExit) as exc_info:
        github_user_activity()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Usage: python main.py <username>" in captured.out


def test_cli_empty_username_argument(monkeypatch, capsys):
    """Test CLI behavior when an empty string username is passed."""
    monkeypatch.setattr(sys, "argv", ["main.py", "   "])

    with pytest.raises(SystemExit) as exc_info:
        github_user_activity()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Username cannot be empty." in captured.out


# 3. Tests for Network, Request Validation & API Errors
@patch("main.requests.get")
def test_requests_get_called_with_correct_parameters(mock_get, monkeypatch):
    """Verify that requests.get is constructed with correct URL, headers, and timeout."""
    monkeypatch.setattr(sys, "argv", ["main.py", "testuser"])

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    github_user_activity()

    mock_get.assert_called_once_with(
        "https://api.github.com/users/testuser/events",
        headers={"User-Agent": "GitHub-Activity-CLI"},
        timeout=10,
    )


@patch("main.requests.get")
def test_api_user_not_found_404(mock_get, monkeypatch, capsys):
    """Test handling of 404 Not Found response."""
    monkeypatch.setattr(sys, "argv", ["main.py", "nonexistentuser"])

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    github_user_activity()

    captured = capsys.readouterr()
    assert "Error: User 'nonexistentuser' was not found." in captured.out


@patch("main.requests.get")
def test_api_rate_limit_exceeded_403(mock_get, monkeypatch, capsys):
    """Test handling of 403 Rate Limit response."""
    monkeypatch.setattr(sys, "argv", ["main.py", "someuser"])

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_get.return_value = mock_response

    github_user_activity()

    captured = capsys.readouterr()
    assert (
        "Error: API rate limit exceeded. Please try again later."
        in captured.out
    )


@patch("main.requests.get")
def test_api_server_error_500(mock_get, monkeypatch, capsys):
    """Test handling of HTTP 500 Internal Server Error."""
    monkeypatch.setattr(sys, "argv", ["main.py", "someuser"])

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "500 Server Error"
    )
    mock_get.return_value = mock_response

    github_user_activity()

    captured = capsys.readouterr()
    assert "HTTP Error occurred: 500 Server Error" in captured.out


@patch("main.requests.get")
def test_network_timeout(mock_get, monkeypatch, capsys):
    """Test handling of network timeout exception."""
    monkeypatch.setattr(sys, "argv", ["main.py", "someuser"])
    mock_get.side_effect = requests.exceptions.Timeout()

    github_user_activity()

    captured = capsys.readouterr()
    assert (
        "Error: Request timed out. Please check your network and try again."
        in captured.out
    )


@patch("main.requests.get")
def test_connection_error(mock_get, monkeypatch, capsys):
    """Test handling of connection error exception."""
    monkeypatch.setattr(sys, "argv", ["main.py", "someuser"])
    mock_get.side_effect = requests.exceptions.ConnectionError()

    github_user_activity()

    captured = capsys.readouterr()
    assert (
        "Error: Could not connect to GitHub. Please check your internet"
        " connection."
        in captured.out
    )


@patch("main.requests.get")
def test_invalid_json_payload(mock_get, monkeypatch, capsys):
    """Test handling of invalid JSON response from server."""
    monkeypatch.setattr(sys, "argv", ["main.py", "someuser"])

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError()
    mock_get.return_value = mock_response

    github_user_activity()

    captured = capsys.readouterr()
    assert "Error: Failed to parse JSON response from server." in captured.out


@patch("main.requests.get")
def test_unexpected_json_structure(mock_get, monkeypatch, capsys):
    """Test handling when response payload is not a list."""
    monkeypatch.setattr(sys, "argv", ["main.py", "someuser"])

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "Not a list"}
    mock_get.return_value = mock_response

    github_user_activity()

    captured = capsys.readouterr()
    assert (
        "Error: Unexpected data structure received from GitHub." in captured.out
    )


@patch("main.requests.get")
def test_empty_events_list(mock_get, monkeypatch, capsys):
    """Test output when user has no recent activity."""
    monkeypatch.setattr(sys, "argv", ["main.py", "someuser"])

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    github_user_activity()

    captured = capsys.readouterr()
    assert "No recent activity found for user 'someuser'." in captured.out


# 4. Tests for Event Formatting & Edge Cases
@patch("main.requests.get")
def test_push_event_payload_variations(mock_get, monkeypatch, capsys):
    """Test PushEvent logic for all commit calculation branches (size, commits list, default)."""
    monkeypatch.setattr(sys, "argv", ["main.py", "testuser"])

    mock_events = [
        {
            "type": "PushEvent",
            "repo": {"name": "user/repo1"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {"size": 5},
        },
        {
            "type": "PushEvent",
            "repo": {"name": "user/repo2"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {"commits": [{"id": "1"}, {"id": "2"}]},
        },
        {
            "type": "PushEvent",
            "repo": {"name": "user/repo3"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {},
        },
    ]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_events
    mock_get.return_value = mock_response

    github_user_activity()

    captured = capsys.readouterr().out
    assert "Pushed 5 commit(s) to user/repo1 on 2026-08-19 02:54:48" in captured
    assert "Pushed 2 commit(s) to user/repo2 on 2026-08-19 02:54:48" in captured
    assert "Pushed 1 commit(s) to user/repo3 on 2026-08-19 02:54:48" in captured


@patch("main.requests.get")
def test_all_event_types_formatting(mock_get, monkeypatch, capsys):
    """Test processing and output formatting for all other supported GitHub event types."""
    monkeypatch.setattr(sys, "argv", ["main.py", "testuser"])

    mock_events = [
        {
            "type": "IssuesEvent",
            "repo": {"name": "testuser/repo1"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {"action": "opened"},
        },
        {
            "type": "WatchEvent",
            "repo": {"name": "testuser/repo2"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {},
        },
        {
            "type": "CreateEvent",
            "repo": {"name": "testuser/repo2"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {"ref_type": "repository"},
        },
        {
            "type": "DeleteEvent",
            "repo": {"name": "testuser/repo2"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {"ref_type": "branch", "ref": "feature-x"},
        },
        {
            "type": "PullRequestEvent",
            "repo": {"name": "testuser/repo1"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {"action": "closed"},
        },
        {
            "type": "ForkEvent",
            "repo": {"name": "original/repo"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {"forkee": {"full_name": "testuser/repo"}},
        },
        {
            "type": "GollumEvent",
            "repo": {"name": "testuser/wiki"},
            "created_at": "2026-08-19T02:54:48Z",
            "payload": {},
        },
    ]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_events
    mock_get.return_value = mock_response

    github_user_activity()

    captured = capsys.readouterr().out
    assert "Opened an issue in testuser/repo1 on 2026-08-19 02:54:48" in captured
    assert "Starred testuser/repo2 on 2026-08-19 02:54:48" in captured
    assert "Created repository in testuser/repo2 on 2026-08-19 02:54:48" in captured
    assert (
        "Deleted branch 'feature-x' in testuser/repo2 on 2026-08-19 02:54:48"
        in captured
    )
    assert (
        "Closed a pull request in testuser/repo1 on 2026-08-19 02:54:48"
        in captured
    )
    assert (
        "Forked original/repo to testuser/repo on 2026-08-19 02:54:48"
        in captured
    )
    assert "GollumEvent in testuser/wiki on 2026-08-19 02:54:48" in captured