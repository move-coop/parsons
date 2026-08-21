import pytest

from parsons import ActionKit


@pytest.fixture
def ak(requests_mock):
    """An ActionKit connector with fake credentials.

    Construction opens a ``requests.Session`` (``ActionKit._conn``) but makes no
    request. ``requests_mock`` is requested here so that Session — and the throwaway
    one ``bulk_upload_csv`` builds for multipart uploads — is intercepted at the HTTP
    boundary for the whole test.
    """
    return ActionKit(domain="domain.actionkit.com", username="user", password="password")
