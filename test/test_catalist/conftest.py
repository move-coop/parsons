import re
import shutil

import pytest
import requests_mock


@pytest.fixture(autouse=True)
def mock_requests():
    """Mock API responses to prevent real network traffic."""
    with requests_mock.Mocker() as mocker:
        # Mock OAuth2 Token logic
        mocker.post(
            "https://auth.catalist.us/oauth/token",
            json={"access_token": "tokenexample", "expires_in": 99999},
        )
        # Mock Default GET (used for some connection checks)
        mocker.get(requests_mock.ANY, json=[{"test": True, "id": "12345"}])
        # Mock Job Status
        mocker.get(
            re.compile("/mapi/status/id/"),
            json={"process": {"processState": "Finished"}},
        )
        yield mocker


@pytest.fixture
def fake_sftp_backend(tmp_path, mocker):
    """
    Replaces the Parsons SFTP client with a local file-system version.
    Ensures that .gz files are actually created and moved.
    """

    class FakeSFTP:
        def __init__(self, host, user, password, **kwargs):
            self.root = tmp_path
            (self.root / "myUploads").mkdir(parents=True, exist_ok=True)
            (self.root / "myDownloads").mkdir(parents=True, exist_ok=True)

        def put_file(self, local_path, remote_path):
            dest = self.root / remote_path.lstrip("/")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(local_path), str(dest))

        def list_directory(self, path):
            target = self.root / path.lstrip("/")
            if not target.exists():
                return []
            return [f.name for f in target.iterdir()]

        def get_file(self, remote_path, **kwargs):
            return str(self.root / remote_path.lstrip("/"))

        def make_directory(self, path):
            (self.root / path.lstrip("/")).mkdir(parents=True, exist_ok=True)

    mocker.patch("parsons.catalist.catalist.SFTP", side_effect=FakeSFTP)
    return FakeSFTP
