from parsons.pdi.pdi import PDI

import os
import pytest


@pytest.fixture
def live_pdi():
    # Generate a live PDI connection based on these env vars

    username = os.environ["PDI_USERNAME"]
    password = os.environ["PDI_PASSWORD"]
    api_token = os.environ["PDI_API_TOKEN"]

    pdi = PDI(username, password, api_token, qa_url=True)

    return pdi


@pytest.fixture
def mock_pdi(requests_mock):
    # Not meant to hit live api servers

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

    return pdi
