from unittest.mock import MagicMock
from typing import Generator
import pytest
import requests_mock
import re


@pytest.fixture(autouse=True)
def mock_requests() -> Generator[MagicMock, None, None]:
    """Replace requests in api_connector with a mock client"""
    with requests_mock.Mocker() as mocker:
        mocker.post(requests_mock.ANY, json={"test": True})
        mocker.post(
            "https://auth.catalist.us/oauth/token",
            json={"access_token": "tokenexample", "expires_in": 99999, "test": True},
        )
        mocker.get(requests_mock.ANY, json=[{"test": True}])
        mocker.get(
            re.compile("/mapi/status/id/"),
            json={"process": {"processState": "Finished"}},
        )

        yield mocker


@pytest.fixture(autouse=True)
def mock_sftp(mocker) -> Generator[MagicMock, None, None]:
    """Replace sftp client with a mock client"""
    magic_mock = MagicMock()

    mocker.patch("parsons.catalist.catalist.SFTP", new=magic_mock)

    yield mocker


@pytest.fixture(autouse=True)
def mock_miscellaneous(mocker) -> Generator[MagicMock, None, None]:
    """Replace miscellaneous utilities with mocks to simplify testing"""
    magic_mock = MagicMock()

    mocker.patch("parsons.catalist.catalist.ZipFile", new=magic_mock)
    mocker.patch("parsons.catalist.catalist.os", new=magic_mock)
    mocker.patch("parsons.catalist.catalist.Table", new=magic_mock)

    yield mocker
