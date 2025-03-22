import os
import unittest
import unittest.mock as mock

from parsons import Salesforce, Table


class TestSalesforce(unittest.TestCase):
    def setUp(self):
        os.environ["SALESFORCE_USERNAME"] = "MYFAKEUSERNAME"
        os.environ["SALESFORCE_PASSWORD"] = "MYFAKEPASSWORD"
        os.environ["SALESFORCE_SECURITY_TOKEN"] = "MYFAKESECURITYTOKEN"

        self.sf = Salesforce()
        self.sf._client = mock.MagicMock()
        self.sf._client.query_all.return_value = {
            "totalSize": 1,
            "done": True,
            "records": [
                {
                    "attributes": {
                        "type": "Contact",
                        "url": "/services/data/v38.0/" + "sobjects/Contact/" + "1234567890AaBbC",
                    },
                    "Id": "1234567890AaBbC",
                }
            ],
        }
        self.sf._client.bulk.Contact.insert.return_value = [
            {"success": True, "created": True, "id": "1234567890AaBbC", "errors": []}
        ]
        self.sf._client.bulk.Contact.update.return_value = [
            {"success": True, "created": False, "id": "1234567890AaBbC", "errors": []}
        ]
        self.sf._client.bulk.Contact.upsert.return_value = [
            {"success": True, "created": False, "id": "1234567890AaBbC", "errors": []},
            {"success": True, "created": True, "id": "1234567890AaBbc", "errors": []},
        ]
        self.sf._client.bulk.Contact.delete.return_value = [
            {"success": True, "created": False, "id": "1234567890AaBbC", "errors": []}
        ]

    def test_describe(self):
        pass

    def test_describe_fields(self):
        # TO DO: test this with requests mock instead?
        pass

    def test_query(self):
        fake_soql = "FAKESOQL"
        response = self.sf.query(fake_soql)
        self.sf.client.query_all.assert_called_with(fake_soql)
        assert response["records"][0]["Id"] == "1234567890AaBbC"

    def test_insert(self):
        fake_data = Table([{"firstname": "Chrisjen", "lastname": "Avasarala"}])
        response = self.sf.insert_record("Contact", fake_data)
        self.sf.client.bulk.Contact.insert.assert_called_with(fake_data.to_dicts())
        assert response[0]["created"]

    def test_update(self):
        fake_data = Table(
            [
                {
                    "id": "1234567890AaBbC",
                    "firstname": "Chrisjen",
                    "lastname": "Avasarala",
                }
            ]
        )
        response = self.sf.update_record("Contact", fake_data)
        self.sf.client.bulk.Contact.update.assert_called_with(fake_data.to_dicts())
        assert not response[0]["created"]

    def test_upsert(self):
        fake_data = Table(
            [
                {
                    "id": "1234567890AaBbC",
                    "firstname": "Chrisjen",
                    "lastname": "Avasarala",
                },
                {"id": None, "firstname": "Roberta", "lastname": "Draper"},
            ]
        )
        response = self.sf.upsert_record("Contact", fake_data, "id")
        self.sf.client.bulk.Contact.upsert.assert_called_with(fake_data.to_dicts(), "id")
        print(response)
        assert not response[0]["created"]
        assert response[1]["created"]

    def test_delete(self):
        fake_data = Table([{"id": "1234567890AaBbC"}])
        response = self.sf.delete_record("Contact", fake_data)
        self.sf.client.bulk.Contact.delete.assert_called_with(fake_data.to_dicts())
        assert not response[0]["created"]
