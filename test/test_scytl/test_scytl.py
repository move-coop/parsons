import csv
import os
import unittest
from pathlib import Path

import requests_mock

from parsons.scytl import Scytl, scytl

TEST_STATE = "GA"
TEST_ELECTION_ID = "114729"
TEST_VERSION_NUM = "296262"

_DIR = Path(__file__).parent


class TestScytl(unittest.TestCase):
    def setUp(self):
        self.scy = Scytl(TEST_STATE, TEST_ELECTION_ID)

        self.requests_mock = requests_mock.Mocker()

        self._mock_responses(self.requests_mock)

    def tearDown(self) -> None:
        self.requests_mock.stop()

    def test_get_summary_results_succeeds(self):
        result = self.scy.get_summary_results()

        with (_DIR / "114729_summary_expected.csv").open(mode="r") as expected:
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

        with (_DIR / "114729_county_expected.csv").open(mode="r") as expected:
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

        with (_DIR / "114729_precinct_expected.csv").open(mode="r") as expected:
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

        with (_DIR / "114729_precinct_expected.csv").open(mode="r") as expected:
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

        m.get(
            mock_election_settings_url,
            text=(_DIR / "GA_114729_296262_county_election_settings.json").read_text(),
        )

        for file in os.listdir(_DIR / "mock_responses"):
            file_url = f"https://results.enr.clarityelections.com/{file}".replace("_", "/")
            m.get(file_url, content=Path(_DIR / "mock_responses" / file).read_bytes())

        mock_summary_csv_url = scytl.SUMMARY_CSV_ZIP_URL_TEMPLATE.format(
            administrator=TEST_STATE,
            election_id=TEST_ELECTION_ID,
            version_num=TEST_VERSION_NUM,
        )

        m.get(mock_summary_csv_url, content=(_DIR / "114729_summary.zip").read_bytes())

        mock_detail_xml_url = scytl.DETAIL_XML_ZIP_URL_TEMPLATE.format(
            administrator=TEST_STATE,
            election_id=TEST_ELECTION_ID,
            version_num=TEST_VERSION_NUM,
        )

        m.get(mock_detail_xml_url, content=(_DIR / "114729_detailxml.zip").read_bytes())

        m.start()
