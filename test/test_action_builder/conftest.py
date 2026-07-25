import json

import pytest

from parsons import ActionBuilder

SUBDOMAIN = "fake_subdomain"
CAMPAIGN = "fake-campaign"
API_KEY = "fake_key"
API_URL = f"https://{SUBDOMAIN}.actionbuilder.org/api/rest/v1/campaigns/{CAMPAIGN}"


@pytest.fixture
def campaign() -> str:
    return CAMPAIGN


@pytest.fixture
def api_url() -> str:
    return API_URL


@pytest.fixture
def bldr() -> ActionBuilder:
    """An ActionBuilder connector wired to a fake subdomain/campaign.

    Construction makes no request, so no mock is needed here.
    """
    return ActionBuilder(api_token=API_KEY, subdomain=SUBDOMAIN, campaign=CAMPAIGN)


@pytest.fixture
def load(shared_datadir):
    """Load a canned Action Builder response from the data/ directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
