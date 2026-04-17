import mimetypes
import os
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


@pytest.mark.parametrize("infer_port", [True, False])
@pytest.mark.parametrize("init_mode", ["args", "env"])
@pytest.mark.parametrize(
    ("tls", "ssl", "starttls_calls", "inferrable_port"),
    [
        (False, None, 0, 25),
        (None, None, 1, 587),
        (None, False, 1, 587),
        (True, None, 1, 587),
        (True, False, 1, 587),
        (False, True, 0, 465),
        (None, True, 0, 465),
        (True, True, 0, 465),
    ],
    ids=[
        "plain-text",
        "implicit-tls",
        "implicit-tls-explicit-not-ssl",
        "explicit-tls",
        "explicit-tls-explicit-not-ssl",
        "explicit-ssl-explicit-not-tls",
        "explicit-ssl-overrides-implicit-tls",
        "explicit-ssl-overrides-explicit-tls",
    ],
)
def test_connection_authentication_flow(
    mock_conn: MagicMock,
    mocker: MockerFixture,
    infer_port: bool,
    init_mode: str,
    tls: bool,
    ssl: bool,
    starttls_calls: int,
    inferrable_port: int,
):
    data = {
        "host": "smtp.custom.com",
        "user": "user123",
        "pass": "secret_pass",
        "port": None if infer_port else 587,
    }

    if init_mode == "args":
        smtp_inst = SMTP(
            host=data["host"],
            username=data["user"],
            password=data["pass"],
            port=data["port"],
            tls=tls,
            ssl=ssl,
        )
    else:
        env_vars = {
            "SMTP_HOST": data["host"],
            "SMTP_USER": data["user"],
            "SMTP_PASSWORD": data["pass"],
            "SMTP_TLS": str(tls) if tls is not None else "",
            "SMTP_SSL": str(ssl) if ssl is not None else "",
        }
        if not infer_port:
            env_vars["SMTP_PORT"] = str(data["port"])

        mocker.patch.dict(os.environ, env_vars)
        smtp_inst = SMTP()

    smtp_inst.send_email("f@ex.com", "t@ex.com", "Sub", "Body")

    implicit_tls = tls is None
    implicit_not_ssl = ssl is None
    tls_disabled = ssl is not True

    assert smtp_inst.host == data["host"]
    assert smtp_inst.port == data["port"] if not infer_port else inferrable_port

    assert smtp_inst.tls in (tls, implicit_tls, tls_disabled), (
        f"TLS Status: {smtp_inst.tls}; TLS Parameter: {tls}; TLS Implicitly Enabled: {implicit_tls}"
    )
    assert smtp_inst.ssl in (ssl, not implicit_not_ssl), (
        f"SSL Status: {smtp_inst.ssl}; SSL Parameter: {ssl}; SSL Implicitly Disabled: {implicit_not_ssl}"
    )
    if smtp_inst.ssl is True:
        assert smtp_inst.tls is False

    mock_conn.login.assert_called_once_with(data["user"], data["pass"])
    assert mock_conn.starttls.call_count == starttls_calls


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
