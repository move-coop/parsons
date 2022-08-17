import urllib, zipfile, csv, requests
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil.parser import parse as parsedate
from pytz import timezone
from io import BytesIO, StringIO

get_version_url = 'https://results.enr.clarityelections.com/{state}/{election_id}/current_ver.txt'
statewide_summary_csv_url = 'https://results.enr.clarityelections.com//{state}//{election_id}/{version_num}/reports/summary.zip'
statewide_detail_xml_url = 'https://results.enr.clarityelections.com//{state}/{election_id}/{version_num}/reports/detailxml.zip'
county_detail_xml_url = 'https://results.enr.clarityelections.com//{state}/{county_name}/{county_election_id}/{county_version_num}/reports/detailxml.zip'
state_detail_settings_json_url = 'https://results.enr.clarityelections.com//{state}/{election_id}/{version_num}/json/en/electionsettings.json'

tzinfos = {
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


class CountyDetails:
    def __init__(self, state: str, county_name: str, county_election_id: str, county_version_num: str, county_update_date: datetime):
        self.state = state
        self.county_name = county_name
        self.county_election_id = county_election_id
        self.county_version_num = county_version_num
        self.county_update_date = county_update_date


class Scytl(object):
    """
    Instantiate a Scytl connector.

    `Args:`:
        state: str
            The short name of the government entity publishing election results, which can be found in the URL of the election's website. 
            ex: "GA" or "TX/Dallas"
        election_id: str
            The numeric identifier for the election found in the url of the election's website.
            ex: "114729"
    """

    def __init__(self, state: str, election_id: str):
        self.state = state
        self.election_id = election_id

        self.previous_statewide_version_num = None
        self.previous_county_version_num = None
        self.previous_precinct_version_num = None
        self.previous_county_details_list = None
        self.previously_fetched_counties = set([])


    def _parse_date_to_utc(self, input_dt):
        if input_dt == None:
            return None

        try:
            temp = parsedate(input_dt, tzinfos=tzinfos)
            temp = temp.astimezone(timezone('UTC'))
        except:
            print(input_dt)
            raise

        return temp


    def _get_version(self, state, election_id, county_name = ''):
        config_version_url = get_version_url.format(state= state, county_name=county_name, election_id=election_id)
                
        res = requests.get(config_version_url)

        return res.text


    def _parse_file_from_zip_url(self, detail_xml_url, file_name) -> bytes:
        try:
            zipdata = BytesIO()

            with urllib.request.urlopen(detail_xml_url) as remote:
                data = remote.read()
                zipdata.write(data)

            zf = zipfile.ZipFile(zipdata)
            
            with zf.open(file_name) as input:
                return input.read()

        except urllib.error.HTTPError as e:
            print ('HTTPError: {} {}'.format(e.code, detail_xml_url))


    def _get_latest_counties_scytl_info(self, state, election_id, version) -> dict[str, CountyDetails]:

        county_dict = {}
                
        config_state_detail_url = state_detail_settings_json_url.format(
            state=state, election_id=election_id, version_num=version
        )

        state_detail_res = requests.get(config_state_detail_url)
        state_detail = state_detail_res.json()
            
        participating_counties = state_detail['settings']['electiondetails']['participatingcounties']

        for county_row in participating_counties:
            county_info = county_row.split('|')
            source_county_name = county_info[0]
            county_election_id = county_info[1]
            county_version_num = county_info[2]
            county_update_date = self._parse_date_to_utc(county_info[3])

            county_details = CountyDetails(
                state, source_county_name, county_election_id, county_version_num, county_update_date
            )
                    
            county_dict[source_county_name] = county_details

        return county_dict

        
    def _parse_county_xml_data_to_precincts(self, county_details: CountyDetails, county_data, timestamp):
        tree = ET.fromstring(county_data)

        precinct_dict = {}
        precinct_votes = []    

        root = tree

        for child in root:

            if child.tag == 'VoterTurnout':
                precincts = child[0]
            
                for precinct in precincts: 
                    data = (precinct.attrib)
                    name = data.get('name')
                    
                    precinct_info = {'name': name,
                                    'total_voters': data.get('totalVoters'),
                                    'ballots_cast': data.get('ballotsCast'),
                                    'voter_turnout':  data.get('voterTurnout'),
                                    'percent_reporting':  data.get('percentReporting'),
                                    'precinct_complete': False}

                    precinct_dict[name] = precinct_info
                    
            if child.tag == 'Contest':

                office = child.attrib['text']

                for choice in child:
                    cand_votes = {}

                    if choice.tag == 'VoteType':
                        continue

                    source_cand_data = choice.attrib
                    cand_name = source_cand_data.get('text')
                    cand_party = source_cand_data.get('party')

                    for vote_type in choice:
                        vote_type_label = vote_type.attrib['name']
                                            
                        for precinct in vote_type:
                            precinct_name = precinct.attrib['name']    
                            cand_votes[precinct_name] = int(precinct.attrib['votes'])                    

                            result = {'state': county_details.state,
                                    'county_name': county_details.county_name,
                                    'county_id': county_details.county_election_id,
                                    'office': office, 
                                    'ballots_cast': precinct_dict[precinct_name]['ballots_cast'],
                                    'reg_voters': precinct_dict[precinct_name]['total_voters'],
                                    'vote_method': vote_type_label,
                                    'candidate_name': cand_name, 
                                    'candidate_party': cand_party, 
                                    'precinct_name': precinct_name, 
                                    'precinct_complete': precinct_dict[precinct_name]['precinct_complete'],
                                    'recorded_votes': cand_votes[precinct_name],
                                    'timestamp_last_updated': timestamp}

                            precinct_votes.append(result)
                            
        return precinct_votes


    def _parse_xml_for_county_data(self, file, state):
        """Parse xml based file to extract fields of interest"""

        root = ET.fromstring(file)

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

                office = child.attrib['text']

                for choice in child:
                    cand_votes = {}

                    if choice.tag == "ParticipatingCounties":
                        continue

                    source_cand_data = choice.attrib
                    cand_name = source_cand_data.get('text')
                    cand_party = source_cand_data.get('party')

                    for vote_type in choice:
                        vote_type_label = vote_type.attrib['name']

                        for county in vote_type:
                            county_name = county.attrib["name"]
                            cand_votes[county_name] = int(county.attrib["votes"])

                            county_turnout = county_dict.get(county_name) or {}

                            result = {'state': state,
                                    'county_name': county_name,
                                    'office': office, 
                                    'ballots_cast': county_turnout.get('ballotsCast'),
                                    'reg_voters': county_turnout.get('totalVoters'),
                                    'precincts_reporting': county_turnout.get('precinctsReported'),
                                    'total_precincts': county_turnout.get('precinctsParticipating'),
                                    'vote_method': vote_type_label,
                                    'candidate_name': cand_name, 
                                    'candidate_party': cand_party, 
                                    'recorded_votes': cand_votes[county_name],
                                    'timestamp_last_updated': timestamp}

                            county_votes.append(result)

        return county_votes


    def get_statewide_results(self, force_update = False):
        """
        Fetch the latest statewide results for the given election, across all contests.

        Please note that all electoral entities administer their elections differently, so not all values will be populated if the entity doesn't provide them.

        `Args:`
            force_update: bool
                If this is False, the connector will check to see if the current version matches the previously fetched version of the results. If the version has not been changed, no results will be fetched or returned.
                Default: false
        `Returns:`
            list[dict]
            The list should contain entries for each candidate in each office.
            Each row will contain the following:
            - state
            - office
            - ballots_cast (in the contest)
            - reg_voters (eligible for the contest)
            - counties_reporting
            - total_counties
            - precincts_reporting
            - total_precincts
            - candidate_name
            - candidate_party (many states do not use this feature and instead include the party in the candidate name)
            - recorded_votes (votes cast for the candidate)
        """

        version_num = self._get_version(self.state, self.election_id)

        if not force_update and version_num == self.previous_statewide_version_num:
            return
        
        summary_csv_zip_url = statewide_summary_csv_url.format(
            state=self.state, election_id=self.election_id, version_num=version_num
        )

        zip_bytes = self._parse_file_from_zip_url(summary_csv_zip_url, 'summary.csv')

        string_buffer = StringIO(zip_bytes.decode('latin-1'))
        csv_data = csv.DictReader(string_buffer, delimiter=",")

        data = list(
            map(lambda x: {
                    'state': self.state,
                    'office': x.get('contest name'), 
                    'ballots_cast': x.get('ballots cast'),
                    'reg_voters': x.get('registered voters'),
                    'counties_reporting': x.get('num Area rptg'),
                    'total_counties': x.get('num Area total'),
                    'precincts_reporting': x.get('num Precinct rptg'),
                    'total_precincts': x.get('num Precinct total'),
                    'candidate_name': x.get('choice name'), 
                    'candidate_party': x.get('party name'), 
                    'recorded_votes': x.get('total votes')
                }, 
                csv_data
            )
        )

        self.previous_statewide_version_num = version_num

        return data


    def get_county_level_results(self, force_update = False):
        """
        Fetch the latest statewide results by county for the given election, across all contests.

        Please note that all electoral entities administer their elections differently, so not all values will be populated if the entity doesn't provide them.

        `Args:`
            force_update: bool
                If this is False, the connector will check to see if the current version matches the previously fetched version of the results. If the version has not been changed, no results will be fetched or returned.
                Default: false
        `Returns:`
            list[dict]
            The list should contain entries for each candidate in each office, per vote method and per county.
            Each row will contain the following:
            - state
            - county_name
            - office
            - ballots_cast
            - reg_voters
            - precincts_reporting
            - total_precincts
            - vote_method (note: some states choose to differentiate results by vote method, while others do not)
            - candidate_name
            - candidate_party (many states do not use this feature and instead include the party in the candidate name)
            - recorded_votes (votes cast for the candidate with this vote method in this county)
            - timestamp_last_updated
        """
        
        version_num = self._get_version(self.state, self.election_id)

        if not force_update and version_num == self.previous_county_version_num:
            return
        
        detail_xml_url = statewide_detail_xml_url.format(
            state=self.state, election_id=self.election_id, version_num=version_num
        )

        parsed_data = []
        
        county_data = self._parse_file_from_zip_url(detail_xml_url, 'detail.xml')
                
        if county_data:
            parsed_data = self._parse_xml_for_county_data(county_data, self.state)

        self.previous_county_version_num = version_num
        
        return parsed_data


    def get_precinct_level_results(
        self,
        county_names: list[str] = None,
        force_update = False
    ):
        """
        Fetch the latest results by precinct for the given election, across all contests.

        Please note that all electoral entities administer their elections differently, so not all values will be populated if the entity doesn't provide them.

        `Args:`
            county_names: list[str]
                The list of counties to get precinct-level results for.
                Default: None (get all counties)
            force_update: bool
                If this is False, the connector will check to see if the current version matches the previously fetched version of the results. If the version has not been changed, no results will be fetched or returned.
                Default: false

        `Returns:`
            list[dict]
            The list should contain entries for each candidate in each office, per vote method, county, and precinct.
            Each row will contain the following:
            - state
            - county_name
            - county_id
            - office
            - ballots_cast
            - reg_voters
            - vote_method (note: some states choose to differentiate results by vote method, while others do not)
            - candidate_name
            - candidate_party (many states do not use this feature and instead include the party in the candidate name)
            - precinct_name
            - precinct_complete
            - recorded_votes (votes cast for the candidate with this vote method in this county)
            - timestamp_last_updated
        """

        version_num = self._get_version(self.state, self.election_id)

        if not force_update and version_num == self.previous_precinct_version_num:
            return []

        county_details_list = self._get_latest_counties_scytl_info(
            self.state, self.election_id, version_num
        )

        parsed_data = []
        fetched_counties = []

        for county_name, county_details in county_details_list.items():
            if county_names and not county_name in county_names:
                continue

            if not force_update and \
                county_name in self.previously_fetched_counties and \
                self.previous_county_details_list and \
                county_details.county_update_date <= self.previous_county_details_list[county_name].county_update_date:
                continue

            timestamp = county_details.county_update_date
            
            detail_xml_url = county_detail_xml_url.format(
                state=county_details.state,
                county_name=county_details.county_name,
                county_election_id=county_details.county_election_id,
                county_version_num=county_details.county_version_num
            )

            county_data = self._parse_file_from_zip_url(detail_xml_url, 'detail.xml')
                
            if county_data:
                parsed_data += self._parse_county_xml_data_to_precincts(county_details, county_data, timestamp)

                fetched_counties.append(county_name)
            

        self.previous_precinct_version_num = version_num
        self.previous_county_details_list = county_details_list
        self.previously_fetched_counties = set(fetched_counties)

        return parsed_data
