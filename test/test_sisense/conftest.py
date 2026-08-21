import pytest

from parsons import Sisense


@pytest.fixture
def sisense() -> Sisense:
    """
    A Sisense connector wired to fake credentials.

    Sisense is built on APIConnector, so tests mock the HTTP boundary with the
    ``requests_mock`` fixture. Construction makes no network call.
    """
    return Sisense(site_name="my_site_name", api_key="my_api_key")
