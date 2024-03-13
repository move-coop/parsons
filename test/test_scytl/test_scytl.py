import unittest
import os
import requests_mock
import csv
from parsons.scytl import Scytl, scytl

TEST_STATE = "GA"
TEST_ELECTION_ID = "114729"
TEST_VERSION_NUM = "296262"

_DIR = os.path.dirname(__file__)


class TestScytl(unittest.TestCase):
    def setUp(self):
        self.scy = Scytl(TEST_STATE, TEST_ELECTION_ID)

        self.requests_mock = requests_mock.Mocker()

        self._mock_responses(self.requests_mock)

    def tearDown(self) -> None:
        self.requests_mock.stop()

    def test_get_summary_results_succeeds(self):
        result = self.scy.get_summary_results()

        with open(f"{_DIR}/114729_summary_expected.csv", "r") as expected:
            expectedResult = list(csv.DictReader(expected, delimiter=","))

            for i, row in enumerate(result):
                expectedResultRow = expectedResult[i]

                expectedResultRow["counties_reporting"] = (
                    expectedResultRow["counties_reporting"] or None
                )
                expectedResultRow["total_counties"] = expectedResultRow["total_counties"] or None

                self.assertDictEqual(row, expectedResultRow)

    def test_get_summary_results_skips_if_no_version_update(self):
        result = self.scy.get_summary_results()

        self.assertIsNotNone(result)

        result = self.scy.get_summary_results()

        self.assertIsNone(result)

        result = self.scy.get_summary_results(True)

        self.assertIsNotNone(result)

    def test_get_detailed_results_succeeds(self):
        result = self.scy.get_detailed_results()

        with open(f"{_DIR}/114729_county_expected.csv", "r") as expected:
            expectedResult = list(csv.DictReader(expected, delimiter=","))

            for i in range(len(result)):
                expectedResultRow = expectedResult[i]

                expectedResultRow["recorded_votes"] = int(expectedResultRow["recorded_votes"])
                expectedResultRow["timestamp_last_updated"] = self.scy._parse_date_to_utc(
                    expectedResultRow["timestamp_last_updated"]
                )

                self.assertDictEqual(result[i], expectedResultRow)

    def test_get_detailed_results_skips_if_no_version_update(self):
        result = self.scy.get_detailed_results()

        self.assertIsNotNone(result)

        result = self.scy.get_detailed_results()

        self.assertIsNone(result)

        result = self.scy.get_detailed_results(True)

        self.assertIsNotNone(result)

    def test_get_detailed_results_for_participating_counties_succeeds(self):
        _, result = self.scy.get_detailed_results_for_participating_counties()

        with open(f"{_DIR}/114729_precinct_expected.csv", "r") as expected:
            expectedResult = list(csv.DictReader(expected, delimiter=","))

            for i in range(len(result)):
                expectedResultRow = expectedResult[i]

                expectedResultRow["recorded_votes"] = int(expectedResultRow["recorded_votes"])
                expectedResultRow["timestamp_last_updated"] = self.scy._parse_date_to_utc(
                    expectedResultRow["timestamp_last_updated"]
                )

                self.assertDictEqual(result[i], expectedResultRow)

    def test_get_detailed_results_for_participating_counties_succeeds_for_two_counties(
        self,
    ):
        counties = ["Barrow", "Clarke"]

        _, result = self.scy.get_detailed_results_for_participating_counties(county_names=counties)

        with open(f"{_DIR}/114729_precinct_expected.csv", "r") as expected:
            expectedResult = csv.DictReader(expected, delimiter=",")

            filteredExpectedResults = list(
                filter(lambda x: x["county_name"] in counties, expectedResult)
            )

            for i, row in enumerate(result):
                expectedResultRow = filteredExpectedResults[i]

                expectedResultRow["recorded_votes"] = int(expectedResultRow["recorded_votes"])
                expectedResultRow["timestamp_last_updated"] = self.scy._parse_date_to_utc(
                    expectedResultRow["timestamp_last_updated"]
                )

                self.assertDictEqual(row, expectedResultRow)

    def test_get_detailed_results_for_participating_counties_missing_counties_update(
        self,
    ):
        counties = ["Barrow"]

        _, result = self.scy.get_detailed_results_for_participating_counties(county_names=counties)

        self.assertNotEqual(result, [])

        self.scy.previous_county_details_version_num = None

        _, result = self.scy.get_detailed_results_for_participating_counties()

        self.assertNotEqual(result, [])

        self.assertTrue(all(x["county_name"] not in counties for x in result))

    def test_get_detailed_results_for_participating_counties_skips_if_no_version_update(
        self,
    ):
        _, result = self.scy.get_detailed_results_for_participating_counties()

        self.assertNotEqual(result, [])

        _, result = self.scy.get_detailed_results_for_participating_counties()

        self.assertEqual(result, [])

        _, result = self.scy.get_detailed_results_for_participating_counties(force_update=True)

        self.assertNotEqual(result, [])

    def test_get_detailed_results_for_participating_counties_skips_if_no_county_version_update(
        self,
    ):
        _, result = self.scy.get_detailed_results_for_participating_counties()

        self.assertNotEqual(result, [])

        self.scy.previous_county_details_version_num = None

        _, result = self.scy.get_detailed_results_for_participating_counties()

        self.assertEqual(result, [])

    def test_get_detailed_results_for_participating_counties_repeats_failed_counties(
        self,
    ):
        _, result = self.scy.get_detailed_results_for_participating_counties()

        self.assertNotEqual(result, [])

        self.scy.previous_county_details_version_num = None
        self.scy.previously_fetched_counties.remove("Barrow")

        _, result = self.scy.get_detailed_results_for_participating_counties()

        self.assertNotEqual(result, [])

    def _mock_responses(self, m: requests_mock.Mocker):
        mock_current_version_url = scytl.CURRENT_VERSION_URL_TEMPLATE.format(
            administrator=TEST_STATE, election_id=TEST_ELECTION_ID
        )

        m.get(mock_current_version_url, text=TEST_VERSION_NUM)

        mock_election_settings_url = scytl.ELECTION_SETTINGS_JSON_URL_TEMPLATE.format(
            state=TEST_STATE, election_id=TEST_ELECTION_ID, version_num=TEST_VERSION_NUM
        )

        with open(f"{_DIR}/GA_114729_296262_county_election_settings.json", "r") as details_file:
            m.get(mock_election_settings_url, text=details_file.read())

        for file in os.listdir(f"{_DIR}/mock_responses"):
            with open(f"{_DIR}/mock_responses/{file}", "rb") as details_file:
                file_url = f"https://results.enr.clarityelections.com/{file}".replace("_", "/")
                m.get(file_url, content=details_file.read())

        mock_summary_csv_url = scytl.SUMMARY_CSV_ZIP_URL_TEMPLATE.format(
            administrator=TEST_STATE,
            election_id=TEST_ELECTION_ID,
            version_num=TEST_VERSION_NUM,
        )

        with open(f"{_DIR}/114729_summary.zip", "rb") as summary:
            m.get(mock_summary_csv_url, content=summary.read())

        mock_detail_xml_url = scytl.DETAIL_XML_ZIP_URL_TEMPLATE.format(
            administrator=TEST_STATE,
            election_id=TEST_ELECTION_ID,
            version_num=TEST_VERSION_NUM,
        )

        with open(f"{_DIR}/114729_detailxml.zip", "rb") as detailxml:
            m.get(mock_detail_xml_url, content=detailxml.read())

        m.start()
