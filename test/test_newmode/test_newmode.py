import os
import unittest
import unittest.mock as mock
from parsons.newmode import Newmode

class TestNewmode(unittest.TestCase):

    def setUp(self):

        os.environ['NEWMODE_API_USER'] = 'MYFAKEUSERNAME'
        os.environ['NEWMODE_API_PASSWORD'] = 'MYFAKEPASSWORD'

        self.nm = Newmode()
        self.nm.client = mock.MagicMock()

        self.nm.client.getTools.return_value = [
            {
                'id': 1,
                'title': 'Tool 1'
            },
            {
                'id': 2,
                'title': 'Tool 2'
            },
        ]

        self.nm.client.getTool.return_value = {
            'id': 1,
            'name': 'Tool 1'
        }

        self.nm.client.getAction.return_value = {
            'required_fields': [
                {
                    'key': 'first_name',
                    'name': 'First Name',
                    'type': 'textfield',
                    'value': ''
                }
            ]
        }

        self.nm.client.lookupTargets.return_value = {
            '0': {
                'unique_id': 'TESTMODE-uniqueid',
                'full_name': 'John Doe'
            }
        }

        self.nm.client.runAction.return_value = {
            'sid': 1
        }

    def test_get_tools(self):
        args = {}
        response = self.nm.get_tools(args)
        self.nm.client.getTools.assert_called_with(params=args)
        self.assertEqual(response[0]['title'], 'Tool 1')

    def test_get_tool(self):
        id = 1
        response = self.nm.get_tool(id)
        self.nm.client.getTool.assert_called_with(id, params={})
        self.assertEqual(response[0]['name'], 'Tool 1')

    def test_lookup_targets(self):
        id = 1
        response = self.nm.lookup_targets(id)
        self.nm.client.lookupTargets.assert_called_with(id, None, params={})
        self.assertEqual(response[0]['full_name'], 'John Doe')

    def test_get_action(self):
        id = 1
        response = self.nm.get_action(id)
        self.nm.client.getAction.assert_called_with(id, params={})
        self.assertEqual(response[0]['required_fields'][0]['key'], 'first_name')

    def test_run_action(self):
        id = 1
        payload = {
            'email': 'john.doe@example.com',
            'first_name': 'John',
        }
        response = self.nm.run_action(id, payload)
        self.nm.client.runAction.assert_called_with(id, payload, params={})
        self.assertEqual(response, 1)
