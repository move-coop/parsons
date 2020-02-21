import unittest
import requests_mock
import json
from parsons.bill_com.bill_com import BillCom


class TestBillCom(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, m):

        self.api_url = 'http://FAKEURL.com/'

        m.post(self.api_url + 'Login.json',
               text=json.dumps({'response_data': {'sessionId': 'FAKE'}}))
        self.bc = BillCom('FAKE', 'FAKE', 'FAKE', 'FAKE', self.api_url)

        self.fake_time = '2019-02-29T00:00:00.000+0000'
        self.fake_date = '2019-02-29'
        self.fake_customer_email = 'fake_customer_email@fake_customer_email.com'

        self.fake_user_list = {'response_status': 0,
                               'response_message': 'Success',
                               'response_data': [{'entity': 'User',
                                                  'id': 'fake_user_id',
                                                  'isActive': '1',
                                                  'createdTime': self.fake_time,
                                                  'updatedTime': self.fake_time,
                                                  'loginId': 'fake_login_id',
                                                  'profileId': 'fake_profile_id',
                                                  'firstName': 'fake_first_name',
                                                  'lastName': 'fake_last_name',
                                                  'email': 'fake_email@fake_email.com',
                                                  'timezoneId': '7',
                                                  'partnerUserGroupType': '2'}]}

        self.fake_customer_list = {'response_status': 0,
                                   'response_message': 'Success',
                                   'response_data': [{'entity': 'Customer',
                                                      'id': 'fake_customer_id',
                                                      'isActive': '1',
                                                      'createdTime': self.fake_time,
                                                      'updatedTime': self.fake_time,
                                                      'name': 'fake_customer_name',
                                                      'shortName': 'fake_shorter_customer_name',
                                                      'parentCustomerId': '0',
                                                      'companyName': 'fake_company_name',
                                                      'contactFirstName': 'fake_first_name',
                                                      'contactLastName': 'fake_last_name',
                                                      'accNumber': '0',
                                                      'billAddress1': '123 Fake Street',
                                                      'billAddress2': 'Suite 13',
                                                      'billAddress3': None,
                                                      'billAddress4': None,
                                                      'billAddressCity': 'Fake City',
                                                      'billAddressState': 'FS',
                                                      'billAddressCountry': 'USA',
                                                      'billAddressZip': '11111',
                                                      'shipAddress1': '123 Fake Street',
                                                      'shipAddress2': 'Office 13',
                                                      'shipAddress3': None,
                                                      'shipAddress4': None,
                                                      'shipAddressCity': 'Fake City',
                                                      'shipAddressState': 'FS',
                                                      'shipAddressCountry': 'USA',
                                                      'shipAddressZip': '11111',
                                                      'email': self.fake_customer_email,
                                                      'phone': '123-123-1234',
                                                      'altPhone': '123-123-1256',
                                                      'fax': '123-123-1235',
                                                      'description': 'fake_description',
                                                      'printAs': None,
                                                      'mergedIntoId': '0',
                                                      'hasAuthorizedToCharge': False,
                                                      'accountType': '1'}]}

        self.fake_customer_read_json = {'response_status': 0,
                                        'response_message': 'Success',
                                        'response_data':
                                        self.fake_customer_list['response_data'][0]}

        self.fake_invoice_list = {'response_status': 0,
                                  'response_message': 'Success',
                                  'response_data': [{'entity': 'Invoice',
                                                     'id': 'fake_invoice_id',
                                                     'isActive': '1',
                                                     'createdTime': self.fake_time,
                                                     'updatedTime': self.fake_time,
                                                     'customerId': 'fake_customer_id',
                                                     'invoiceNumber': 'fake_invoice_number',
                                                     'invoiceDate': self.fake_date,
                                                     'dueDate': self.fake_date,
                                                     'glPostingDate': self.fake_date,
                                                     'amount': 1.0,
                                                     'amountDue': 1.0,
                                                     'paymentStatus': '1',
                                                     'description': None,
                                                     'poNumber': None,
                                                     'isToBePrinted': False,
                                                     'isToBeEmailed': False,
                                                     'lastSentTime': None,
                                                     'itemSalesTax': '0',
                                                     'salesTaxPercentage': 0,
                                                     'salesTaxTotal': 0.0,
                                                     'terms': None,
                                                     'salesRep': None,
                                                     'FOB': None,
                                                     'shipDate': None,
                                                     'shipMethod': None,
                                                     'departmentId': '0',
                                                     'locationId': '0',
                                                     'actgClassId': '0',
                                                     'jobId': '0',
                                                     'payToBankAccountId': '0',
                                                     'payToChartOfAccountId': '0',
                                                     'invoiceTemplateId': '0',
                                                     'hasAutoPay': False,
                                                     'source': '0',
                                                     'emailDeliveryOption': '1',
                                                     'mailDeliveryOption': '0',
                                                     'creditAmount': 0.0,
                                                     'invoiceLineItems': [{'entity':
                                                                           'InvoiceLineItem',
                                                                           'id':
                                                                           'fake_line_item_id',
                                                                           'createdTime':
                                                                           self.fake_time,
                                                                           'updatedTime':
                                                                           self.fake_time,
                                                                           'invoiceId':
                                                                           'fake_invoice_id',
                                                                           'itemId': '0',
                                                                           'quantity': 1,
                                                                           'amount': 1.0,
                                                                           'price': None,
                                                                           'serviceDate': None,
                                                                           'ratePercent': None,
                                                                           'chartOfAccountId': '0',
                                                                           'departmentId': '0',
                                                                           'locationId': '0',
                                                                           'actgClassId': '0',
                                                                           'jobId': '0',
                                                                           'description': None,
                                                                           'taxable': False,
                                                                           'taxCode': 'Non'}]}]}

        self.fake_invoice_read_json = self.fake_invoice_read_json = \
            {'response_status': 0,
             'response_message': 'Success',
             'response_data':
             self.fake_invoice_list['response_data'][0]}

        self.fake_invoice_line_items = \
            self.fake_invoice_list['response_data'][0]['invoiceLineItems']

    def test_init(self):
        self.assertEqual(self.bc.session_id, 'FAKE')

    def test_get_payload(self):
        fake_json = {'fake_key': 'fake_data'}
        payload = self.bc.get_payload(fake_json)
        self.assertEqual(payload, {'devKey': self.bc.dev_key,
                                   'sessionId': self.bc.session_id,
                                   'data': json.dumps(fake_json)})

    @requests_mock.Mocker()
    def test_post_request(self, m):
        data = {
            'id': 'fake_customer_id'
        }
        m.post(self.api_url + 'Crud/Read/Customer.json',
               text=json.dumps(self.fake_customer_read_json))
        self.assertEqual(self.bc.post_request(data, 'Read', 'Customer'),
                         self.fake_customer_read_json)

    @requests_mock.Mocker()
    def test_get_request_response(self, m):
        data = {
            'id': 'fake_customer_id'
        }
        m.post(self.api_url + 'Crud/Read/Customer.json',
               text=json.dumps(self.fake_customer_read_json))
        self.assertEqual(self.bc.get_request_response(data, 'Read', 'Customer', 'response_data'),
                         self.fake_customer_read_json['response_data'])

    @requests_mock.Mocker()
    def test_get_user_list(self, m):
        m.post(self.api_url + 'List/User.json',
               text=json.dumps(self.fake_user_list))
        self.assertAlmostEqual(self.bc.get_user_list(),
                               self.fake_user_list['response_data'])

    @requests_mock.Mocker()
    def test_get_customer_list(self, m):
        m.post(self.api_url + 'List/Customer.json',
               text=json.dumps(self.fake_customer_list))
        self.assertAlmostEqual(self.bc.get_customer_list(),
                               self.fake_customer_list['response_data'])

    @requests_mock.Mocker()
    def test_get_invoice_list(self, m):
        m.post(self.api_url + 'List/Invoice.json',
               text=json.dumps(self.fake_invoice_list))
        self.assertAlmostEqual(self.bc.get_invoice_list(),
                               self.fake_invoice_list['response_data'])

    @requests_mock.Mocker()
    def test_read_customer(self, m):
        m.post(self.api_url + 'Crud/Read/Customer.json',
               text=json.dumps(self.fake_customer_read_json))
        self.assertAlmostEqual(self.bc.read_customer('fake_customer_id'),
                               self.fake_customer_read_json['response_data'])

    @requests_mock.Mocker()
    def test_read_invoice(self, m):
        m.post(self.api_url + 'Crud/Read/Invoice.json',
               text=json.dumps(self.fake_invoice_read_json))
        self.assertAlmostEqual(self.bc.read_invoice('fake_invoice_id'),
                               self.fake_invoice_read_json['response_data'])

    def test_check_customer(self):
        self.assertTrue(self.bc.check_customer({'id': 'fake_customer_id'},
                                               {'id': 'fake_customer_id'}))
        self.assertTrue(self.bc.check_customer({'email': 'fake_email@fake_email.com'},
                                               {'id': 'fake_customer_id',
                                                'email': 'fake_email@fake_email.com'}))
        self.assertFalse(self.bc.check_customer({'id': 'fake_customer_id1'},
                                                {'id': 'fake_customer_id2'}))
        self.assertFalse(self.bc.check_customer({'email': 'fake_email1@fake_email.com'},
                                                {'id': 'fake_customer_id2',
                                                 'email': 'fake_email2@fake_email.com'}))

    @requests_mock.Mocker()
    def test_create_customer(self, m):
        m.post(self.api_url + 'List/Customer.json',
               text=json.dumps(self.fake_customer_list))
        m.post(self.api_url + 'Crud/Create/Customer.json',
               text=json.dumps(self.fake_customer_read_json))
        self.assertEqual(self.bc.create_customer('fake_customer_name',
                                                 self.fake_customer_email),
                         self.fake_customer_read_json['response_data'])

    @requests_mock.Mocker()
    def test_create_invoice(self, m):
        m.post(self.api_url + 'Crud/Create/Invoice.json',
               text=json.dumps(self.fake_invoice_read_json))
        self.assertEqual(self.bc.create_invoice('fake_customer_id',
                                                '1',
                                                self.fake_date,
                                                self.fake_date,
                                                self.fake_invoice_line_items),
                         self.fake_invoice_read_json['response_data'])

    @requests_mock.Mocker()
    def test_send_invoice(self, m):
        send_invoice_response_json = {'response_status': 0,
                                      'response_message': 'Success',
                                      'response_data': {}}
        m.post(self.api_url + 'SendInvoice.json',
               text=json.dumps(send_invoice_response_json))
        self.assertEqual(self.bc.send_invoice('fake_invoice_id',
                                              'fake_user_id',
                                              'fake_user_email@fake_email.com',
                                              'fake_subject',
                                              'fake_message_body'), {})
