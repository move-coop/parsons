import pytest

from parsons import Slack


@pytest.fixture
def slack(monkeypatch):
    """Provides a Slack connector built with a fake API token."""
    monkeypatch.setenv("SLACK_API_TOKEN", "SOME_API_TOKEN")
    return Slack()
