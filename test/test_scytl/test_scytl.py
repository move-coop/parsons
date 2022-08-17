import unittest, os, requests_mock, csv
from parsons.scytl import scytl
from parsons import Table

TEST_STATE = 'GA'
TEST_ELECTION_ID = '114729'
TEST_VERSION_NUM = '296262'

_dir = os.path.dirname(__file__)


class TestScytl(unittest.TestCase):

    def setUp(self):
        self.scy = scytl.Scytl(TEST_STATE, TEST_ELECTION_ID)
    

    @requests_mock.Mocker()
    def test_statewide_results_succeeds(self, m: requests_mock.Mocker):
        self._mock_version_num(m)

        mock_url = scytl.statewide_summary_csv_url.format(
            state=TEST_STATE, election_id=TEST_ELECTION_ID, version_num=TEST_VERSION_NUM
        )

        with open(f'{_dir}/114729_summary.zip', 'r') as summary:
            m.get(mock_url, body=summary)

        result = self.scy.get_statewide_results()

        with open(f'{_dir}/114729_summary_expected.csv', 'r') as expected:
            expectedResult = list(csv.DictReader(expected, delimiter=","))
            self.assertListEqual(expectedResult, result)


    @requests_mock.Mocker()
    def test_statewide_results_skips_if_no_version_update(self, m: requests_mock.Mocker):
        self._mock_version_num(m)

        self.scy.previous_statewide_version_num = TEST_VERSION_NUM

        result = self.scy.get_statewide_results()

        assert result == None

    @requests_mock.Mocker()
    def test_county_level_results_succeeds(self, m: requests_mock.Mocker):
        self._mock_version_num(m)

        mock_url = scytl.statewide_detail_xml_url.format(
            state=TEST_STATE, election_id=TEST_ELECTION_ID, version_num=TEST_VERSION_NUM
        )

        with open(f'{_dir}/114729_detailxml.zip', 'r') as summary:
            m.get(mock_url, body=summary)

        result = self.scy.get_county_level_results()

        with open(f'{_dir}/114729_county_expected.csv', 'r') as expected:
            expectedResult = list(csv.DictReader(expected, delimiter=","))

            for i in range(len(result)):
                expectedResultRow = expectedResult[i]

                expectedResultRow['recorded_votes'] = int(expectedResultRow['recorded_votes'])
                expectedResultRow['timestamp_last_updated'] = \
                    self.scy._parse_date_to_utc(expectedResultRow['timestamp_last_updated'])

                self.assertDictEqual(result[i], expectedResultRow)
    

    @requests_mock.Mocker()
    def test_county_level_results_skips_if_no_version_update(self, m: requests_mock.Mocker):
        self._mock_version_num(m)

        self.scy.previous_county_version_num = TEST_VERSION_NUM

        result = self.scy.get_county_level_results()
        
        assert result == None

    
    @requests_mock.Mocker()
    def test_precinct_level_results_skips_if_no_version_update(self, m: requests_mock.Mocker):
        self._mock_version_num(m)

        self.scy.previous_precinct_version_num = TEST_VERSION_NUM

        result = self.scy.get_precinct_level_results()
        
        assert result == None


    def _mock_version_num(self, m: requests_mock.Mocker):
        mock_url = scytl.get_version_url.format(
            state=TEST_STATE, election_id=TEST_ELECTION_ID, county_name=''
        )

        m.get(mock_url, text=TEST_VERSION_NUM)

