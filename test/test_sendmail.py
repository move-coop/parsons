import io
import pytest
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase

from parsons.notifications.sendmail import EmptyListError, SendMail


@pytest.fixture(scope="function")
def dummy_sendmail():
    """Have to create a dummy class that inherits from SendMail and defines a couple
    of methods in order to test out the methods that aren't abstract.
    """

    class DummySendMail(SendMail):
        def __init__(self):
            pass

        def _send_message(self, message):
            pass

    return DummySendMail()


class TestSendMailCreateMessageSimple:
    def test_creates_mimetext_message(self, dummy_sendmail):
        message = dummy_sendmail._create_message_simple("from", "to", "subject", "text")
        assert isinstance(message, MIMEText)

    def test_message_contents_set_appropriately(self, dummy_sendmail):
        message = dummy_sendmail._create_message_simple("from", "to", "subject", "text")
        assert message.get("from") == "from"
        assert message.get("to") == "to"
        assert message.get("subject") == "subject"
        assert message.get_payload() == "text"


class TestSendMailCreateMessageHtml:
    def test_creates_multipart_message(self, dummy_sendmail):
        message = dummy_sendmail._create_message_html("from", "to", "subject", "text", "html")
        assert isinstance(message, MIMEMultipart)

    def test_sets_to_from_subject(self, dummy_sendmail):
        message = dummy_sendmail._create_message_html("from", "to", "subject", "text", "html")
        assert message.get("from") == "from"
        assert message.get("to") == "to"
        assert message.get("subject") == "subject"

    def test_works_if_no_message_text(self, dummy_sendmail):
        message = dummy_sendmail._create_message_html("from", "to", "subject", None, "html")
        assert len(message.get_payload()) == 1
        assert message.get_payload()[0].get_payload() == "html"
        assert message.get_payload()[0].get_content_type() == "text/html"

    def test_works_with_text_and_html(self, dummy_sendmail):
        message = dummy_sendmail._create_message_html("from", "to", "subject", "text", "html")
        assert len(message.get_payload()) == 2
        assert message.get_payload()[0].get_payload() == "text"
        assert message.get_payload()[0].get_content_type() == "text/plain"
        assert message.get_payload()[1].get_payload() == "html"
        assert message.get_payload()[1].get_content_type() == "text/html"


class TestSendMailCreateMessageAttachments:
    def test_creates_multipart_message(self, dummy_sendmail):
        message = dummy_sendmail._create_message_attachments("from", "to", "subject", "text", [])
        assert isinstance(message, MIMEMultipart)

    def test_can_handle_html(self, dummy_sendmail):
        message = dummy_sendmail._create_message_attachments(
            "from", "to", "subject", "text", [], message_html="html"
        )
        assert len(message.get_payload()) == 2
        assert message.get_payload()[0].get_payload() == "text"
        assert message.get_payload()[0].get_content_type() == "text/plain"
        assert message.get_payload()[1].get_payload() == "html"
        assert message.get_payload()[1].get_content_type() == "text/html"

    @pytest.mark.parametrize(
        "filename,expected_type",
        [
            ("image.png", MIMEImage),
            ("application.exe", MIMEApplication),
            ("text.txt", MIMEText),
            ("audio.mp3", MIMEAudio),
            (
                "video.mp4",
                MIMEBase,
            ),  # This will fail if the method is updated to parse video
        ],
    )
    def test_properly_detects_file_types(self, tmp_path, dummy_sendmail, filename, expected_type):
        filename = tmp_path / filename
        filename.write_bytes(b"Parsons")
        message = dummy_sendmail._create_message_attachments(
            "from", "to", "subject", "text", [filename]
        )
        assert len(message.get_payload()) == 2  # text body plus attachment
        assert isinstance(message.get_payload()[1], expected_type)

    @pytest.mark.parametrize("buffer", [io.StringIO, io.BytesIO])
    def test_works_with_buffers(self, dummy_sendmail, buffer):
        value = "Parsons"
        if buffer is io.BytesIO:
            value = b"Parsons"
        message = dummy_sendmail._create_message_attachments(
            "from", "to", "subject", "text", [buffer(value)]
        )
        assert len(message.get_payload()) == 2  # text body plus attachment
        assert isinstance(message.get_payload()[1], MIMEApplication)


class TestSendMailValidateEmailString:
    @pytest.mark.parametrize("bad_email", ["a", "a@", "a+b", "@b.com"])
    def test_errors_with_invalid_emails(self, dummy_sendmail, bad_email):
        with pytest.raises(ValueError):
            dummy_sendmail._validate_email_string(bad_email)

    @pytest.mark.parametrize("good_email", ["a@b", "a+b@c", "a@d.com", "a@b.org"])
    def test_passes_valid_emails(self, dummy_sendmail, good_email):
        dummy_sendmail._validate_email_string(good_email)


class TestSendMailSendEmail:
    @pytest.fixture(scope="function")
    def patched_sendmail(self):
        class PatchedSendMail(SendMail):
            def __init__(self):
                pass

            def _send_message(self, message):
                self.message = message  # Stores message for post-call introspection

        return PatchedSendMail()

    def test_errors_when_send_message_not_implemented(self):
        with pytest.raises(TypeError, match="Can't instantiate abstract class SendMail"):
            SendMail().send_email("from@from.com", "to@to.com", "subject", "text")

    def test_can_handle_lists_of_emails(self, patched_sendmail):
        patched_sendmail.send_email("from", ["to1@to1.com", "to2@to2.com"], "subject", "text")
        assert patched_sendmail.message.get("to") == "to1@to1.com, to2@to2.com"

    def test_errors_if_an_email_in_a_list_doesnt_validate(self, patched_sendmail):
        with pytest.raises(ValueError, match="Invalid email address"):
            patched_sendmail.send_email(
                "from", ["to1@to1.com", "invalid", "to2@to2.com"], "subject", "text"
            )

    def test_errors_if_no_to_email_is_specified(self, patched_sendmail):
        with pytest.raises(EmptyListError, match="Must contain at least 1 email"):
            patched_sendmail.send_email("from", [], "subject", "text")

    def test_appropriately_dispatches_html_email(self, patched_sendmail):
        patched_sendmail.send_email("from", "to@to.com", "subject", "text", message_html="html")
        assert len(patched_sendmail.message.get_payload()) == 2
        assert patched_sendmail.message.get_payload()[1].get_content_type() == "text/html"

    def test_appropriately_handles_filename_specified_as_string(self, tmp_path, patched_sendmail):
        filename = tmp_path / "test.txt"
        filename.write_bytes(b"Parsons")
        patched_sendmail.send_email("from", "to@to.com", "subject", "text", files=str(filename))
        assert len(patched_sendmail.message.get_payload()) == 2
        assert isinstance(patched_sendmail.message.get_payload()[1], MIMEText)
