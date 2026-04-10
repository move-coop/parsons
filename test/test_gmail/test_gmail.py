import base64
import email
import json
import os
from email.message import Message
from email.mime.text import MIMEText
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from parsons import Gmail

_dir = Path(__file__).parent


@pytest.fixture
def gmail_client(tmp_path: Path) -> Gmail:
    """Set up temporary credentials and return a configured Gmail client."""
    credentials_file = tmp_path / "credentials.json"
    token_file = tmp_path / "token.json"

    credentials_file.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "someclientid.apps.googleusercontent.com",
                    "project_id": "some-project-id-12345",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://www.googleapis.com/oauth2/v3/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "someclientsecret",
                    "redirect_uris": [
                        "urn:ietf:wg:oauth:2.0:oob",
                        "http://localhost",
                    ],
                }
            }
        )
    )

    token_file.write_text(
        json.dumps(
            {
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
        )
    )

    return Gmail(str(credentials_file), str(token_file))


@pytest.fixture
def email_meta() -> dict[str, str]:
    return {
        "sender": "Sender <sender@email.com>",
        "to": "Recepient <recepient@email.com>",
        "subject": "Test Subject",
        "text": "The is the message text",
        "html": "<p>This is html</p>",
    }


def get_decoded_email(gmail_client: Gmail, msg_obj: MIMEText) -> Message:
    """Helper to decode the raw gmail message into an email object."""
    raw = gmail_client._encode_raw_message(msg_obj)
    return email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))


def get_normalized_items(decoded_msg) -> list[tuple[str]]:
    """Normalizes Content-Type boundaries for consistent assertion."""
    updated = []
    for key, value in decoded_msg.items():
        if "Content-Type" in key and "boundary=" in value:
            updated.append(("Content-Type", "multipart/alternative;\n boundary="))
        else:
            updated.append((key, value))
    return updated


def test_create_message_simple(gmail_client: Gmail, email_meta: dict[str, str]):
    msg = gmail_client._create_message_simple(
        email_meta["sender"], email_meta["to"], email_meta["subject"], email_meta["text"]
    )
    decoded = get_decoded_email(gmail_client, msg)

    assert decoded["to"] == email_meta["to"]
    assert decoded["subject"] == email_meta["subject"]
    assert decoded.get_payload() == email_meta["text"]


def test_create_message_html(gmail_client: Gmail, email_meta: dict[str, str]):
    msg = gmail_client._create_message_html(
        email_meta["sender"],
        email_meta["to"],
        email_meta["subject"],
        email_meta["text"],
        email_meta["html"],
    )
    decoded = get_decoded_email(gmail_client, msg)

    assert get_normalized_items(decoded)[0] == (
        "Content-Type",
        "multipart/alternative;\n boundary=",
    )
    parts = decoded.get_payload()
    assert parts[0].get_payload() == email_meta["text"]
    assert parts[1].get_payload() == email_meta["html"]


@pytest.mark.parametrize(
    ("ext", "expected_type", "b64_suffix"),
    [
        ("txt", "text/plain", "txt"),
        ("jpeg", "image/jpeg", "jpeg"),
        ("m4a", "audio/mp4", "m4a"),
        ("mp3", "audio/mpeg", "mp3"),
        ("mp4", "video/mp4", "mp4"),
        ("pdf", "application/pdf", "pdf"),
    ],
)
def test_create_message_attachments_all(
    gmail_client: Gmail, email_meta: dict[str, str], ext: str, expected_type: str, b64_suffix: str
):
    # Handle the specific logic for Windows line endings in the txt file
    if ext == "txt" and os.linesep == "\r\n":
        b64_suffix = "win_txt"

    attachment_path = _dir / f"assets/loremipsum.{ext}"
    b64_ref_path = _dir / f"assets/loremipsum_b64_{b64_suffix}.txt"

    msg = gmail_client._create_message_attachments(
        email_meta["sender"],
        email_meta["to"],
        email_meta["subject"],
        email_meta["text"],
        [str(attachment_path)],
        message_html=email_meta["html"],
    )

    decoded = get_decoded_email(gmail_client, msg)
    parts = decoded.get_payload()

    assert parts[0].get_payload() == email_meta["text"]
    assert parts[1].get_payload() == email_meta["html"]

    assert expected_type in parts[2].get_content_type()
    assert parts[2].get_payload() == b64_ref_path.read_text()


@pytest.mark.parametrize(
    ("email_str", "expected_valid"),
    [
        ("Sender <sender@email.com>", True),
        ("sender@email.com", True),
        ("<sender@email.com>", True),
        ("Sender sender@email.com", False),
        ("Sender <sender2email.com>", False),
        ("Sender <sender@email,com>", False),
        ("Sender <sender+alias@email,com>", False),
    ],
)
def test__validate_email_string(gmail_client: Gmail, email_str: str, expected_valid: bool):
    if expected_valid:
        assert gmail_client._validate_email_string(email_str)
    else:
        with pytest.raises(ValueError, match="Invalid email address"):
            gmail_client._validate_email_string(email_str)

# TODO test sending emails
