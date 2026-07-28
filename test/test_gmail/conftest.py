import json
from pathlib import Path

import pytest

from parsons import Gmail


@pytest.fixture
def assets() -> Path:
    """The directory of attachment fixtures (binaries + their base64 encodings)."""
    return Path(__file__).parent / "assets"


CREDENTIALS = {
    "installed": {
        "client_id": "someclientid.apps.googleusercontent.com",
        "project_id": "some-project-id-12345",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://www.googleapis.com/oauth2/v3/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "someclientsecret",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    }
}

TOKEN = {
    "access_token": "someaccesstoken",
    "client_id": "some-client-id.apps.googleusercontent.com",
    "client_secret": "someclientsecret",
    "refresh_token": "1/refreshrate",
    "token_expiry": "2030-02-20T23:28:09Z",
    "token_uri": "https://www.googleapis.com/oauth2/v3/token",
    "user_agent": None,
    "revoke_uri": "https://oauth2.googleapis.com/revoke",
    "id_token": None,
    "id_token_jwt": None,
    "token_response": {
        "access_token": "someaccesstoken",
        "expires_in": 3600000,
        "scope": "https://www.googleapis.com/auth/gmail.send",
        "token_type": "Bearer",
    },
    "scopes": ["https://www.googleapis.com/auth/gmail.send"],
    "token_info_uri": "https://oauth2.googleapis.com/tokeninfo",
    "invalid": False,
    "_class": "OAuth2Credentials",
    "_module": "oauth2client.client",
}


@pytest.fixture
def gmail(tmp_path) -> Gmail:
    """A Gmail connector built from throwaway credentials/token files.

    Construction makes no network call, so no mock is needed here.
    """
    credentials_file = tmp_path / "credentials.json"
    credentials_file.write_text(json.dumps(CREDENTIALS))
    token_file = tmp_path / "token.json"
    token_file.write_text(json.dumps(TOKEN))
    return Gmail(str(credentials_file), str(token_file))
