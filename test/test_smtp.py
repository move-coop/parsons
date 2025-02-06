from parsons import SMTP
import base64
import io
import re
import unittest


class FakeConnection(object):
    def __init__(self, result_obj):
        self.result_obj = result_obj

    def sendmail(self, sender, to, message_body):
        self.result_obj.result = (sender, to, message_body)
        if "willfail@example.com" in to:
            return {"willfail@example.com": (550, "User unknown")}

    def quit(self):
        self.result_obj.quit_ran = True


class TestSMTP(unittest.TestCase):
    def setUp(self):
        self.smtp = SMTP("fake.example.com", username="fake", password="fake")
        self.smtp.conn = FakeConnection(self)
        self.result = None
        self.quit_ran = False

    def test_send_message_simple(self):
        self.smtp.send_email(
            "foo@example.com", "recipient1@example.com", "Simple subject", "Fake body"
        )
        self.assertEqual(self.result[0], "foo@example.com")
        self.assertEqual(self.result[1], ["recipient1@example.com"])
        self.assertTrue(
            self.result[2].endswith(
                "\nto: recipient1@example.com\nfrom: foo@example.com"
                "\nsubject: Simple subject\n\nFake body"
            )
        )
        self.assertTrue(self.quit_ran)

    def test_send_message_html(self):
        self.smtp.send_email(
            "foohtml@example.com",
            "recipienthtml@example.com",
            "Simple subject",
            "Fake body",
            "<p>Really Fake html</p>",
        )
        self.assertEqual(self.result[0], "foohtml@example.com")
        self.assertEqual(self.result[1], ["recipienthtml@example.com"])
        self.assertRegex(self.result[2], r"<p>Really Fake html</p>\n--=======")
        self.assertRegex(self.result[2], r"\nFake body\n--======")
        self.assertRegex(self.result[2], r"ubject: Simple subject\n")
        self.assertTrue(self.quit_ran)

    def test_send_message_manualclose(self):
        smtp = SMTP("fake.example.com", username="fake", password="fake", close_manually=True)
        smtp.conn = FakeConnection(self)
        smtp.send_email("foo@example.com", "recipient1@example.com", "Simple subject", "Fake body")
        self.assertFalse(self.quit_ran)

    def test_send_message_files(self):
        named_file_content = "x,y,z\n1,2,3\r\n3,4,5\r\n"
        unnamed_file_content = "foo,bar\n1,2\r\n3,4\r\n"
        bytes_file_content = bytes(
            [
                71,
                73,
                70,
                56,
                57,
                97,
                1,
                0,
                1,
                0,
                0,
                255,
                0,
                44,
                0,
                0,
                0,
                0,
                1,
                0,
                1,
                0,
                0,
                2,
                0,
                59,
            ]
        )
        named_file = io.StringIO(named_file_content)
        named_file.name = "xyz.csv"

        bytes_file = io.BytesIO(bytes_file_content)
        bytes_file.name = "xyz.gif"

        self.smtp.send_email(
            "foofiles@example.com",
            "recipientfiles@example.com",
            "Simple subject",
            "Fake body",
            files=[io.StringIO(unnamed_file_content), named_file, bytes_file],
        )
        self.assertEqual(self.result[0], "foofiles@example.com")
        self.assertEqual(self.result[1], ["recipientfiles@example.com"])
        self.assertRegex(self.result[2], r"\nFake body\n--======")
        found = re.findall(r'filename="file"\n\n([\w=/]+)\n\n--===', self.result[2])
        self.assertEqual(base64.b64decode(found[0]).decode(), unnamed_file_content)
        found_named = re.findall(
            r'Content-Type: text/csv; charset="utf-8"\nMIME-Version: 1.0'
            r"\nContent-Transfer-Encoding: base64\nContent-Disposition: "
            r'attachment; filename="xyz.csv"\n\n([\w=/]+)\n\n--======',
            self.result[2],
        )
        self.assertEqual(base64.b64decode(found_named[0]).decode(), named_file_content)

        found_gif = re.findall(
            r"Content-Type: image/gif\nMIME-Version: 1.0"
            r"\nContent-Transfer-Encoding: base64\nContent-ID: <xyz.gif>"
            r'\nContent-Disposition: attachment; filename="xyz.gif"\n\n([\w=/]+)\n\n--==',
            self.result[2],
        )
        self.assertEqual(base64.b64decode(found_gif[0]), bytes_file_content)
        self.assertTrue(self.quit_ran)

    def test_send_message_partial_fail(self):
        simple_msg = self.smtp._create_message_simple(
            "foo@example.com",
            "recipient1@example.com, willfail@example.com",
            "Simple subject",
            "Fake body",
        )
        send_result = self.smtp._send_message(simple_msg)
        self.assertEqual(send_result, {"willfail@example.com": (550, "User unknown")})
