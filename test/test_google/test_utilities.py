import json
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from parsons.google import utilities as util

TEST_ENV_NAME = "DUMMY_APP_CREDS"


@pytest.fixture
def fake_credentials():
    """Write a fake Google credentials file to a temp dir.

    Yields a namespace with ``cred_path`` (path to the file) and
    ``cred_contents`` (the dict written to it). The temp dir is cleaned up on
    teardown.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        cred_path = str(Path(tmp_dir) / "mycred.json")
        cred_contents = {
            "client_id": "foobar.apps.googleusercontent.com",
            "client_secret": str(hash("foobar")),
            "quota_project_id": "project-id",
            "refresh_token": str(hash("foobarfoobar")),
            "type": "authorized_user",
        }
        with Path(cred_path).open(mode="w") as f:
            json.dump(cred_contents, f)

        yield SimpleNamespace(cred_path=cred_path, cred_contents=cred_contents)


def test_noop_if_env_already_set(fake_credentials, monkeypatch):
    monkeypatch.setenv(TEST_ENV_NAME, fake_credentials.cred_path)
    util.setup_google_application_credentials(None, TEST_ENV_NAME)
    assert os.environ[TEST_ENV_NAME] == fake_credentials.cred_path


def test_accepts_dictionary(fake_credentials, monkeypatch):
    monkeypatch.delenv(TEST_ENV_NAME, raising=False)
    util.setup_google_application_credentials(fake_credentials.cred_contents, TEST_ENV_NAME)
    actual = Path(os.environ[TEST_ENV_NAME])
    assert actual.exists()
    with actual.open(mode="r") as f:
        assert json.load(f) == fake_credentials.cred_contents


def test_accepts_string(fake_credentials, monkeypatch):
    monkeypatch.delenv(TEST_ENV_NAME, raising=False)
    cred_str = json.dumps(fake_credentials.cred_contents)
    util.setup_google_application_credentials(cred_str, TEST_ENV_NAME)
    actual = Path(os.environ[TEST_ENV_NAME])
    assert actual.exists()
    with actual.open(mode="r") as f:
        assert json.load(f) == fake_credentials.cred_contents


def test_accepts_file_path(fake_credentials, monkeypatch):
    monkeypatch.delenv(TEST_ENV_NAME, raising=False)
    util.setup_google_application_credentials(fake_credentials.cred_path, TEST_ENV_NAME)
    actual = Path(os.environ[TEST_ENV_NAME])
    assert actual.exists()
    with actual.open(mode="r") as f:
        assert json.load(f) == fake_credentials.cred_contents


def test_credentials_are_valid_after_double_call(fake_credentials, monkeypatch):
    monkeypatch.delenv(TEST_ENV_NAME, raising=False)
    # write creds to tmp file...
    util.setup_google_application_credentials(fake_credentials.cred_contents, TEST_ENV_NAME)
    fst = os.environ[TEST_ENV_NAME]

    # repeat w/ default args...
    util.setup_google_application_credentials(None, TEST_ENV_NAME)
    snd = os.environ[TEST_ENV_NAME]

    actual = Path(snd).read_text()
    assert fake_credentials.cred_contents == json.loads(actual)
    assert Path(fst).read_text() == actual


def test_returns_A_on_1():
    assert util.hexavigesimal(1) == "A"


def test_returns_AA_on_27():
    assert util.hexavigesimal(27) == "AA"


def test_returns_error_on_0():
    with pytest.raises(ValueError, match="This function only works for positive integers"):
        util.hexavigesimal(0)
