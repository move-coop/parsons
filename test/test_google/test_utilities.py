import json
import os
import tempfile
import unittest
from pathlib import Path

import pytest

from parsons.google import utilities as util


class FakeCredentialTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.cred_path = str(Path(self.dir.name) / "mycred.json")
        self.cred_contents = {
            "client_id": "foobar.apps.googleusercontent.com",
            "client_secret": str(hash("foobar")),
            "quota_project_id": "project-id",
            "refresh_token": str(hash("foobarfoobar")),
            "type": "authorized_user",
        }
        with Path(self.cred_path).open(mode="w") as f:
            json.dump(self.cred_contents, f)

    def tearDown(self) -> None:
        self.dir.cleanup()


class TestSetupGoogleApplicationCredentials(FakeCredentialTest):
    TEST_ENV_NAME = "DUMMY_APP_CREDS"

    def tearDown(self) -> None:
        super().tearDown()
        del os.environ[self.TEST_ENV_NAME]

    def test_noop_if_env_already_set(self):
        os.environ[self.TEST_ENV_NAME] = self.cred_path
        util.setup_google_application_credentials(None, self.TEST_ENV_NAME)
        assert os.environ[self.TEST_ENV_NAME] == self.cred_path

    def test_accepts_dictionary(self):
        util.setup_google_application_credentials(self.cred_contents, self.TEST_ENV_NAME)
        actual = Path(os.environ[self.TEST_ENV_NAME])
        self.assertTrue(actual.exists())
        with actual.open(mode="r") as f:
            self.assertEqual(json.load(f), self.cred_contents)

    def test_accepts_string(self):
        cred_str = json.dumps(self.cred_contents)
        util.setup_google_application_credentials(cred_str, self.TEST_ENV_NAME)
        actual = Path(os.environ[self.TEST_ENV_NAME])
        self.assertTrue(actual.exists())
        with actual.open(mode="r") as f:
            self.assertEqual(json.load(f), self.cred_contents)

    def test_accepts_file_path(self):
        util.setup_google_application_credentials(self.cred_path, self.TEST_ENV_NAME)
        actual = Path(os.environ[self.TEST_ENV_NAME])
        self.assertTrue(actual.exists())
        with actual.open(mode="r") as f:
            self.assertEqual(json.load(f), self.cred_contents)

    def test_credentials_are_valid_after_double_call(self):
        # write creds to tmp file...
        util.setup_google_application_credentials(self.cred_contents, self.TEST_ENV_NAME)
        fst = os.environ[self.TEST_ENV_NAME]

        # repeat w/ default args...
        util.setup_google_application_credentials(None, self.TEST_ENV_NAME)
        snd = os.environ[self.TEST_ENV_NAME]

        actual = Path(snd).read_text()
        self.assertEqual(self.cred_contents, json.loads(actual))
        self.assertEqual(Path(fst).read_text(), actual)


class TestHexavigesimal(unittest.TestCase):
    def test_returns_A_on_1(self):
        assert util.hexavigesimal(1) == "A"

    def test_returns_AA_on_27(self):
        assert util.hexavigesimal(27) == "AA"

    def test_returns_error_on_0(self):
        with pytest.raises(ValueError, match="This function only works for positive integers"):
            util.hexavigesimal(0)
