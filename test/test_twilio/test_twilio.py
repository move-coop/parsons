import os
import unittest
import unittest.mock as mock
from parsons import Twilio


class TestTwilio(unittest.TestCase):
    def setUp(self):
        os.environ["TWILIO_ACCOUNT_SID"] = "MYFAKESID"
        os.environ["TWILIO_AUTH_TOKEN"] = "MYFAKEAUTHTOKEN"

        self.twilio = Twilio()
        self.twilio.client = mock.MagicMock()

    def test_get_account(self):
        fake_sid = "FAKESID"
        self.twilio.get_account(fake_sid)
        self.twilio.client.api.accounts.assert_called_with(fake_sid)

    def test_get_accounts(self):
        self.twilio.get_accounts(name="MyOrg", status="active")
        self.twilio.client.api.accounts.list.assert_called_with(
            friendly_name="MyOrg", status="active"
        )

    def test_get_messages(self):
        self.twilio.get_messages(date_sent="2019-10-29")
        self.twilio.client.messages.list.assert_called_with(
            date_sent="2019-10-29",
            to=None,
            from_=None,
            date_sent_before=None,
            date_sent_after=None,
        )

    def test_get_account_usage(self):
        # Make sure that it is calling the correct Twilio methods
        self.twilio.client.usage.records.today.list.assert_not_called()
        self.twilio.get_account_usage(time_period="today")
        self.twilio.client.usage.records.today.list.assert_called()

        self.twilio.client.usage.records.last_month.list.assert_not_called()
        self.twilio.get_account_usage(time_period="last_month")
        self.twilio.client.usage.records.last_month.list.assert_called()

        self.twilio.client.usage.records.this_month.list.assert_not_called()
        self.twilio.get_account_usage(time_period="this_month")
        self.twilio.client.usage.records.this_month.list.assert_called()

        self.twilio.client.usage.records.yesterday.list.assert_not_called()
        self.twilio.get_account_usage(time_period="yesterday")
        self.twilio.client.usage.records.yesterday.list.assert_called()

        # Make sure that it is calling the correct Twilio methods
        self.twilio.client.usage.records.daily.list.assert_not_called()
        self.twilio.get_account_usage(group_by="daily", start_date="10-19-2019")
        self.twilio.client.usage.records.daily.list.assert_called_with(start_date="10-19-2019")

        self.twilio.client.usage.records.monthly.list.assert_not_called()
        self.twilio.get_account_usage(group_by="monthly", start_date="10-19-2019")
        self.twilio.client.usage.records.monthly.list.assert_called_with(start_date="10-19-2019")

        self.twilio.client.usage.records.yearly.list.assert_not_called()
        self.twilio.get_account_usage(group_by="yearly", start_date="10-19-2019")
        self.twilio.client.usage.records.yearly.list.assert_called_with(start_date="10-19-2019")
