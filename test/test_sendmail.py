import pytest

from parsons.notifications.sendmail import SendMail


class TestSendMailValidateEmailString:
    @pytest.mark.parametrize("bad_email", ["a", "a@", "a+b", "@b.com"])
    def test_errors_with_invalid_emails(self, bad_email):
        with pytest.raises(ValueError):
            SendMail()._validate_email_string(bad_email)

    @pytest.mark.parametrize("good_email", ["a@b", "a+b@c", "a@d.com", "a@b.org"])
    def test_passes_valid_emails(self, good_email):
        SendMail()._validate_email_string(good_email)