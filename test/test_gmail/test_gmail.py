"""Tests for the Gmail connector.

These exercise MIME message construction (``_create_message_*`` /
``_encode_raw_message``), which is pure/local — no network is involved.
"""

import base64
import email
import os
from pathlib import Path

import pytest
from email_validator import EmailSyntaxError

SENDER = "Sender <sender@email.com>"
TO = "Recepient <recepient@email.com>"
MESSAGE_TEXT = "The is the message text of the email with attachments"
MESSAGE_HTML = "<p>This is the html message part of the email with attachments</p>"

MULTIPART_HEADER = ("Content-Type", "multipart/alternative;\n boundary=")


def decode_raw(gmail, msg) -> email.message.Message:
    """Encode a message the way the connector does, then decode it back for inspection."""
    raw = gmail._encode_raw_message(msg)
    return email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))


def normalize_multipart_boundary(items: list) -> list:
    """The multipart boundary is random; collapse it to a stable prefix for comparison."""
    return [
        MULTIPART_HEADER
        if key == "Content-Type" and "multipart/alternative;\n boundary=" in value
        else (key, value)
        for key, value in items
    ]


def test_create_message_simple(gmail):
    subject = "This is a test email"
    message_text = "The is the message text of the email"

    decoded = decode_raw(gmail, gmail._create_message_simple(SENDER, TO, subject, message_text))

    assert decoded.items() == [
        ("Content-Type", 'text/plain; charset="us-ascii"'),
        ("MIME-Version", "1.0"),
        ("Content-Transfer-Encoding", "7bit"),
        ("to", TO),
        ("from", SENDER),
        ("subject", subject),
    ]
    assert decoded.get_payload() == message_text
    assert sum(1 for _ in decoded.walk()) == 1


def test_create_message_html(gmail):
    subject = "This is a test html email"
    message_text = "The is the message text of the email"
    message_html = "<p>This is the html message part of the email</p>"

    decoded = decode_raw(
        gmail, gmail._create_message_html(SENDER, TO, subject, message_text, message_html)
    )

    assert normalize_multipart_boundary(decoded.items()) == [
        MULTIPART_HEADER,
        ("MIME-Version", "1.0"),
        ("subject", subject),
        ("from", SENDER),
        ("to", TO),
    ]
    parts = decoded.get_payload()
    assert parts[0].get_payload() == message_text
    assert parts[1].get_payload() == message_html
    assert sum(1 for _ in decoded.walk()) == 3


def test_create_message_html_no_text(gmail):
    subject = "This is a test html email"
    message_html = "<p>This is the html message part of the email</p>"

    decoded = decode_raw(gmail, gmail._create_message_html(SENDER, TO, subject, "", message_html))

    assert normalize_multipart_boundary(decoded.items()) == [
        MULTIPART_HEADER,
        ("MIME-Version", "1.0"),
        ("subject", subject),
        ("from", SENDER),
        ("to", TO),
    ]
    assert sum(1 for _ in decoded.walk()) == 2


# (filename, base64 fixture stem, (accessor, expected), has Content-ID)
ATTACHMENT_CASES = [
    ("loremipsum.jpeg", "loremipsum_b64_jpeg", ("get_content_type", "image/jpeg"), True),
    ("loremipsum.m4a", "loremipsum_b64_m4a", ("get_content_maintype", "audio"), False),
    ("loremipsum.mp3", "loremipsum_b64_mp3", ("get_content_type", "audio/mpeg"), False),
    ("loremipsum.mp4", "loremipsum_b64_mp4", ("get_content_type", "video/mp4"), False),
    ("loremipsum.pdf", "loremipsum_b64_pdf", ("get_content_type", "application/pdf"), False),
]


def _attachment_message(gmail, attachment_path):
    subject = "This is a test email with attachements"
    msg = gmail._create_message_attachments(
        SENDER, TO, subject, MESSAGE_TEXT, [str(attachment_path)], message_html=MESSAGE_HTML
    )
    decoded = decode_raw(gmail, msg)

    assert normalize_multipart_boundary(decoded.items()) == [
        MULTIPART_HEADER,
        ("MIME-Version", "1.0"),
        ("to", TO),
        ("from", SENDER),
        ("subject", subject),
    ]
    parts = decoded.get_payload()
    assert parts[0].get_payload() == MESSAGE_TEXT
    assert parts[1].get_payload() == MESSAGE_HTML
    assert sum(1 for _ in decoded.walk()) == 4
    return parts


def test_create_message_attachments_text(gmail, assets):
    parts = _attachment_message(gmail, assets / "loremipsum.txt")

    b64_name = "loremipsum_b64_win_txt" if os.linesep == "\r\n" else "loremipsum_b64_txt"
    assert parts[2].get_payload() == (assets / f"{b64_name}.txt").read_text()
    assert parts[2].get_content_type() == "text/plain"


@pytest.mark.parametrize(
    ("filename", "b64_stem", "content_check", "has_content_id"),
    ATTACHMENT_CASES,
    ids=[c[0] for c in ATTACHMENT_CASES],
)
def test_create_message_attachments(
    gmail, assets, filename, b64_stem, content_check, has_content_id
):
    parts = _attachment_message(gmail, assets / filename)

    assert parts[2].get_payload() == (assets / f"{b64_stem}.txt").read_text()

    accessor, expected = content_check
    assert getattr(parts[2], accessor)() == expected

    if has_content_id:
        assert parts[2].get("Content-ID") == f"<{Path(filename).name}>"


def test_validate_email_string(gmail):
    cases = [
        ("Sender <sender@email.com>", True),
        ("sender@email.com", True),
        ("<sender@email.com>", True),
        ("Sender sender@email.com", False),
        ("Sender <sender2email.com>", False),
        # email_validator rejects comma domains consistently across Python versions.
        ("Sender <sender@email,com>", False),
        ("Sender <sender+alias@email,com>", False),
    ]

    for value, valid in cases:
        if valid:
            assert gmail._validate_email_string(value)
        else:
            with pytest.raises(EmailSyntaxError):
                gmail._validate_email_string(value)
