import pytest

from parsons import Braintree

MERCHANT_ID = "abcd1234abcd1234"
MERCHANT_URL = f"https://api.braintreegateway.com:443/merchants/{MERCHANT_ID}"


@pytest.fixture
def merchant_url() -> str:
    return MERCHANT_URL


@pytest.fixture
def braintree() -> Braintree:
    """A Braintree connector with fake credentials (construction makes no request)."""
    return Braintree(
        merchant_id=MERCHANT_ID,
        public_key="abcd1234abcd1234",
        private_key="abcd1234abcd1234abcd1234abcd1234",
    )


@pytest.fixture
def xml(shared_datadir):
    """Read a canned Braintree XML response from the data/ directory."""

    def _xml(name: str) -> str:
        return (shared_datadir / f"{name}.xml").read_text()

    return _xml
