import os
import unittest
import unittest.mock as mock
from parsons.salesforce.salesforce import Salesforce, Table

class TestSalesforce(unittest.TestCase):
    
    def setUp(self):

        os.environ['SALESFORCE_USERNAME'] = 'MYFAKEUSERNAME'
        os.environ['SALESFORCE_PASSWORD'] = 'MYFAKEPASSWORD'
        os.environ['SALESFORCE_SECURITY_TOKEN'] = 'MYFAKESECURITYTOKEN'

        self.sf = Salesforce()
        self.sf._client = mock.MagicMock()

        self.sf._client.query_all.return_value = [{'Id': 1, 'value': 'FAKE'}]
        self.sf._client.bulk.Contact.insert.return_value = [{
            'success': True, 'created': True, 'id': '1234567890AaBbC', 'errors': []
        }]
        self.sf._client.bulk.Contact.update.return_value = [{
            'success': True, 'created': False, 'id': '1234567890AaBbC', 'errors': []
        }]
        self.sf._client.bulk.Contact.upsert.return_value = [{
            'success': True, 'created': False, 'id': '1234567890AaBbC', 'errors': []
        },
        {
            'success': True, 'created': True, 'id': '1234567890AaBbc', 'errors': []
        }]
        self.sf._client.bulk.Contact.delete.return_value = [{
            'success': True, 'created': False, 'id': '1234567890AaBbC', 'errors': []
        }]

    def test_describe(self):

        pass

    def test_describe_fields(self):

        # TO DO: test this with requests mock instead?
        pass

    def test_query(self):

        fake_soql = 'FAKESOQL'
        response = self.sf.query(fake_soql) 
        assert self.sf.client.query_all.called_with(fake_soql)
        self.assertEqual(response[0]['value'], 'FAKE')

    def test_insert(self):

        fake_data = Table([{'firstname': 'Chrisjen', 'lastname': 'Avasarala'}])
        response = self.sf.insert_record('Contact', fake_data)
        assert self.sf.client.bulk.Contact.insert.called_with(fake_data)
        assert response[0]['created']

    def test_update(self):

        fake_data = Table([{'id': '1234567890AaBbC',
            'firstname': 'Chrisjen',
            'lastname': 'Avasarala'}])
        response = self.sf.update_record('Contact', fake_data)
        assert self.sf.client.bulk.Contact.update.called_with(fake_data)
        assert not response[0]['created']

    def test_upsert(self):

        fake_data = Table([{'id': '1234567890AaBbC',
            'firstname': 'Chrisjen',
            'lastname': 'Avasarala'},
            {'id': None,
            'firstname': 'Roberta',
            'lastname': 'Draper'}])
        response = self.sf.upsert_record('Contact', fake_data, 'id')
        assert self.sf.client.bulk.Contact.update.called_with(fake_data)
        print(response)
        assert not response[0]['created']
        assert response[1]['created']

    def test_delete(self):

        fake_data = Table([{'id': '1234567890AaBbC'}])
        response = self.sf.delete_record('Contact', fake_data)
        assert self.sf.client.bulk.Contact.update.called_with(fake_data)
        assert not response[0]['created']
