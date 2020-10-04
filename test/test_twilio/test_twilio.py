import os
import unittest
import unittest.mock as mock
from parsons.twilio.twilio import Twilio


class TestTwilio(unittest.TestCase):

    def setUp(self):

        os.environ['TWILIO_ACCOUNT_SID'] = 'MYFAKESID'
        os.environ['TWILIO_AUTH_TOKEN'] = 'MYFAKEAUTHTOKEN'

        self.twilio = Twilio()
        self.twilio.client = mock.MagicMock()

    def test_get_account(self):

        fake_sid = 'FAKESID'
        self.twilio.get_account(fake_sid)
        assert self.twilio.client.api.accounts.called_with(fake_sid)

    def test_get_accounts(self):

        self.twilio.get_accounts(name='MyOrg', status='active')
        assert self.twilio.client.api.accounts.list.called_with(
            friendly_name='MyOrg', status='active')

    def test_get_messages(self):

        self.twilio.get_messages(date_sent='2019-10-29')
        assert self.twilio.client.messages.list.called_with(date_sent='2019-10-29')

    def test_get_account_usage(self):

        # Make sure that it is calling the correct Twilio methods
        self.twilio.get_account_usage(time_period='today')
        assert self.twilio.client.usage.records.today.list.called_with(time_period='today')
        self.twilio.get_account_usage(time_period='last_month')
        assert self.twilio.client.usage.records.last_month.list.called_with(
            time_period='last_month')
        self.twilio.get_account_usage(time_period='this_month')
        assert self.twilio.client.usage.records.this_month.list.called_with(
            time_period='this_month')
        self.twilio.get_account_usage(time_period='yesterday')
        assert self.twilio.client.usage.records.today.list.called_with(time_period='yesterday')

        # Make sure that it is calling the correct Twilio methods
        self.twilio.get_account_usage(time_period='daily', start_date='10-19-2019')
        assert self.twilio.client.usage.records.daily.list.called_with(start_date='10-19-2019')
        self.twilio.get_account_usage(time_period='monthly', start_date='10-19-2019')
        assert self.twilio.client.usage.records.monthly.list.called_with(start_date='10-19-2019')
        self.twilio.get_account_usage(time_period='yearly', start_date='10-19-2019')
        assert self.twilio.client.usage.records.yearly.list.called_with(start_date='10-19-2019')
