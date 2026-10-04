import os

import pytest
from requests_mock import Mocker

from parsons import PDI


@pytest.fixture
def live_pdi() -> PDI:
    """Provide PDI instance that uses live API servers authenticated using environment variables."""
    username = os.environ["PDI_USERNAME"]
    password = os.environ["PDI_PASSWORD"]
    api_token = os.environ["PDI_API_TOKEN"]

    return PDI(username, password, api_token, qa_url=True)


@pytest.fixture
def mock_pdi(requests_mock: Mocker) -> PDI:
    """Provide PDI instance without hitting live API servers during initial authentication."""
    requests_mock.post(
        "https://apiqa.bluevote.com/sessions",
        json={
            "AccessToken": "AccessToken",
            "ExpirationDate": "2100-01-01",
        },
    )

    username = "PDI_USERNAME"
    password = "PDI_PASSWORD"
    api_token = "PDI_API_TOKEN"

    pdi = PDI(username, password, api_token, qa_url=True)
    requests_mock.reset_mock()

    return pdi
