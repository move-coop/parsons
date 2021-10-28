import unittest
import requests_mock
from parsons import Table
from parsons.bluelink import Bluelink, BluelinkPerson, BluelinkIdentifier, BluelinkEmail


class TestBluelink(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, m):
        self.bluelink = Bluelink("fake_user", "fake_password")

    @staticmethod
    def row_to_person(row):
        """
        dict -> BluelinkPerson
        Transforms a parsons Table row to a BluelinkPerson.
        This function is passed into bulk_upsert_person along with a Table
        """
        email = row["email"]
        return BluelinkPerson(
            identifiers=[
                BluelinkIdentifier(source="FAKESOURCE", identifier=email),
            ],
            emails=[BluelinkEmail(address=email, primary=True)],
            family_name=row["family_name"],
            given_name=row["given_name"],
        )

    @staticmethod
    def get_table():
        return Table([
            {"given_name": "Bart", "family_name": "Simpson", "email": "bart@springfield.net"},
            {"given_name": "Homer", "family_name": "Simpson", "email": "homer@springfield.net"},
        ])

    @requests_mock.Mocker()
    def test_bulk_upsert_person(self, m):
        """
        This function demonstrates how to use a "row_to_person" function to bulk
        insert people using a Table as the data source
        """
        # Mock POST requests to api
        m.post(self.bluelink.api_url)

        # get data as a parsons Table
        tbl = self.get_table()

        # String to identify that the data came from your system. For example, your company name.
        source = "BLUELINK-PARSONS-TEST"

        # call bulk_upsert_person
        # passing in the source, the Table, and the function that maps a Table row -> BluelinkPerson
        self.bluelink.bulk_upsert_person(source, tbl, self.row_to_person)

    @requests_mock.Mocker()
    def test_upsert_person(self, m):
        """
        This function demonstrates how to insert a single BluelinkPerson record
        """
        # Mock POST requests to api
        m.post(self.bluelink.api_url)

        # create a BluelinkPerson object
        # The BluelinkIdentifier is pretending that the user can be
        # identified in SALESFORCE with FAKE_ID as her id
        person = BluelinkPerson(identifiers=[BluelinkIdentifier(source="SALESFORCE",
                                                                identifier="FAKE_ID")],
                                given_name="Jane", family_name="Doe",
                                emails=[BluelinkEmail(address="jdoe@example.com", primary=True)])

        # String to identify that the data came from your system. For example, your company name.
        source = "BLUELINK-PARSONS-TEST"

        # call upsert_person
        self.bluelink.upsert_person(source, person)

    def test_table_to_people(self):
        """
        Test transforming a parsons Table -> list[BluelinkPerson]
        """
        # setup
        tbl = self.get_table()

        # function under test
        actual_people = BluelinkPerson.from_table(tbl, self.row_to_person)

        # expected:
        person1 = BluelinkPerson(
            identifiers=[BluelinkIdentifier(source="FAKESOURCE",
                                            identifier="bart@springfield.net")],
            emails=[BluelinkEmail(address="bart@springfield.net", primary=True)],
            family_name="Simpson", given_name="Bart")
        person2 = BluelinkPerson(
            identifiers=[BluelinkIdentifier(source="FAKESOURCE",
                                            identifier="homer@springfield.net")],
            emails=[BluelinkEmail(address="homer@springfield.net", primary=True)],
            family_name="Simpson", given_name="Homer")
        expected_people = [person1, person2]
        self.assertEqual(actual_people, expected_people)
