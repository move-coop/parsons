import base64
import email
import json
import os
from pathlib import Path

import pytest

from parsons import Gmail

_dir = Path(__file__).parent


@pytest.fixture
def gmail_client(tmp_path: Path) -> Gmail:
    """Set up temporary credentials and return a configured Gmail client with mocked network requests."""
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


def test_create_message_simple(gmail_client: Gmail):
    sender = "Sender <sender@email.com>"
    to = "Recepient <recepient@email.com>"
    subject = "This is a test email"
    message_text = "The is the message text of the email"

    msg = gmail_client._create_message_simple(sender, to, subject, message_text)
    raw = gmail_client._encode_raw_message(msg)

    decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

    expected_items = [
        ("Content-Type", 'text/plain; charset="us-ascii"'),
        ("MIME-Version", "1.0"),
        ("Content-Transfer-Encoding", "7bit"),
        ("to", to),
        ("from", sender),
        ("subject", subject),
    ]

    assert decoded.items() == expected_items

    expected_parts = 1
    assert sum(1 for _ in decoded.walk()) == expected_parts

    assert decoded.get_payload() == message_text


def test_create_message_html(gmail_client: Gmail):
    sender = "Sender <sender@email.com>"
    to = "Recepient <recepient@email.com>"
    subject = "This is a test html email"
    message_text = "The is the message text of the email"
    message_html = "<p>This is the html message part of the email</p>"

    msg = gmail_client._create_message_html(sender, to, subject, message_text, message_html)
    raw = gmail_client._encode_raw_message(msg)

    decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

    expected_items = [
        ("Content-Type", "multipart/alternative;\n boundary="),
        ("MIME-Version", "1.0"),
        ("subject", subject),
        ("from", sender),
        ("to", to),
    ]

    updated_items = []
    for key, value in decoded.items():
        if "Content-Type" in key and "multipart/alternative;\n boundary=" in value:
            updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
        else:
            updated_items.append((key, value))

    assert updated_items == expected_items

    expected_parts = 3
    assert sum(1 for _ in decoded.walk()) == expected_parts

    parts = decoded.get_payload()
    assert parts[0].get_payload() == message_text
    assert parts[1].get_payload() == message_html


def test_create_message_html_no_text(gmail_client: Gmail):
    sender = "Sender <sender@email.com>"
    to = "Recepient <recepient@email.com>"
    subject = "This is a test html email"
    message_html = "<p>This is the html message part of the email</p>"

    msg = gmail_client._create_message_html(sender, to, subject, "", message_html)
    raw = gmail_client._encode_raw_message(msg)

    decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

    expected_items = [
        ("Content-Type", "multipart/alternative;\n boundary="),
        ("MIME-Version", "1.0"),
        ("subject", subject),
        ("from", sender),
        ("to", to),
    ]

    updated_items = []
    for key, value in decoded.items():
        if "Content-Type" in key and "multipart/alternative;\n boundary=" in value:
            updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
        else:
            updated_items.append((key, value))

    assert updated_items == expected_items

    expected_parts = 2
    assert sum(1 for _ in decoded.walk()) == expected_parts

    parts = decoded.get_payload()
    assert parts[0].get_payload() == message_html


def test_create_message_attachments(gmail_client: Gmail):
    sender = "Sender <sender@email.com>"
    to = "Recepient <recepient@email.com>"
    subject = "This is a test email with attachements"
    message_text = "The is the message text of the email with attachments"
    message_html = "<p>This is the html message part of the email with attachments</p>"
    attachments = [str(_dir / "assets/loremipsum.txt")]

    msg = gmail_client._create_message_attachments(
        sender, to, subject, message_text, attachments, message_html=message_html
    )
    raw = gmail_client._encode_raw_message(msg)

    decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

    expected_items = [
        ("Content-Type", "multipart/alternative;\n boundary="),
        ("MIME-Version", "1.0"),
        ("to", to),
        ("from", sender),
        ("subject", subject),
    ]

    updated_items = []
    for key, value in decoded.items():
        if "Content-Type" in key and "multipart/alternative;\n boundary=" in value:
            updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
        else:
            updated_items.append((key, value))

    assert updated_items == expected_items

    expected_parts = 4
    assert sum(1 for _ in decoded.walk()) == expected_parts

    parts = decoded.get_payload()
    assert parts[0].get_payload() == message_text
    assert parts[1].get_payload() == message_html

    if os.linesep == "\r\n":
        file = _dir / "assets/loremipsum_b64_win_txt.txt"
    else:
        file = _dir / "assets/loremipsum_b64_txt.txt"

    assert parts[2].get_content_type() == "text/plain"
    assert parts[2].get_payload() == file.read_text()


def test_create_message_attachments_jpeg(gmail_client: Gmail):
    sender = "Sender <sender@email.com>"
    to = "Recepient <recepient@email.com>"
    subject = "This is a test email with attachements"
    message_text = "The is the message text of the email with attachments"
    message_html = "<p>This is the html message part of the email with attachments</p>"
    attachments = [str(_dir / "assets/loremipsum.jpeg")]

    msg = gmail_client._create_message_attachments(
        sender, to, subject, message_text, attachments, message_html=message_html
    )
    raw = gmail_client._encode_raw_message(msg)

    decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

    expected_items = [
        ("Content-Type", "multipart/alternative;\n boundary="),
        ("MIME-Version", "1.0"),
        ("to", to),
        ("from", sender),
        ("subject", subject),
    ]

    updated_items = []
    for key, value in decoded.items():
        if "Content-Type" in key and "multipart/alternative;\n boundary=" in value:
            updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
        else:
            updated_items.append((key, value))

    assert updated_items == expected_items

    expected_parts = 4
    assert sum(1 for _ in decoded.walk()) == expected_parts

    parts = decoded.get_payload()
    assert parts[0].get_payload() == message_text
    assert parts[1].get_payload() == message_html
    assert parts[2].get_content_maintype() == "image"
    assert parts[2].get_payload() == (_dir / "assets/loremipsum_b64_jpeg.txt").read_text()


def test_create_message_attachments_m4a(gmail_client: Gmail):
    sender = "Sender <sender@email.com>"
    to = "Recepient <recepient@email.com>"
    subject = "This is a test email with attachements"
    message_text = "The is the message text of the email with attachments"
    message_html = "<p>This is the html message part of the email with attachments</p>"
    attachments = [str(_dir / "assets/loremipsum.m4a")]

    msg = gmail_client._create_message_attachments(
        sender, to, subject, message_text, attachments, message_html=message_html
    )
    raw = gmail_client._encode_raw_message(msg)

    decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

    expected_items = [
        ("Content-Type", "multipart/alternative;\n boundary="),
        ("MIME-Version", "1.0"),
        ("to", to),
        ("from", sender),
        ("subject", subject),
    ]

    updated_items = []
    for key, value in decoded.items():
        if "Content-Type" in key and "multipart/alternative;\n boundary=" in value:
            updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
        else:
            updated_items.append((key, value))

    assert updated_items == expected_items

    expected_parts = 4
    assert sum(1 for _ in decoded.walk()) == expected_parts

    parts = decoded.get_payload()
    assert parts[0].get_payload() == message_text
    assert parts[1].get_payload() == message_html
    assert parts[2].get_content_maintype() == "audio"
    assert parts[2].get_payload() == (_dir / "assets/loremipsum_b64_m4a.txt").read_text()


def test_create_message_attachments_mp3(gmail_client: Gmail):
    sender = "Sender <sender@email.com>"
    to = "Recepient <recepient@email.com>"
    subject = "This is a test email with attachements"
    message_text = "The is the message text of the email with attachments"
    message_html = "<p>This is the html message part of the email with attachments</p>"
    attachments = [str(_dir / "assets/loremipsum.mp3")]

    msg = gmail_client._create_message_attachments(
        sender, to, subject, message_text, attachments, message_html=message_html
    )
    raw = gmail_client._encode_raw_message(msg)

    decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

    expected_items = [
        ("Content-Type", "multipart/alternative;\n boundary="),
        ("MIME-Version", "1.0"),
        ("to", to),
        ("from", sender),
        ("subject", subject),
    ]

    updated_items = []
    for key, value in decoded.items():
        if "Content-Type" in key and "multipart/alternative;\n boundary=" in value:
            updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
        else:
            updated_items.append((key, value))

    assert updated_items == expected_items

    expected_parts = 4
    assert sum(1 for _ in decoded.walk()) == expected_parts

    parts = decoded.get_payload()
    assert parts[0].get_payload() == message_text
    assert parts[1].get_payload() == message_html
    assert parts[2].get_content_type() == "audio/mpeg"
    assert parts[2].get_payload() == (_dir / "assets/loremipsum_b64_mp3.txt").read_text()


def test_create_message_attachments_mp4(gmail_client: Gmail):
    sender = "Sender <sender@email.com>"
    to = "Recepient <recepient@email.com>"
    subject = "This is a test email with attachements"
    message_text = "The is the message text of the email with attachments"
    message_html = "<p>This is the html message part of the email with attachments</p>"
    attachments = [str(_dir / "assets/loremipsum.mp4")]

    msg = gmail_client._create_message_attachments(
        sender, to, subject, message_text, attachments, message_html=message_html
    )
    raw = gmail_client._encode_raw_message(msg)

    decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

    expected_items = [
        ("Content-Type", "multipart/alternative;\n boundary="),
        ("MIME-Version", "1.0"),
        ("to", to),
        ("from", sender),
        ("subject", subject),
    ]

    updated_items = []
    for key, value in decoded.items():
        if "Content-Type" in key and "multipart/alternative;\n boundary=" in value:
            updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
        else:
            updated_items.append((key, value))

    assert updated_items == expected_items

    expected_parts = 4
    assert sum(1 for _ in decoded.walk()) == expected_parts

    parts = decoded.get_payload()
    assert parts[0].get_payload() == message_text
    assert parts[1].get_payload() == message_html
    assert parts[2].get_content_type() == "video/mp4"
    assert parts[2].get_payload() == (_dir / "assets/loremipsum_b64_mp4.txt").read_text()


def test_create_message_attachments_pdf(gmail_client: Gmail):
    sender = "Sender <sender@email.com>"
    to = "Recepient <recepient@email.com>"
    subject = "This is a test email with attachements"
    message_text = "The is the message text of the email with attachments"
    message_html = "<p>This is the html message part of the email with attachments</p>"
    attachments = [str(_dir / "assets/loremipsum.pdf")]

    msg = gmail_client._create_message_attachments(
        sender, to, subject, message_text, attachments, message_html=message_html
    )

    raw = gmail_client._encode_raw_message(msg)

    decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

    expected_items = [
        ("Content-Type", "multipart/alternative;\n boundary="),
        ("MIME-Version", "1.0"),
        ("to", to),
        ("from", sender),
        ("subject", subject),
    ]

    updated_items = []
    for key, value in decoded.items():
        if "Content-Type" in key and "multipart/alternative;\n boundary=" in value:
            updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
        else:
            updated_items.append((key, value))

    assert updated_items == expected_items

    expected_parts = 4
    assert sum(1 for _ in decoded.walk()) == expected_parts

    parts = decoded.get_payload()
    assert parts[0].get_payload() == message_text
    assert parts[1].get_payload() == message_html
    assert parts[2].get_content_type() == "application/pdf"
    assert parts[2].get_payload() == (_dir / "assets/loremipsum_b64_pdf.txt").read_text()


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
