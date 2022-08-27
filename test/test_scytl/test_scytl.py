import unittest, os, requests_mock, csv
from parsons.scytl import Scytl, scytl

TEST_STATE = 'GA'
TEST_ELECTION_ID = '114729'
TEST_VERSION_NUM = '296262'

_dir = os.path.dirname(__file__)

class TestScytl(unittest.TestCase):

    @requests_mock.Mocker()
    def test_get_summary_results_succeeds(self, m):
        self._mock_responses(m)

        mock_url = scytl.summary_csv_url_template.format(
            administrator=TEST_STATE, election_id=TEST_ELECTION_ID, version_num=TEST_VERSION_NUM
        )

        with open(f'{_dir}/114729_summary.zip', 'r') as summary:
            m.get(mock_url, body=summary)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)
        result = scy.get_summary_results()

        with open(f'{_dir}/114729_summary_expected.csv', 'r') as expected:
            expectedResult = list(csv.DictReader(expected, delimiter=",", ))

            for i, row in enumerate(result):
                expectedResultRow = expectedResult[i]

                expectedResultRow['counties_reporting'] = expectedResultRow['counties_reporting'] or None
                expectedResultRow['total_counties'] = expectedResultRow['total_counties'] or None

                self.assertDictEqual(row, expectedResultRow)


    @requests_mock.Mocker()
    def test_get_summary_results_skips_if_no_version_update(self, m: requests_mock.Mocker):
        self._mock_responses(m)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)

        result = scy.get_summary_results()

        assert result != None

        result = scy.get_summary_results()

        assert result == None

        result = scy.get_summary_results(True)

        assert result != None


    @requests_mock.Mocker()
    def test_get_detailed_results_succeeds(self, m: requests_mock.Mocker):
        self._mock_responses(m)

        mock_url = scytl.detail_xml_url_template.format(
            administrator=TEST_STATE, election_id=TEST_ELECTION_ID, version_num=TEST_VERSION_NUM
        )

        with open(f'{_dir}/114729_detailxml.zip', 'r') as detailxml:
            m.get(mock_url, body=detailxml)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)

        result = scy.get_detailed_results()

        with open(f'{_dir}/114729_county_expected.csv', 'r') as expected:
            expectedResult = list(csv.DictReader(expected, delimiter=","))

            for i in range(len(result)):
                expectedResultRow = expectedResult[i]

                expectedResultRow['recorded_votes'] = int(expectedResultRow['recorded_votes'])
                expectedResultRow['timestamp_last_updated'] = \
                    scy._parse_date_to_utc(expectedResultRow['timestamp_last_updated'])

                self.assertDictEqual(result[i], expectedResultRow)
    

    @requests_mock.Mocker()
    def test_get_detailed_results_skips_if_no_version_update(self, m: requests_mock.Mocker):
        self._mock_responses(m)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)
        
        result = scy.get_detailed_results()

        assert result != None

        result = scy.get_detailed_results()
        
        assert result == None

        result = scy.get_detailed_results(True)

        assert result != None


    @requests_mock.Mocker()
    def test_get_detailed_results_for_participating_counties_succeeds(self, m: requests_mock.Mocker):
        self._mock_responses(m)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)
        
        _, result = scy.get_detailed_results_for_participating_counties()

        with open(f'{_dir}/114729_precinct_expected.csv', 'r') as expected:
            expectedResult = list(csv.DictReader(expected, delimiter=","))

            for i in range(len(result)):
                expectedResultRow = expectedResult[i]

                expectedResultRow['recorded_votes'] = int(expectedResultRow['recorded_votes'])
                expectedResultRow['timestamp_last_updated'] = \
                    scy._parse_date_to_utc(expectedResultRow['timestamp_last_updated'])

                self.assertDictEqual(result[i], expectedResultRow)

    @requests_mock.Mocker()
    def test_get_detailed_results_for_participating_counties_succeeds_for_two_counties(self, m: requests_mock.Mocker):
        self._mock_responses(m)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)

        counties = ['Barrow', 'Clarke']
        
        _, result = scy.get_detailed_results_for_participating_counties(county_names=counties)

        with open(f'{_dir}/114729_precinct_expected.csv', 'r') as expected:
            expectedResult = csv.DictReader(expected, delimiter=",")

            filteredExpectedResults = list(filter(lambda x: x['county_name'] in counties, expectedResult))

            for i, row in enumerate(result):
                expectedResultRow = filteredExpectedResults[i]

                expectedResultRow['recorded_votes'] = int(expectedResultRow['recorded_votes'])
                expectedResultRow['timestamp_last_updated'] = \
                    scy._parse_date_to_utc(expectedResultRow['timestamp_last_updated'])

                self.assertDictEqual(row, expectedResultRow)


    @requests_mock.Mocker()
    def test_get_detailed_results_for_participating_counties_missing_counties_update(self, m: requests_mock.Mocker):
        self._mock_responses(m)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)

        counties = ['Barrow', 'Clarke']
        
        _, result = scy.get_detailed_results_for_participating_counties(county_names=counties)

        assert result != []

        self._mock_responses(m)

        scy.previous_county_details_version_num = None

        _, result = scy.get_detailed_results_for_participating_counties()

        assert result != []

        self.assertTrue(all(x['county_name'] not in counties for x in result))


    @requests_mock.Mocker()
    def test_get_detailed_results_for_participating_counties_skips_if_no_version_update(self, m: requests_mock.Mocker):
        self._mock_responses(m)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)

        _, result = scy.get_detailed_results_for_participating_counties()

        assert result != []

        _, result = scy.get_detailed_results_for_participating_counties()

        assert result == []

        _, result = scy.get_detailed_results_for_participating_counties(force_update = True)

        assert result != []


    @requests_mock.Mocker()
    def test_get_detailed_results_for_participating_counties_skips_if_no_county_version_update(self, m: requests_mock.Mocker):
        self._mock_responses(m)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)
        
        _, result = scy.get_detailed_results_for_participating_counties()

        assert result != []

        scy.previous_county_details_version_num = None

        _, result = scy.get_detailed_results_for_participating_counties()

        assert result == []


    @requests_mock.Mocker()
    def test_get_detailed_results_for_participating_counties_repeats_failed_counties(self, m: requests_mock.Mocker):
        self._mock_responses(m)

        scy = Scytl(TEST_STATE, TEST_ELECTION_ID)
        
        _, result = scy.get_detailed_results_for_participating_counties()

        assert result != []

        scy.previous_county_details_version_num = None
        scy.previously_fetched_counties.remove('Barrow')

        _, result = scy.get_detailed_results_for_participating_counties()

        assert result != []


    def _mock_responses(self, m: requests_mock.Mocker):
        mock_url = scytl.get_version_url.format(
            administrator=TEST_STATE, election_id=TEST_ELECTION_ID
        )

        m.get(mock_url, text=TEST_VERSION_NUM)

        mock_detail_url = scytl.detail_settings_json_url_template.format(
            state=TEST_STATE, election_id=TEST_ELECTION_ID, version_num=TEST_VERSION_NUM
        )

        with open(f'{_dir}/114729_county_election_settings.json', 'r') as f:
            m.get(mock_detail_url, text=f.read())

        for file in os.listdir(f'{_dir}/county_precinct_details'):
            with open(f'{_dir}/county_precinct_details/{file}') as f:
                fn = f'https://results.enr.clarityelections.com//{file}'.replace('_', '/')
                m.get(fn, body=f)

