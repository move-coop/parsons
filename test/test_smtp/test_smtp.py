"""Tests for the SMTP connector.

Reference example of the protocol testing pattern (see docs/contrib_docs/write_tests.rst):
pytest-native functions with a fake connection class (fakes.py) injected via a
fixture, in place of mocking a stateful protocol method by method.
"""

import base64
import io
import re

from parsons import SMTP
from test.test_smtp.fakes import FakeSMTPConnection


def test_send_message_simple(smtp, conn):
    smtp.send_email("foo@example.com", "recipient1@example.com", "Simple subject", "Fake body")

    assert conn.result[0] == "foo@example.com"
    assert conn.result[1] == ["recipient1@example.com"]
    assert conn.result[2].endswith(
        "\nto: recipient1@example.com\nfrom: foo@example.com\nsubject: Simple subject\n\nFake body"
    )
    assert conn.quit_ran


def test_send_message_html(smtp, conn):
    smtp.send_email(
        "foohtml@example.com",
        "recipienthtml@example.com",
        "Simple subject",
        "Fake body",
        "<p>Really Fake html</p>",
    )

    assert conn.result[0] == "foohtml@example.com"
    assert conn.result[1] == ["recipienthtml@example.com"]
    assert re.search(r"<p>Really Fake html</p>\n--=======", conn.result[2])
    assert re.search(r"\nFake body\n--======", conn.result[2])
    assert re.search(r"ubject: Simple subject\n", conn.result[2])
    assert conn.quit_ran


def test_send_message_manualclose():
    conn = FakeSMTPConnection()
    smtp = SMTP("fake.example.com", username="fake", password="fake", close_manually=True)
    smtp.conn = conn

    smtp.send_email("foo@example.com", "recipient1@example.com", "Simple subject", "Fake body")

    assert not conn.quit_ran


def test_send_message_files(smtp, conn):
    named_file_content = "x,y,z\n1,2,3\r\n3,4,5\r\n"
    unnamed_file_content = "foo,bar\n1,2\r\n3,4\r\n"
    bytes_file_content = bytes(
        [71, 73, 70, 56, 57, 97, 1, 0, 1, 0, 0, 255, 0, 44, 0, 0, 0, 0, 1, 0, 1, 0, 0, 2, 0, 59]
    )
    named_file = io.StringIO(named_file_content)
    named_file.name = "xyz.csv"

    bytes_file = io.BytesIO(bytes_file_content)
    bytes_file.name = "xyz.gif"

    smtp.send_email(
        "foofiles@example.com",
        "recipientfiles@example.com",
        "Simple subject",
        "Fake body",
        files=[io.StringIO(unnamed_file_content), named_file, bytes_file],
    )

    assert conn.result[0] == "foofiles@example.com"
    assert conn.result[1] == ["recipientfiles@example.com"]
    assert re.search(r"\nFake body\n--======", conn.result[2])

    found = re.findall(r'filename="file"\n\n([\w=/]+)\n\n--===', conn.result[2])
    assert base64.b64decode(found[0]).decode() == unnamed_file_content

    found_named = re.findall(
        r'Content-Type: text/csv; charset="utf-8"\nMIME-Version: 1.0'
        r"\nContent-Transfer-Encoding: base64\nContent-Disposition: "
        r'attachment; filename="xyz.csv"\n\n([\w=/]+)\n\n--======',
        conn.result[2],
    )
    assert base64.b64decode(found_named[0]).decode() == named_file_content

    found_gif = re.findall(
        r"Content-Type: image/gif\nMIME-Version: 1.0"
        r"\nContent-Transfer-Encoding: base64\nContent-ID: <xyz.gif>"
        r'\nContent-Disposition: attachment; filename="xyz.gif"\n\n([\w=/]+)\n\n--==',
        conn.result[2],
    )
    assert base64.b64decode(found_gif[0]) == bytes_file_content
    assert conn.quit_ran


def test_send_message_partial_fail(smtp):
    simple_msg = smtp._create_message_simple(
        "foo@example.com",
        "recipient1@example.com, willfail@example.com",
        "Simple subject",
        "Fake body",
    )

    send_result = smtp._send_message(simple_msg)

    assert send_result == {"willfail@example.com": (550, "User unknown")}
