import os

import pytest


@pytest.fixture
def preserve_environ():
    """Snapshot ``os.environ`` and restore it after the test.

    Some utilities (e.g. ``credential_tools.decode_credential``) set environment
    variables directly, which would otherwise leak into other tests.
    """
    original = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original)
