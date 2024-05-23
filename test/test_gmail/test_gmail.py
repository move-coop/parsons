from parsons import Gmail
import json
import os
import requests_mock
import unittest
import shutil
import base64
import email


_dir = os.path.dirname(__file__)


class TestGmail(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        self.tmp_folder = "tmp/"
        self.credentials_file = f"{self.tmp_folder}/credentials.json"
        self.token_file = f"{self.tmp_folder}/token.json"

        os.mkdir(self.tmp_folder)

        with open(self.credentials_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "installed": {
                            "client_id": "someclientid.apps.googleusercontent.com",
                            "project_id": "some-project-id-12345",
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://www.googleapis.com/oauth2/v3/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",  # noqa: E501
                            "client_secret": "someclientsecret",
                            "redirect_uris": [
                                "urn:ietf:wg:oauth:2.0:oob",
                                "http://localhost",
                            ],
                        }
                    }
                )
            )

        with open(self.token_file, "w") as f:
            f.write(
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

        self.gmail = Gmail(self.credentials_file, self.token_file)

    def tearDown(self):
        # Delete tmp folder and files
        shutil.rmtree(self.tmp_folder)

    def test_create_message_simple(self):
        sender = "Sender <sender@email.com>"
        to = "Recepient <recepient@email.com>"
        subject = "This is a test email"
        message_text = "The is the message text of the email"

        msg = self.gmail._create_message_simple(sender, to, subject, message_text)
        raw = self.gmail._encode_raw_message(msg)

        decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

        expected_items = [
            ("Content-Type", 'text/plain; charset="us-ascii"'),
            ("MIME-Version", "1.0"),
            ("Content-Transfer-Encoding", "7bit"),
            ("to", to),
            ("from", sender),
            ("subject", subject),
        ]

        # Check the metadata
        self.assertListEqual(decoded.items(), expected_items)

        # Check the message
        self.assertEqual(decoded.get_payload(), message_text)

        # Check the number of parts
        expected_parts = 1
        self.assertEqual(sum([1 for i in decoded.walk()]), expected_parts)

    def test_create_message_html(self):
        sender = "Sender <sender@email.com>"
        to = "Recepient <recepient@email.com>"
        subject = "This is a test html email"
        message_text = "The is the message text of the email"
        message_html = "<p>This is the html message part of the email</p>"

        msg = self.gmail._create_message_html(sender, to, subject, message_text, message_html)
        raw = self.gmail._encode_raw_message(msg)

        decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

        expected_items = [
            ("Content-Type", "multipart/alternative;\n boundary="),
            ("MIME-Version", "1.0"),
            ("subject", subject),
            ("from", sender),
            ("to", to),
        ]

        # The boundary id changes everytime. Replace it with the beginnig to
        # avoid failures
        updated_items = []
        for i in decoded.items():
            if "Content-Type" in i[0] and "multipart/alternative;\n boundary=" in i[1]:  # noqa
                updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
            else:
                updated_items.append((i[0], i[1]))

        # Check the metadata
        self.assertListEqual(updated_items, expected_items)

        # Check the message
        # The first part is just a container for the text and html parts
        parts = decoded.get_payload()

        self.assertEqual(parts[0].get_payload(), message_text)
        self.assertEqual(parts[1].get_payload(), message_html)

        # Check the number of parts
        expected_parts = 3
        self.assertEqual(sum([1 for i in decoded.walk()]), expected_parts)

    def test_create_message_html_no_text(self):
        sender = "Sender <sender@email.com>"
        to = "Recepient <recepient@email.com>"
        subject = "This is a test html email"
        message_html = "<p>This is the html message part of the email</p>"

        msg = self.gmail._create_message_html(sender, to, subject, "", message_html)
        raw = self.gmail._encode_raw_message(msg)

        decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

        expected_items = [
            ("Content-Type", "multipart/alternative;\n boundary="),
            ("MIME-Version", "1.0"),
            ("subject", subject),
            ("from", sender),
            ("to", to),
        ]

        # The boundary id changes everytime. Replace it with the beginnig to
        # avoid failures
        updated_items = []
        for i in decoded.items():
            if "Content-Type" in i[0] and "multipart/alternative;\n boundary=" in i[1]:  # noqa
                updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
            else:
                updated_items.append((i[0], i[1]))

        # Check the metadata
        self.assertListEqual(updated_items, expected_items)

        # Check the message
        # The first part is just a container for the text and html parts
        parts = decoded.get_payload()

        self.assertEqual(parts[0].get_payload(), message_html)

        # Check the number of parts
        expected_parts = 2
        self.assertEqual(sum([1 for i in decoded.walk()]), expected_parts)

    def test_create_message_attachments(self):
        sender = "Sender <sender@email.com>"
        to = "Recepient <recepient@email.com>"
        subject = "This is a test email with attachements"
        message_text = "The is the message text of the email with attachments"
        message_html = "<p>This is the html message part of the email " "with attachments</p>"
        attachments = [f"{_dir}/assets/loremipsum.txt"]

        msg = self.gmail._create_message_attachments(
            sender, to, subject, message_text, attachments, message_html=message_html
        )
        raw = self.gmail._encode_raw_message(msg)

        decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

        expected_items = [
            ("Content-Type", "multipart/alternative;\n boundary="),
            ("MIME-Version", "1.0"),
            ("to", to),
            ("from", sender),
            ("subject", subject),
        ]

        # The boundary id changes everytime. Replace it with the beginnig to
        # avoid failures
        updated_items = []
        for i in decoded.items():
            if "Content-Type" in i[0] and "multipart/alternative;\n boundary=" in i[1]:  # noqa
                updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
            else:
                updated_items.append((i[0], i[1]))

        # Check the metadata
        self.assertListEqual(updated_items, expected_items)

        # Check the message
        # The first part is just a container for the text and html parts
        parts = decoded.get_payload()

        self.assertEqual(parts[0].get_payload(), message_text)
        self.assertEqual(parts[1].get_payload(), message_html)

        if os.linesep == "\r\n":
            file = f"{_dir}/assets/loremipsum_b64_win_txt.txt"
        else:
            file = f"{_dir}/assets/loremipsum_b64_txt.txt"

        with open(file, "r") as f:
            b64_txt = f.read()
        self.assertEqual(parts[2].get_payload(), b64_txt)

        self.assertEqual(parts[2].get_content_type(), "text/plain")

        # Check the number of parts
        expected_parts = 4
        self.assertEqual(sum([1 for i in decoded.walk()]), expected_parts)

    def test_create_message_attachments_jpeg(self):
        sender = "Sender <sender@email.com>"
        to = "Recepient <recepient@email.com>"
        subject = "This is a test email with attachements"
        message_text = "The is the message text of the email with attachments"
        message_html = "<p>This is the html message part of the email " "with attachments</p>"
        attachments = [f"{_dir}/assets/loremipsum.jpeg"]

        msg = self.gmail._create_message_attachments(
            sender, to, subject, message_text, attachments, message_html=message_html
        )
        raw = self.gmail._encode_raw_message(msg)

        decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

        expected_items = [
            ("Content-Type", "multipart/alternative;\n boundary="),
            ("MIME-Version", "1.0"),
            ("to", to),
            ("from", sender),
            ("subject", subject),
        ]

        # The boundary id changes everytime. Replace it with the beginnig to
        # avoid failures
        updated_items = []
        for i in decoded.items():
            if "Content-Type" in i[0] and "multipart/alternative;\n boundary=" in i[1]:  # noqa
                updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
            else:
                updated_items.append((i[0], i[1]))

        # Check the metadata
        self.assertListEqual(updated_items, expected_items)

        # Check the message
        # The first part is just a container for the text and html parts
        parts = decoded.get_payload()

        self.assertEqual(parts[0].get_payload(), message_text)
        self.assertEqual(parts[1].get_payload(), message_html)

        with open(f"{_dir}/assets/loremipsum_b64_jpeg.txt", "r") as f:
            b64_txt = f.read()
        self.assertEqual(parts[2].get_payload(), b64_txt)

        expected_id = f"<{attachments[0].split('/')[-1]}>"
        self.assertEqual(parts[2].get("Content-ID"), expected_id)
        self.assertEqual(parts[2].get_content_type(), "image/jpeg")

        # Check the number of parts
        expected_parts = 4
        self.assertEqual(sum([1 for i in decoded.walk()]), expected_parts)

    def test_create_message_attachments_m4a(self):
        sender = "Sender <sender@email.com>"
        to = "Recepient <recepient@email.com>"
        subject = "This is a test email with attachements"
        message_text = "The is the message text of the email with attachments"
        message_html = "<p>This is the html message part of the email " "with attachments</p>"
        attachments = [f"{_dir}/assets/loremipsum.m4a"]

        msg = self.gmail._create_message_attachments(
            sender, to, subject, message_text, attachments, message_html=message_html
        )
        raw = self.gmail._encode_raw_message(msg)

        decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

        expected_items = [
            ("Content-Type", "multipart/alternative;\n boundary="),
            ("MIME-Version", "1.0"),
            ("to", to),
            ("from", sender),
            ("subject", subject),
        ]

        # The boundary id changes everytime. Replace it with the beginnig to
        # avoid failures
        updated_items = []
        for i in decoded.items():
            if "Content-Type" in i[0] and "multipart/alternative;\n boundary=" in i[1]:  # noqa
                updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
            else:
                updated_items.append((i[0], i[1]))

        # Check the metadata
        self.assertListEqual(updated_items, expected_items)

        # Check the message
        # The first part is just a container for the text and html parts
        parts = decoded.get_payload()

        self.assertEqual(parts[0].get_payload(), message_text)
        self.assertEqual(parts[1].get_payload(), message_html)

        with open(f"{_dir}/assets/loremipsum_b64_m4a.txt", "r") as f:
            b64_txt = f.read()
        self.assertEqual(parts[2].get_payload(), b64_txt)

        self.assertEqual(parts[2].get_content_maintype(), "audio")

        # Check the number of parts
        expected_parts = 4
        self.assertEqual(sum([1 for i in decoded.walk()]), expected_parts)

    def test_create_message_attachments_mp3(self):
        sender = "Sender <sender@email.com>"
        to = "Recepient <recepient@email.com>"
        subject = "This is a test email with attachements"
        message_text = "The is the message text of the email with attachments"
        message_html = "<p>This is the html message part of the email " "with attachments</p>"
        attachments = [f"{_dir}/assets/loremipsum.mp3"]

        msg = self.gmail._create_message_attachments(
            sender, to, subject, message_text, attachments, message_html=message_html
        )
        raw = self.gmail._encode_raw_message(msg)

        decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

        expected_items = [
            ("Content-Type", "multipart/alternative;\n boundary="),
            ("MIME-Version", "1.0"),
            ("to", to),
            ("from", sender),
            ("subject", subject),
        ]

        # The boundary id changes everytime. Replace it with the beginnig to
        # avoid failures
        updated_items = []
        for i in decoded.items():
            if "Content-Type" in i[0] and "multipart/alternative;\n boundary=" in i[1]:  # noqa
                updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
            else:
                updated_items.append((i[0], i[1]))

        # Check the metadata
        self.assertListEqual(updated_items, expected_items)

        # Check the message
        # The first part is just a container for the text and html parts
        parts = decoded.get_payload()

        self.assertEqual(parts[0].get_payload(), message_text)
        self.assertEqual(parts[1].get_payload(), message_html)

        with open(f"{_dir}/assets/loremipsum_b64_mp3.txt", "r") as f:
            b64_txt = f.read()
        self.assertEqual(parts[2].get_payload(), b64_txt)

        self.assertEqual(parts[2].get_content_type(), "audio/mpeg")

        # Check the number of parts
        expected_parts = 4
        self.assertEqual(sum([1 for i in decoded.walk()]), expected_parts)

    def test_create_message_attachments_mp4(self):
        sender = "Sender <sender@email.com>"
        to = "Recepient <recepient@email.com>"
        subject = "This is a test email with attachements"
        message_text = "The is the message text of the email with attachments"
        message_html = "<p>This is the html message part of the email " "with attachments</p>"
        attachments = [f"{_dir}/assets/loremipsum.mp4"]

        msg = self.gmail._create_message_attachments(
            sender, to, subject, message_text, attachments, message_html=message_html
        )
        raw = self.gmail._encode_raw_message(msg)

        decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

        expected_items = [
            ("Content-Type", "multipart/alternative;\n boundary="),
            ("MIME-Version", "1.0"),
            ("to", to),
            ("from", sender),
            ("subject", subject),
        ]

        # The boundary id changes everytime. Replace it with the beginnig to
        # avoid failures
        updated_items = []
        for i in decoded.items():
            if "Content-Type" in i[0] and "multipart/alternative;\n boundary=" in i[1]:  # noqa
                updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
            else:
                updated_items.append((i[0], i[1]))

        # Check the metadata
        self.assertListEqual(updated_items, expected_items)

        # Check the message
        # The first part is just a container for the text and html parts
        parts = decoded.get_payload()

        self.assertEqual(parts[0].get_payload(), message_text)
        self.assertEqual(parts[1].get_payload(), message_html)

        with open(f"{_dir}/assets/loremipsum_b64_mp4.txt", "r") as f:
            b64_txt = f.read()
        self.assertEqual(parts[2].get_payload(), b64_txt)

        self.assertEqual(parts[2].get_content_type(), "video/mp4")

        # Check the number of parts
        expected_parts = 4
        self.assertEqual(sum([1 for i in decoded.walk()]), expected_parts)

    def test_create_message_attachments_pdf(self):
        sender = "Sender <sender@email.com>"
        to = "Recepient <recepient@email.com>"
        subject = "This is a test email with attachements"
        message_text = "The is the message text of the email with attachments"
        message_html = "<p>This is the html message part of the email " "with attachments</p>"
        attachments = [f"{_dir}/assets/loremipsum.pdf"]

        msg = self.gmail._create_message_attachments(
            sender, to, subject, message_text, attachments, message_html=message_html
        )

        raw = self.gmail._encode_raw_message(msg)

        decoded = email.message_from_bytes(base64.urlsafe_b64decode(bytes(raw["raw"], "utf-8")))

        expected_items = [
            ("Content-Type", "multipart/alternative;\n boundary="),
            ("MIME-Version", "1.0"),
            ("to", to),
            ("from", sender),
            ("subject", subject),
        ]

        # The boundary id changes everytime. Replace it with the beginnig to
        # avoid failures
        updated_items = []
        for i in decoded.items():
            if "Content-Type" in i[0] and "multipart/alternative;\n boundary=" in i[1]:  # noqa
                updated_items.append(("Content-Type", "multipart/alternative;\n boundary="))
            else:
                updated_items.append((i[0], i[1]))

        # Check the metadata
        self.assertListEqual(updated_items, expected_items)

        # Check the message
        # The first part is just a container for the text and html parts
        parts = decoded.get_payload()

        self.assertEqual(parts[0].get_payload(), message_text)
        self.assertEqual(parts[1].get_payload(), message_html)

        with open(f"{_dir}/assets/loremipsum_b64_pdf.txt", "r") as f:
            b64_txt = f.read()
        self.assertEqual(parts[2].get_payload(), b64_txt)

        self.assertEqual(parts[2].get_content_type(), "application/pdf")

        # Check the number of parts
        expected_parts = 4
        self.assertEqual(sum([1 for i in decoded.walk()]), expected_parts)

    def test__validate_email_string(self):
        emails = [
            {"email": "Sender <sender@email.com>", "expected": True},
            {"email": "sender@email.com", "expected": True},
            {"email": "<sender@email.com>", "expected": True},
            {"email": "Sender sender@email.com", "expected": False},
            {"email": "Sender <sender2email.com>", "expected": False},
            {"email": "Sender <sender@email,com>", "expected": True},
            {"email": "Sender <sender+alias@email,com>", "expected": True},
        ]

        for e in emails:
            if e["expected"]:
                self.assertTrue(self.gmail._validate_email_string(e["email"]))
            else:
                self.assertRaises(ValueError, self.gmail._validate_email_string, e["email"])

    # TODO test sending emails


if __name__ == "__main__":
    unittest.main()
