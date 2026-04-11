import mimetypes
import random
import string
from email import message_from_string
from email.message import Message
from io import BytesIO, StringIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from parsons import SMTP
from parsons.notifications.sendmail import EmptyListError


@pytest.fixture
def mock_conn(mocker: MockerFixture) -> MagicMock:
    mock_smtp_class = mocker.patch("parsons.notifications.smtp.smtplib.SMTP", autospec=True)
    mock_smtp_ssl_class = mocker.patch("parsons.notifications.smtp.smtplib.SMTP_SSL", autospec=True)

    conn = mock_smtp_class.return_value
    mock_smtp_ssl_class.return_value = conn

    conn.sendmail.return_value = None
    conn.ehlo.return_value = (250, b"ok")
    conn.starttls.return_value = (220, b"Ready to start TLS")
    conn.login.return_value = (235, b"Authentication successful")

    def get_msg() -> Message | None:
        if not conn.sendmail.called:
            return None
        args, kwargs = conn.sendmail.call_args
        msg_string = kwargs.get("msg") or args[2]
        return message_from_string(msg_string)

    def get_types() -> list[str]:
        msg = get_msg()
        if not msg:
            return []
        return [p.get_content_type() for p in msg.walk() if not p.is_multipart()]

    def get_attachments() -> dict[str, str]:
        msg = get_msg()
        return {p.get_filename(): p.get_content_type() for p in msg.walk() if p.get_filename()}

    conn.get_sent_msg = get_msg
    conn.get_sent_types = get_types
    conn.get_attachments = get_attachments

    return conn


@pytest.fixture
def smtp(mock_conn: MagicMock) -> SMTP:
    """Configure a Parsons SMTP instance with fake credentials."""
    return SMTP("fake.example.com", username="fake", password="fake")


def create_virtual_file(name: str, content: str = "data") -> StringIO:
    f = StringIO(content)
    f.name = name
    return f


@pytest.mark.usefixtures("mocker")
@pytest.mark.parametrize(
    ("html", "files", "expected_types"),
    [
        (None, None, ["text/plain"]),
        ("<p>HTML</p>", None, ["text/plain", "text/html"]),
        (None, ["test.csv"], ["text/plain", "text/csv"]),
        ("<p>HTML</p>", ["test.csv"], ["text/plain", "text/html", "text/csv"]),
        (
            None,
            ["1.csv", "2.csv"],
            ["text/plain", "text/csv", "text/csv"],
        ),
    ],
    ids=(
        "Simple Body",
        "Body + HTML",
        "Body + Attachment",
        "Body + HTML + Attachment",
        "Multiple Attachments",
    ),
)
def test_send_email_content(
    smtp: SMTP,
    mock_conn: MagicMock,
    html: str | None,
    files: list[str] | None,
    expected_types: list[str],
):
    files_with_data = (
        [
            create_virtual_file(
                f, content="".join(random.choices(string.ascii_letters + string.digits, k=8))
            )
            for f in files
        ]
        if files
        else None
    )

    smtp.send_email(
        "f@ex.com",
        "t@ex.com",
        "We've been trying to reach you...",
        "Your car's warranty is about to expire!",
        message_html=html,
        files=files_with_data,
    )

    msg = mock_conn.get_sent_msg()
    assert msg["Subject"] == "We've been trying to reach you..."
    assert msg["To"] == "t@ex.com"
    assert msg["From"] == "f@ex.com"
    sent_payloads = [p.get_payload(decode=True) for p in msg.walk() if not p.is_multipart()]
    assert b"Your car's warranty is about to expire!" in sent_payloads

    if html:
        assert html.encode() in sent_payloads

    if files_with_data:
        for content in files_with_data:
            assert content.getvalue().encode() in sent_payloads

    sent_types = mock_conn.get_sent_types()
    for t in expected_types:
        assert t in sent_types


def test_dynamic_mime_check(smtp: SMTP, mock_conn: MagicMock):
    filenames = ["report.pdf", "data.csv", "photo.jpg"]
    virtual_files = [create_virtual_file(f) for f in filenames]

    smtp.send_email("f@ex.com", "t@ex.com", "Sub", "Body", files=virtual_files)

    sent = mock_conn.get_attachments()
    for f in filenames:
        expected_type, _ = mimetypes.guess_type(f)
        assert sent[f] == expected_type


def test_binary_attachment_integrity(smtp: SMTP, mock_conn: MagicMock):
    gif_data = bytes([71, 73, 70, 56, 57, 97, 1, 0, 1, 0])
    gif_file = BytesIO(gif_data)
    gif_file.name = "tiny.gif"

    smtp.send_email("f@ex.com", "t@ex.com", "Sub", "Body", files=[gif_file])

    msg = mock_conn.get_sent_msg()
    gif_part = next(p for p in msg.walk() if p.get_filename() == "tiny.gif")

    assert gif_part.get_content_type() == "image/gif"
    assert gif_part.get_payload(decode=True) == gif_data


def test_attachment_disposition(smtp: SMTP, mock_conn: MagicMock):
    named_file = StringIO("content")
    named_file.name = "report.pdf"

    smtp.send_email("f@ex.com", "t@ex.com", "Sub", "Body", files=[named_file])

    msg = mock_conn.get_sent_msg()
    file_part = next(p for p in msg.walk() if p.get_filename() == "report.pdf")
    assert "attachment" in file_part.get("Content-Disposition")


def test_connection_authentication_flow(mock_conn: MagicMock):
    host, user, pwd = "smtp.custom.com", "user123", "secret_pass"
    smtp_inst = SMTP(host=host, username=user, password=pwd, port=587, tls=True)
    smtp_inst.send_email("f@ex.com", "t@ex.com", "Sub", "Body")

    assert mock_conn.ehlo.called
    assert mock_conn.starttls.call_count == 1

    mock_conn.login.assert_called_once_with(user, pwd)


def test_send_email_files_as_single_string(smtp: SMTP, mock_conn: MagicMock, tmp_path: Path):
    file_path = tmp_path / "single_report.pdf"
    file_path.write_bytes(b"fake pdf content")

    smtp.send_email("s@ex.com", "t@ex.com", "Sub", "Body", files=str(file_path))

    sent_attachments = mock_conn.get_attachments()
    assert "single_report.pdf" in sent_attachments


def test_send_email_empty_recipient_list(smtp: SMTP):
    with pytest.raises(EmptyListError, match="Must contain at least 1 email."):
        smtp.send_email("sender@ex.com", [], "Sub", "Body")


@pytest.mark.parametrize(
    ("input_to", "expected_header"),
    [
        (["a@b.com", "c@d.com"], "a@b.com, c@d.com"),
        (['"Name" <a@b.com>', "c@d.com"], '"Name" <a@b.com>, c@d.com'),
    ],
)
def test_recipient_string_joining(
    smtp: SMTP, mock_conn: MagicMock, input_to: list[str], expected_header: str
):
    smtp.send_email("f@ex.com", input_to, "Sub", "Body")

    msg = mock_conn.get_sent_msg()
    assert msg["To"] == expected_header


@pytest.mark.parametrize(("close_manually", "expected_quit_count"), [(True, 0), (False, 1)])
def test_connection_closing_logic(
    mock_conn: MagicMock, close_manually: bool, expected_quit_count: int
) -> None:
    smtp_inst = SMTP(
        "fake.example.com", username="fake", password="fake", close_manually=close_manually
    )

    smtp_inst.send_email("a@b.com", "c@d.com", "Sub", "Body")

    assert mock_conn.quit.call_count == expected_quit_count


def test_send_message_error_handling(smtp: SMTP, mock_conn: MagicMock) -> None:
    """Ensure partial failures are returned correctly."""
    fail_response = {"bad@ex.com": (550, "User unknown")}
    mock_conn.sendmail.return_value = fail_response

    simple_msg = smtp._create_message_simple("f@ex.com", "bad@ex.com", "Sub", "Body")
    result = smtp._send_message(simple_msg)

    assert result == fail_response
