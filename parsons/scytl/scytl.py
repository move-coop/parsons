import zipfile
import csv
import requests
import xml.etree.ElementTree as ET
import typing as t
from datetime import datetime
from dateutil.parser import parse as parsedate
from pytz import timezone
from io import BytesIO, StringIO
from dataclasses import dataclass

CLARITY_URL = "https://results.enr.clarityelections.com/"

CURRENT_VERSION_URL_TEMPLATE = CLARITY_URL + "{administrator}/{election_id}/current_ver.txt"
SUMMARY_CSV_ZIP_URL_TEMPLATE = (
    CLARITY_URL + "{administrator}/{election_id}/{version_num}/reports/summary.zip"
)
DETAIL_XML_ZIP_URL_TEMPLATE = (
    CLARITY_URL + "{administrator}/{election_id}/{version_num}/reports/detailxml.zip"
)
COUNTY_DETAIL_XML_ZIP_URL_TEMPLATE = (
    CLARITY_URL
    + "{state}/{county_name}/{county_election_id}/{county_version_num}/reports/detailxml.zip"
)
ELECTION_SETTINGS_JSON_URL_TEMPLATE = (
    CLARITY_URL + "{state}/{election_id}/{version_num}/json/en/electionsettings.json"
)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) "
    + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}

TZ_INFO = {
    "EST": "UTC-5",
    "EDT": "UTC-4",
    "CST": "UTC-6",
    "CDT": "UTC-5",
    "MST": "UTC-7",
    "MDT": "UTC-6",
    "PST": "UTC-8",
    "PDT": "UTC-7",
    "AKST": "UTC-9",
    "AKDT": "UTC-8",
    "HST": "UTC-10",
    "HDT": "UTC-9",
}


@dataclass
class CountyDetails:
    """
    A class for keeping track of County election details.

    A dataclass is decorator that adds special functions including an
    automatic __init__ function. See more here: https://docs.python.org/3/library/dataclasses.html
    """

    state: str
    county_name: str
    county_election_id: str
    county_version_num: str
    county_update_date: datetime = None


class Scytl:
    """
    Instantiate a Scytl connector.

    `Args:`:
        state: str
            The two letter code of the state the publishing election results.
            ex: GA
        election_id: str
            The numeric identifier for the election found in the url of the election's website.
            ex: "114729"
        county: str (optional)
            The name of the county publishing the results.
            ex: Clarke
    """

    def __init__(self, state: str, election_id: str, county=""):
        self.state = state
        self.county = county.replace(" ", "_")

        self.administrator = f"{self.state}/{self.county}" if self.county else self.state
        self.election_id = election_id

        self.previous_summary_version_num = None
        self.previous_details_version_num = None
        self.previous_county_details_version_num = None
        self.previous_county_details_list = None
        self.previously_fetched_counties = set([])

    def _parse_date_to_utc(self, input_dt: str) -> datetime:
        """
        Parse datetime string as datetime in UTC

        `Args`:
            input_dt: str
                The datetime string to be parsed
        `Returns`:
            datetime | None
        """

        if input_dt is None:
            return

        temp = parsedate(input_dt, tzinfos=TZ_INFO)
        temp = temp.astimezone(timezone("UTC"))

        return temp

    def _get_version(self, administrator: str, election_id: str) -> str:
        """
        Fetch the latest version of the election results from the Clarity site

        `Args`:
            administrator: str
                The url code for the election administrator, either the two-letter
                state code or the state code and the county, separated by a slash
            election_id: str
                The election id for the given election as a string
        `Returns`:
            str
            The version id as a string
        """

        config_version_url = CURRENT_VERSION_URL_TEMPLATE.format(
            administrator=administrator, election_id=election_id
        )

        res = requests.get(config_version_url, headers=BROWSER_HEADERS)

        return res.text

    def _parse_file_from_zip_url(self, zipfile_url: str, file_name: str) -> bytes:
        """
        Fetch a zip file from the given url and unzip to a byte array

        `Args`:
            zipfile_url: str
                The url where the zip file can be found
            election_id: str
                The expected name of the file in the zipfile to read
        `Returns`:
            bytes
            The unzipped file as bytes
        """

        with BytesIO() as zipdata:
            with requests.get(zipfile_url, headers=BROWSER_HEADERS) as res:
                zipdata.write(res.content)
                zipdata.flush()

            zf = zipfile.ZipFile(zipdata)

            with zf.open(file_name) as input:
                return input.read()

    def _get_latest_counties_scytl_info(
        self, state: str, election_id: str, version_num: str
    ) -> t.Dict[str, CountyDetails]:
        """
        Fetch the settings JSON file for the election and parse the county details
        for participating counties in a state election.

        `Args`:
            state: str
                The two-letter state code for the state
            election_id: str
                The election ID for the given election
            version_num: str
                The latest version ID of the election as a string
        `Returns`:
            dict[str, CountyDetails]
            A dictionary mapping county names to their sub-election information
        """

        county_dict = {}

        config_settings_json_url = ELECTION_SETTINGS_JSON_URL_TEMPLATE.format(
            state=state, election_id=election_id, version_num=version_num
        )

        settings_json_res = requests.get(config_settings_json_url, headers=BROWSER_HEADERS)
        settings_json = settings_json_res.json()

        participating_counties = settings_json["settings"]["electiondetails"][
            "participatingcounties"
        ]

        for county_row in participating_counties:
            county_info = county_row.split("|")
            source_county_name = county_info[0]
            county_election_id = county_info[1]
            county_version_num = county_info[2]
            county_update_date = self._parse_date_to_utc(county_info[3])

            county_details = CountyDetails(
                state,
                source_county_name,
                county_election_id,
                county_version_num,
                county_update_date,
            )

            county_dict[source_county_name] = county_details

        return county_dict

    def _parse_county_xml_data_to_precincts(
        self, county_data: bytes, county_details: CountyDetails
    ) -> t.List[t.Dict]:
        """
        Parse a detail XML file for a county into a list of election
        results by precinct and vote method.

        `Args`:
            county_data: bytes
                The detail XML file for a county as bytes
            county_details: str
                The details class for the county, including name,
                id, and last updated datetime
        `Returns`:
            list[dict]
            The list of election results by precinct and vote method in the file.
        """

        tree = ET.fromstring(county_data)

        precinct_dict = {}
        precinct_votes = []

        root = tree

        for child in root:

            if child.tag == "VoterTurnout":
                precincts = child[0]

                for precinct in precincts:
                    data = precinct.attrib
                    name = data.get("name")

                    precinct_info = {
                        "total_voters": data.get("totalVoters"),
                        "ballots_cast": data.get("ballotsCast"),
                        "voter_turnout": data.get("voterTurnout"),
                        "percent_reporting": data.get("percentReporting"),
                    }

                    precinct_dict[name] = precinct_info

            if child.tag == "Contest":

                office = child.attrib["text"]

                for choice in child:
                    cand_votes = {}

                    if choice.tag == "VoteType":
                        continue

                    source_cand_data = choice.attrib
                    cand_name = source_cand_data.get("text")
                    cand_party = source_cand_data.get("party")

                    for vote_type in choice:
                        vote_type_label = vote_type.attrib["name"]

                        for precinct in vote_type:
                            precinct_name = precinct.attrib["name"]
                            cand_votes[precinct_name] = int(precinct.attrib["votes"])

                            precinct_turnout = precinct_dict.get(precinct_name, {})

                            result = {
                                "state": county_details.state,
                                "county_name": county_details.county_name,
                                "county_id": county_details.county_election_id,
                                "office": office,
                                "ballots_cast": precinct_turnout.get("ballots_cast"),
                                "reg_voters": precinct_turnout.get("total_voters"),
                                "vote_method": vote_type_label,
                                "candidate_name": cand_name,
                                "candidate_party": cand_party,
                                "precinct_name": precinct_name,
                                "recorded_votes": cand_votes[precinct_name],
                                "voter_turnout": precinct_turnout.get("voter_turnout"),
                                "percent_reporting": precinct_turnout.get("percent_reporting"),
                                "timestamp_last_updated": county_details.county_update_date,
                            }

                            precinct_votes.append(result)

        return precinct_votes

    def _parse_state_xml_data_to_counties(self, state_data: bytes, state: str) -> t.List[t.Dict]:
        """
        Parse a detail XML file for a state into a list of election
        results by county and vote method.

        `Args`:
            state_data: bytes
                The detail XML file for a state as bytes
            state: str
                The two-letter state code for the state associated with the file
        `Returns`:
            list[dict]
            The list of election results by state and vote method in the file.
        """

        root = ET.fromstring(state_data)

        county_dict = {}
        county_votes = []

        timestamp = None

        for child in root:

            if child.tag == "Timestamp":  # <Timestamp>1/5/2021 3:22:30 PM EST</Timestamp>
                timestamp = self._parse_date_to_utc(child.text)

            if child.tag == "ElectionVoterTurnout":
                counties = child[0]

                for county in counties:
                    data = county.attrib
                    name = data["name"]

                    county_dict[name] = data

            if child.tag == "Contest":

                office = child.attrib["text"]

                for choice in child:
                    cand_votes = {}

                    if choice.tag == "ParticipatingCounties":
                        continue

                    source_cand_data = choice.attrib
                    cand_name = source_cand_data.get("text")
                    cand_party = source_cand_data.get("party")

                    for vote_type in choice:
                        vote_type_label = vote_type.attrib["name"]

                        for county in vote_type:
                            county_name = county.attrib["name"]
                            cand_votes[county_name] = int(county.attrib["votes"])

                            county_turnout = county_dict.get(county_name, {})

                            result = {
                                "state": state,
                                "county_name": county_name,
                                "office": office,
                                "ballots_cast": county_turnout.get("ballotsCast"),
                                "reg_voters": county_turnout.get("totalVoters"),
                                "precincts_reporting": county_turnout.get("precinctsReported"),
                                "total_precincts": county_turnout.get("precinctsParticipating"),
                                "vote_method": vote_type_label,
                                "candidate_name": cand_name,
                                "candidate_party": cand_party,
                                "recorded_votes": cand_votes[county_name],
                                "timestamp_last_updated": timestamp,
                            }

                            county_votes.append(result)

        return county_votes

    def _fetch_and_parse_summary_results(
        self, administrator: str, election_id: str, version_num: str, county=""
    ) -> t.List[t.Dict]:
        """
        Fetches the summary results CSV file from the Scytl site and parses it
        into a list of election results by candidate.

        `Args`:
            administrator: str
                The url code for the election administrator, either the two-letter
                state code or the state code and the county, separated by a slash
            election_id: str
                The election id for the given election as a string
            version_num: str
                The latest version ID of the election as a string
            county: str
                The name of the county associated with the summary file
        `Returns`:
            list[dict]
            The list of election results by candidate.
        """

        summary_csv_zip_url = SUMMARY_CSV_ZIP_URL_TEMPLATE.format(
            administrator=administrator,
            election_id=election_id,
            version_num=version_num,
        )

        zip_bytes = self._parse_file_from_zip_url(summary_csv_zip_url, "summary.csv")

        string_buffer = StringIO(zip_bytes.decode("latin-1"))
        csv_data = csv.DictReader(string_buffer, delimiter=",")

        data = [
            {
                "state": self.state,
                "county_name": county or self.county,
                "office": x.get("contest name"),
                "ballots_cast": x.get("ballots cast"),
                "reg_voters": x.get("registered voters"),
                "counties_reporting": x.get("num Area rptg"),
                "total_counties": x.get("num Area total"),
                "precincts_reporting": x.get("num Precinct rptg"),
                "total_precincts": x.get("num Precinct total"),
                "candidate_name": x.get("choice name"),
                "candidate_party": x.get("party name"),
                "recorded_votes": x.get("total votes"),
            }
            for x in csv_data
        ]

        return data

    def get_summary_results(self, force_update=False) -> t.List[t.Dict]:
        """
        Fetch the latest summary results for the given election, across all contests.

        Please note that all electoral entities administer their elections differently,
            so not all values will be populated if the entity doesn't provide them.

        `Args:`
            force_update: bool
                If this is False, the connector will check to see if the current version
                    matches the previously fetched version of the results.
                    If the version has not been changed, no results will be fetched or returned.
                Default: false
        `Returns:`
            list[dict]
            The list should contain entries for each candidate in each office.
            Each row will contain the following:
            - state
            - county_name (if applicable)
            - office
            - ballots_cast (in the contest)
            - reg_voters (eligible for the contest)
            - counties_reporting
            - total_counties
            - precincts_reporting
            - total_precincts
            - candidate_name
            - candidate_party (many administrators do not use this feature
                and instead include the party in the candidate name)
            - recorded_votes (votes cast for the candidate)
        """

        version_num = self._get_version(self.administrator, self.election_id)

        if not force_update and version_num == self.previous_summary_version_num:
            return

        data = self._fetch_and_parse_summary_results(
            self.administrator, self.election_id, version_num
        )

        self.previous_summary_version_num = version_num

        return data

    def get_detailed_results(self, force_update=False) -> t.List[t.Dict]:
        """
        Fetch the latest detailed results by geography for the given election, across all contests.

        Please note that all electoral entities administer their elections differently,
            so not all values will be populated if the entity doesn't provide them.

        `Args:`
            force_update: bool
                If this is False, the connector will check to see if the current version
                    matches the previously fetched version of the results.
                    If the version has not been changed, no results will be fetched or returned.
                Default: false
        `Returns:`
            list[dict]
            The list should contain entries for each candidate in each office,
                per vote method and per county.

            If fetching for a state, results will look like:
            - state
            - county_name
            - office
            - ballots_cast
            - reg_voters
            - precincts_reporting
            - total_precincts
            - vote_method (note: some administrators choose to differentiate
                results by vote method, while others do not)
            - candidate_name
            - candidate_party (many administrators do not use this
                feature and instead include the party in the candidate name)
            - recorded_votes (votes cast for the candidate
                with this vote method in this county)
            - timestamp_last_updated

            If fetching for a county, results will look like:
            - state
            - county_name
            - county_id
            - office
            - ballots_cast
            - reg_voters
            - vote_method (note: some administrators choose to
                differentiate results by vote method, while others do not)
            - candidate_name
            - candidate_party (many administrators do not use this
                feature and instead include the party in the candidate name)
            - precinct_name
            - recorded_votes (votes cast for the candidate
                with this vote method in this county)
            - voter_turnout
            - percent_reporting
            - timestamp_last_updated
        """

        version_num = self._get_version(self.administrator, self.election_id)

        if not force_update and version_num == self.previous_details_version_num:
            return

        detail_xml_url = DETAIL_XML_ZIP_URL_TEMPLATE.format(
            administrator=self.administrator,
            election_id=self.election_id,
            version_num=version_num,
        )

        parsed_data = []

        county_data = self._parse_file_from_zip_url(detail_xml_url, "detail.xml")

        if self.county:
            county_details = CountyDetails(self.state, self.county, self.election_id, version_num)

            parsed_data = self._parse_county_xml_data_to_precincts(county_data, county_details)
        else:
            parsed_data = self._parse_state_xml_data_to_counties(county_data, self.state)

        self.previous_details_version_num = version_num

        return parsed_data

    def get_detailed_results_for_participating_counties(
        self, county_names: t.List[str] = None, force_update=False
    ) -> t.Tuple[t.List[str], t.List[t.Dict]]:
        """
        Fetch the latest detailed results for the given election for all participating counties
            with detailed results, across all contests.

        Some counties may not have detailed results. If so, this will attempt
            to fetch the summary results for that county. If no results exist for either,
            the county name will be appended to the missing_counties list.

        After the first fetch, only the counties with updates will be returned,
            previous results will not be included.

        Please note that all electoral entities administer their elections differently,
            so not all values will be populated if the entity doesn't provide them.

        `Args:`
            county_names: list[str]
                The list of counties to get precinct-level results for.
                Default: None (get all counties)
            force_update: bool
                If this is False, the connector will check to see if the current
                    version matches the previously fetched version of the results.
                    If the version has not been changed, no results will be fetched or returned.
                Default: false

        `Returns:`
            list[str]
            The list of county names that could not be fetched

            list[dict]
            The list should contain entries for each candidate in
                each office, per vote method, county, and precinct.
            Each row will contain the following:
            - state
            - county_name
            - county_id
            - office
            - ballots_cast
            - reg_voters
            - vote_method (note: some administrators choose to differentiate
                results by vote method, while others do not)
            - candidate_name
            - candidate_party (many administrators do not use this feature
                and instead include the party in the candidate name)
            - precinct_name
            - recorded_votes (votes cast for the candidate with this vote method in this county)
            - voter_turnout
            - percent_reporting
            - timestamp_last_updated
        """

        version_num = self._get_version(self.administrator, self.election_id)

        if not force_update and version_num == self.previous_county_details_version_num:
            return [], []

        county_details_list = self._get_latest_counties_scytl_info(
            self.state, self.election_id, version_num
        )

        parsed_data = []
        fetched_counties = []
        missing_counties = []

        for county_name, county_details in county_details_list.items():
            if county_names and county_name not in county_names:
                continue

            if (
                not force_update
                and county_name in self.previously_fetched_counties
                and self.previous_county_details_list
                and county_details.county_update_date
                <= self.previous_county_details_list[county_name].county_update_date
            ):
                continue

            detail_xml_url = COUNTY_DETAIL_XML_ZIP_URL_TEMPLATE.format(
                state=county_details.state,
                county_name=county_details.county_name,
                county_election_id=county_details.county_election_id,
                county_version_num=county_details.county_version_num,
            )

            try:
                county_data = self._parse_file_from_zip_url(detail_xml_url, "detail.xml")

            except requests.exceptions.RequestException:
                try:
                    summary_data = self._fetch_and_parse_summary_results(
                        f"{self.state}/{county_name}",
                        county_details.county_election_id,
                        county_details.county_version_num,
                        county_name,
                    )

                except requests.exceptions.RequestException:
                    missing_counties.append(county_name)

                else:
                    if len(summary_data) > 0:
                        parsed_data += summary_data

            else:
                parsed_data += self._parse_county_xml_data_to_precincts(county_data, county_details)

                fetched_counties.append(county_name)

        self.previous_county_details_version_num = version_num
        self.previous_county_details_list = county_details_list
        self.previously_fetched_counties = set(fetched_counties)

        return missing_counties, parsed_data
