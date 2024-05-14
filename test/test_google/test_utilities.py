import json
import unittest
import os
import tempfile

from parsons.google import utitities as util


class FakeCredentialTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.cred_path = os.path.join(self.dir.name, "mycred.json")
        self.cred_contents = {
            "client_id": "foobar.apps.googleusercontent.com",
            "client_secret": str(hash("foobar")),
            "quota_project_id": "project-id",
            "refresh_token": str(hash("foobarfoobar")),
            "type": "authorized_user",
        }
        with open(self.cred_path, "w") as f:
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
        self.assertEqual(os.environ[self.TEST_ENV_NAME], self.cred_path)

    def test_accepts_dictionary(self):
        util.setup_google_application_credentials(self.cred_contents, self.TEST_ENV_NAME)
        actual = os.environ[self.TEST_ENV_NAME]
        self.assertTrue(os.path.exists(actual))
        with open(actual, "r") as f:
            self.assertEqual(json.load(f), self.cred_contents)

    def test_accepts_string(self):
        cred_str = json.dumps(self.cred_contents)
        util.setup_google_application_credentials(cred_str, self.TEST_ENV_NAME)
        actual = os.environ[self.TEST_ENV_NAME]
        self.assertTrue(os.path.exists(actual))
        with open(actual, "r") as f:
            self.assertEqual(json.load(f), self.cred_contents)

    def test_accepts_file_path(self):
        util.setup_google_application_credentials(self.cred_path, self.TEST_ENV_NAME)
        actual = os.environ[self.TEST_ENV_NAME]
        self.assertTrue(os.path.exists(actual))
        with open(actual, "r") as f:
            self.assertEqual(json.load(f), self.cred_contents)

    def test_credentials_are_valid_after_double_call(self):
        # write creds to tmp file...
        util.setup_google_application_credentials(self.cred_contents, self.TEST_ENV_NAME)
        fst = os.environ[self.TEST_ENV_NAME]

        # repeat w/ default args...
        util.setup_google_application_credentials(None, self.TEST_ENV_NAME)
        snd = os.environ[self.TEST_ENV_NAME]

        with open(fst, "r") as ffst:
            with open(snd, "r") as fsnd:
                actual = fsnd.read()
                self.assertEqual(self.cred_contents, json.loads(actual))
                self.assertEqual(ffst.read(), actual)


class TestHexavigesimal(unittest.TestCase):

    def test_returns_A_on_1(self):
        self.assertEqual(util.hexavigesimal(1), "A")

    def test_returns_AA_on_27(self):
        self.assertEqual(util.hexavigesimal(27), "AA")

    def test_returns_error_on_0(self):
        with self.assertRaises(ValueError):
            util.hexavigesimal(0)
