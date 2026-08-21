import json
from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def bq_creds(tmp_path, monkeypatch):
    """A fake Google credential file plus GOOGLE_APPLICATION_CREDENTIALS env var.

    Mirrors the old FakeCredentialTest base the suite inherited from. Autouse so every
    test runs with credentials available; the credential-specific tests request it by
    name to read ``cred_path`` / ``cred_contents``.
    """
    cred_path = tmp_path / "mycred.json"
    cred_contents = {
        "client_id": "foobar.apps.googleusercontent.com",
        "client_secret": str(hash("foobar")),
        "quota_project_id": "project-id",
        "refresh_token": str(hash("foobarfoobar")),
        "type": "authorized_user",
    }
    cred_path.write_text(json.dumps(cred_contents))
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(cred_path))
    return SimpleNamespace(cred_path=str(cred_path), cred_contents=cred_contents)
