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
            "required_fields": [
                {
                    "key": "first_name",
                    "name": "First Name",
                    "type": "textfield",
                    "value": ""
                }
            ]
        }

        self.nm.client.lookupTargets.return_value = {
            "0": {
                "unique_id": "TESTMODE-uniqueid",
                "full_name": "John Doe"
            }
        }

    def test_get_tools(self):
        args = {}
        response = self.nm.get_tools(args)
        assert self.nm.client.getTools.called_with(args)
        self.assertEqual(response[0]['title'], 'Tool 1')

    def test_get_tool(self):
        id = 1
        response = self.nm.get_tool(id)
        assert self.nm.client.getTool.called_with(id)
        self.assertEqual(response[0]['name'], 'Tool 1')

    def test_lookup_targets(self):
        id = 1
        response = self.nm.lookup_targets(id)
        assert self.nm.client.lookupTargets.called_with(id)
        self.assertEqual(response[0]['full_name'], 'John Doe')

    def test_get_action(self):
        id = 1
        response = self.nm.get_action(id)
        assert self.nm.client.getAction.called_with(id)
        self.assertEqual(response[0]['required_fields'][0]['key'], 'first_name')
