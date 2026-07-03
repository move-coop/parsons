from pathlib import Path

import pytest

from parsons import GitHub

_dir = Path(__file__).parent


@pytest.fixture(scope="module")
def get_repo_response_text() -> str:
    return (_dir / "test_data" / "test_get_repo.json").read_text()


@pytest.fixture
def github_client() -> GitHub:
    return GitHub()
