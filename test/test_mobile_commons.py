import unittest
import os
import requests_mock
from parsons.mobile_commons.mobile_commons import MobileCommons
from test.utils import validate_list


os.environ['MC_USER'] = 'SOME_USER'
os.environ['MC_PASS'] = 'SOME_PASS'


class TestMobileCommons(unittest.TestCase):

    def setUp(self):

        self.mc = MobileCommons(
            username=os.environ['MC_USER'],
            password=os.environ['MC_PASS'])

    def tearDown(self):

        pass

    def test_clean_dict(self):
        init = [{'@z': [{'@a': 'a'},
                {'@b': 'b'}],
                '@y': 'nothing',
                '@x': {'@l': 'l'}}]

        expected = [{"z": [{"a": "a"},
                    {"b": "b"}],
                    "y": "nothing",
                    "x": {"l": "l"}}]
        self.assertCountEqual(self.mc.connection.clean_dict(init), expected)

    @requests_mock.Mocker()
    def test_campaigns(self, m):

        # Create response
        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <campaigns>'
               '    <campaign id="168866" active="true">'
               '      <name>FWA-SaleforceTestAccount Master Campaign</name>'
               '      <description/>'
               '      <tags>'
               '      </tags>'
               '    </campaign>'
               '    <campaign id="184679" active="true">'
               '      <name>TEST Campagin</name>'
               '      <description>Test campaign created by Daniel Bravo</description>'
               '      <tags>'
               '        <tag>daniel@movementcooperative.org</tag>'
               '      </tags>'
               '    </campaign>'
               '  </campaigns>'
               '</response>')

        m.get(self.mc.connection.uri + 'campaigns', text=xml)

        # Expected Structure
        expected = ['id', 'active', 'name', 'description', 'tags']

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.mc.campaigns()))

        # To Do: Test what happens when it doesn't find any Campaigns

    @requests_mock.Mocker()
    def test_campaign(self, m):

        # Initial conditions
        CAMPAIGN_ID = 168866

        # Create response
        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <campaigns>'
               '    <campaign id="168866" active="true">'
               '      <name>FWA-SaleforceTestAccount Master Campaign</name>'
               '      <description/>'
               '      <tags>'
               '      </tags>'
               '    </campaign>'
               '  </campaigns>'
               '</response>')
        m.get(self.mc.connection.uri + 'campaigns', text=xml)

        # Expected Structure
        expected = ['id', 'active', 'name', 'description', 'tags']

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.mc.campaign(CAMPAIGN_ID)))

        # To Do: Test what happens when it doesn't find the Campaign

    @requests_mock.Mocker()
    def test_groups(self, m):

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <groups>'
               '    <group id="15084" type="FilteredGroup" status="active">'
               '      <name>CA California</name>'
               '      <size>4896</size>'
               '    </group>'
               '    <group id="18674" type="UploadedGroup" status="inactive">'
               '      <name>Capps Callers</name>'
               '      <size>90</size>'
               '    </group>'
               '    <group id="20094" type="UploadedGroup" status="inactive">'
               '      <name>Lockyer Callers</name>'
               '      <size>28</size>'
               '    </group>'
               '  </groups>'
               '</response>')

        m.get(self.mc.connection.uri + 'groups', text=xml)

        # Expected Structure
        expected = ['id', 'type', 'status', 'name', 'size']

        self.assertTrue(validate_list(expected, self.mc.groups()))

    @requests_mock.Mocker()
    def test_groups_none(self, m):

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <groups>'
               '  </groups>'
               '</response>')

        m.get(self.mc.connection.uri + 'groups', text=xml)

        # Expects None

        self.assertIsNone(self.mc.groups())

    @requests_mock.Mocker()
    def test_group_members(self, m):

        # Initial conditions
        GROUP_ID = 355559

# FIXXXXX
        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <group name="“WATCH” opt-ins since December 4th" id="355559" type="FilteredGroup">'
               '    <profile id="260832344">'
               '      <first_name/>'
               '      <last_name/>'
               '      <phone_number>19148825677</phone_number>'
               '      <email>rlandstrom11@gmail.com</email>'
               '      <status>Active Subscriber</status>'
               '      <created_at>2017-12-04 21:16:47 UTC</created_at>'
               '      <updated_at>2018-04-30 21:46:07 UTC</updated_at>'
               '      <opted_out_at/>'
               '      <opted_out_source/>'
               '      <source type="mConnect" name="NY_Cuomo_Stop inFRACKstructure_LS1117" id="36653"/>'
               '      <address>'
               '        <street1/>'
               '        <street2/>'
               '        <city>Monroe</city>'
               '        <state>NY</state>'
               '        <postal_code>10950</postal_code>'
               '        <country>US</country>'
               '      </address>'
               '      <location>'
               '        <latitude>41.33065</latitude>'
               '        <longitude>-74.18681</longitude>'
               '        <precision>place</precision>'
               '        <city>Monroe</city>'
               '        <state>NY</state>'
               '        <postal_code>10950</postal_code>'
               '        <country>US</country>'
               '      </location>'
               '      <districts>'
               '        <congressional_district>NY-18</congressional_district>'
               '        <state_upper_district>NY-</state_upper_district>'
               '        <state_lower_district>NY-</state_lower_district>'
               '        <split_district>No</split_district>'
               '      </districts>'
               '      <custom_columns>'
               '        <custom_column name="0715ManyWords"/>'
               '        <custom_column name="0715OneWord"/>'
               '        <custom_column name="ABX_pop_quiz"/>'
               '        <custom_column name="Antibiotic-Resistance_MJB0614"/>'
               '        <custom_column name="AntibioticsFlowchartQ1_MJB0614"/>'
               '        <custom_column name="AntibioticsFlowchartQ2_MJB0614"/>'
               '        <custom_column name="AntibioticsFlowchartQ3_MJB0614"/>'
               '        <custom_column name="AntibioticsFlowchartQ4_MJB0614"/>'
               '        <custom_column name="CA_Feb7Bus_MJB0115"/>'
               '        <custom_column name="CON-ID"/>'
               '        <custom_column name="DAPL_Action_TownHall_1_SH"/>'
               '        <custom_column name="DAPL_Action_TownHall_2_SH"/>'
               '        <custom_column name="DAPL_Action_TownHall_3_SH"/>'
               '        <custom_column name="dark_act_petition"/>'
               '        <custom_column name="DC_resist_SH"/>'
               '        <custom_column name="DC_resist2_SH"/>'
               '        <custom_column name="Fossil Fuel_1"/>'
               '        <custom_column name="Fossil Fuel_2"/>'
               '        <custom_column name="Frackdown - Cool? MJB091114"/>'
               '        <custom_column name="Frackopoly_InfoBuyDonate_MC0516"/>'
               '        <custom_column name="Frackopoly_InfoBuyDonate2_MC0516"/>'
               '        <custom_column name="Frackopoly_InfoBuyDonate3_MC0516"/>'
               '        <custom_column name="Frackopoly_InfoBuyDonate4_MC0516"/>'
               '        <custom_column name="FWWJOBS"/>'
               '        <custom_column name="general_text"/>'
               '        <custom_column name="Generic_YES-NO"/>'
               '        <custom_column name="Krasner_1"/>'
               '        <custom_column name="Krasner_2"/>'
               '        <custom_column name="MCER_2SignUpInfo_SH0516"/>'
               '        <custom_column name="MCER_3SignUpInfo_SH0516"/>'
               '        <custom_column name="MCER_4SignUpInfo_SH0516"/>'
               '        <custom_column name="MCER_SignUpInfo_SH0516"/>'
               '        <custom_column name="MJB 060712 FR NJ Drive, How many, Need Ride"/>'
               '        <custom_column name="MJB 081613 Obama NY/PA DETAILS"/>'
               '        <custom_column name="MJB 121012 Produce Source"/>'
               '        <custom_column name="MJB 121012 Text Frequency"/>'
               '        <custom_column name="MJB 121012 Water Source"/>'
               '        <custom_column name="MJB042514PeoplesPlatformAgainstFracking"/>'
               '        <custom_column name="MJB070813WatchGaslandPartII"/>'
               '        <custom_column name="NAT_Pruitt1_SH"/>'
               '        <custom_column name="NAT_Pruitt2_SH"/>'
               '        <custom_column name="NAT_Pruitt3_SH"/>'
               '        <custom_column name="NAT_Pruitt4_SH"/>'
               '        <custom_column name="NAT_PublicLandsDay_SH0916"/>'
               '        <custom_column name="NAT_PublicLandsDay2_SH0916"/>'
               '        <custom_column name="NAT_resistance event_SH0217"/>'
               '        <custom_column name="NAT_resistance event2_SH0217"/>'
               '        <custom_column name="NAT_TPP_2ndCall_SH1016"/>'
               '        <custom_column name="NAT_TPP_CALL_SH"/>'
               '        <custom_column name="NAT_TPP_Oct 2016 TPP Activist Call 1_1017SH"/>'
               '        <custom_column name="NAT_TPP_Oct 2016 TPP Activist Call 2_1017SH"/>'
               '        <custom_column name="NJ_Pinelands_Forum_SH0117"/>'
               '        <custom_column name="NJ_Pinelands_Forum2_SH0117"/>'
               '        <custom_column name="NJ_Pinelands Jan 24 Hearing_SH0117"/>'
               '        <custom_column name="NJ_Pinelands Jan 24_SH0117"/>'
               '        <custom_column name="NJ_TeamRetreat_MobileDemo_2_SH0916"/>'
               '        <custom_column name="NJ_TeamRetreat_MobileDemo_3_SH0916"/>'
               '        <custom_column name="NJ_TeamRetreat_MobileDemo_SH0916"/>'
               '        <custom_column name="NTENDrink"/>'
               '        <custom_column name="NY Sheridan Hollow more info 0518"/>'
               '        <custom_column name="OFF_Host Ask_1_SH0417"/>'
               '        <custom_column name="OFF_Host Ask_2_SH0417"/>'
               '        <custom_column name="ombid" created_at="2018-04-30T21:46:07Z" updated_at="2018-04-30T21:46:07Z">'
               '14121        </custom_column>'
               '        <custom_column name="OR Right to Know 091814"/>'
               '        <custom_column name="petition_read_or_sign"/>'
               '        <custom_column name="PLEDGE time of day"/>'
               '        <custom_column name="Resist_address_1"/>'
               '        <custom_column name="Resist_address_2"/>'
               '        <custom_column name="Resist_address_3"/>'
               '        <custom_column name="Resist_address_4"/>'
               '        <custom_column name="REV_Coming_to_Philly"/>'
               '        <custom_column name="Revolution_Opt_in_Coming_Philly"/>'
               '        <custom_column name="Smartphone"/>'
               '        <custom_column name="spanish_english"/>'
               '        <custom_column name="StudentsAct_Interest_SH0916"/>'
               '        <custom_column name="TBTTStudent"/>'
               '        <custom_column name="Top Issue Interest"/>'
               '        <custom_column name="victories_2014election"/>'
               '        <custom_column name="Voted"/>'
               '        <custom_column name="Voter_Registration"/>'
               '        <custom_column name="wolfrally0515"/>'
               '        <custom_column name="WorldWater"/>'
               '        <custom_column name="YES-NO"/>'
               '      </custom_columns>'
               '      <subscriptions>'
               '        <subscription campaign_id="9171" campaign_name="Food &amp; Water Action Master Campaign" campaign_description="" opt_in_path_id="132681" status="Active" opt_in_source="WATCH" created_at="2017-12-04T21:23:58Z" activated_at="2017-12-04T21:23:58Z" opted_out_at="" opt_out_source=""/>'
               '        <subscription campaign_id="12681" campaign_name="FWW General Campaign" campaign_description="" opt_in_path_id="" status="Active" opt_in_source="DRBC call in day (PA, NY, NJ, DE) EP1217 FINAL " created_at="2017-12-05T15:59:30Z" activated_at="2017-12-05T15:59:30Z" opted_out_at="" opt_out_source=""/>'
               '        <subscription campaign_id="82861" campaign_name="New York" campaign_description="" opt_in_path_id="" status="Active" opt_in_source="NY Spectra 12/18 Call Cuomo LS FINAL" created_at="2017-12-18T18:52:37Z" activated_at="2017-12-18T18:52:37Z" opted_out_at="" opt_out_source=""/>'
               '        <subscription campaign_id="89401" campaign_name="Water for the Public" campaign_description="" opt_in_path_id="" status="Active" opt_in_source="NAT Water Privatization Nestle Water Grab LH0318 FINAL" created_at="2018-03-01T23:32:24Z" activated_at="2018-03-01T23:32:24Z" opted_out_at="" opt_out_source=""/>'
               '        <subscription campaign_id="130917" campaign_name="Fundraising" campaign_description="All opt-in paths for people wanting to donate. " opt_in_path_id="" status="Active" opt_in_source="NAT DEV 2018 Sustainer Drive Monsanto survey engagement LH0718 draft copy 9" created_at="2018-08-02T19:34:52Z" activated_at="2018-08-02T19:34:52Z" opted_out_at="" opt_out_source=""/>'
               '      </subscriptions>'
               '      <clicks>'
               '        <click id="114680924">'
               '          <created_at>2018-11-23 22:14:25 UTC</created_at>'
               '          <url>https://www.foodandwaterwatch.org/news/food-water-watch-response-national-climate-assessment-release</url>'
               '          <remote_addr>148.74.84.216</remote_addr>'
               '          <http_referer>148.74.84.216</http_referer>'
               '          <user_agent>Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1</user_agent>'
               '        </click>'
               '        <click id="116297642">'
               '          <created_at>2018-12-04 20:05:18 UTC</created_at>'
               '          <url>https://secure.foodandwaterwatch.org/act/tell-drbc-we-need-full-ban-fracking?ms=onor_mc_12032018_tell-drbc-we-need-full-ban-fracking&amp;oms=onor_mc_12032018_tell-drbc-we-need-full-ban-fracking&amp;phone=19148825677&amp;profile_city=Monroe&amp;profile_email=rlandstrom11%40gmail.com&amp;profile_first_name=&amp;profile_last_name=&amp;profile_postal_code=10950&amp;profile_state=NY</url>'
               '          <remote_addr>216.6.184.136</remote_addr>'
               '          <http_referer>216.6.184.136</http_referer>'
               '          <user_agent>Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1</user_agent>'
               '        </click>'
               '      </clicks>'
               '    </profile>'
               '    <profile id="261988127">'
               '      <first_name/>'
               '      <last_name/>'
               '      <phone_number>19175144109</phone_number>'
               '      <email>rachelmarcohavens@gmail.com</email>'
               '      <status>Active Subscriber</status>'
               '      <created_at>2017-12-11 13:45:10 UTC</created_at>'
               '      <updated_at>2018-04-20 22:22:54 UTC</updated_at>'
               '      <opted_out_at/>'
               '      <opted_out_source/>'
               '      <source type="mConnect" name="NY_Cuomo_Stop inFRACKstructure_LS1117" id="36653"/>'
               '      <address>'
               '        <street1/>'
               '        <street2/>'
               '        <city>Woodstock</city>'
               '        <state>NY</state>'
               '        <postal_code>12498</postal_code>'
               '        <country>US</country>'
               '      </address>'
               '      <location>'
               '        <latitude>42.04136</latitude>'
               '        <longitude>-74.11762</longitude>'
               '        <precision>place</precision>'
               '        <city>Woodstock</city>'
               '        <state>NY</state>'
               '        <postal_code>12498</postal_code>'
               '        <country>US</country>'
               '      </location>'
               '      <districts>'
               '        <congressional_district>NY-19</congressional_district>'
               '        <state_upper_district>NY-</state_upper_district>'
               '        <state_lower_district>NY-</state_lower_district>'
               '        <split_district>No</split_district>'
               '      </districts>'
               '      <custom_columns>'
               '        <custom_column name="0715ManyWords"/>'
               '        <custom_column name="0715OneWord"/>'
               '        <custom_column name="ABX_pop_quiz"/>'
               '        <custom_column name="Antibiotic-Resistance_MJB0614"/>'
               '        <custom_column name="AntibioticsFlowchartQ1_MJB0614"/>'
               '        <custom_column name="AntibioticsFlowchartQ2_MJB0614"/>'
               '        <custom_column name="AntibioticsFlowchartQ3_MJB0614"/>'
               '        <custom_column name="AntibioticsFlowchartQ4_MJB0614"/>'
               '        <custom_column name="CA_Feb7Bus_MJB0115"/>'
               '        <custom_column name="CON-ID"/>'
               '        <custom_column name="DAPL_Action_TownHall_1_SH"/>'
               '        <custom_column name="DAPL_Action_TownHall_2_SH"/>'
               '        <custom_column name="DAPL_Action_TownHall_3_SH"/>'
               '        <custom_column name="dark_act_petition"/>'
               '        <custom_column name="DC_resist_SH"/>'
               '        <custom_column name="DC_resist2_SH"/>'
               '        <custom_column name="Fossil Fuel_1"/>'
               '        <custom_column name="Fossil Fuel_2"/>'
               '        <custom_column name="Frackdown - Cool? MJB091114"/>'
               '        <custom_column name="Frackopoly_InfoBuyDonate_MC0516"/>'
               '        <custom_column name="Frackopoly_InfoBuyDonate2_MC0516"/>'
               '        <custom_column name="Frackopoly_InfoBuyDonate3_MC0516"/>'
               '        <custom_column name="Frackopoly_InfoBuyDonate4_MC0516"/>'
               '        <custom_column name="FWWJOBS"/>'
               '        <custom_column name="general_text"/>'
               '        <custom_column name="Generic_YES-NO"/>'
               '        <custom_column name="Krasner_1"/>'
               '        <custom_column name="Krasner_2"/>'
               '        <custom_column name="MCER_2SignUpInfo_SH0516"/>'
               '        <custom_column name="MCER_3SignUpInfo_SH0516"/>'
               '        <custom_column name="MCER_4SignUpInfo_SH0516"/>'
               '        <custom_column name="MCER_SignUpInfo_SH0516"/>'
               '        <custom_column name="MJB 060712 FR NJ Drive, How many, Need Ride"/>'
               '        <custom_column name="MJB 081613 Obama NY/PA DETAILS"/>'
               '        <custom_column name="MJB 121012 Produce Source"/>'
               '        <custom_column name="MJB 121012 Text Frequency"/>'
               '        <custom_column name="MJB 121012 Water Source"/>'
               '        <custom_column name="MJB042514PeoplesPlatformAgainstFracking"/>'
               '        <custom_column name="MJB070813WatchGaslandPartII"/>'
               '        <custom_column name="NAT_Pruitt1_SH"/>'
               '        <custom_column name="NAT_Pruitt2_SH"/>'
               '        <custom_column name="NAT_Pruitt3_SH"/>'
               '        <custom_column name="NAT_Pruitt4_SH"/>'
               '        <custom_column name="NAT_PublicLandsDay_SH0916"/>'
               '        <custom_column name="NAT_PublicLandsDay2_SH0916"/>'
               '        <custom_column name="NAT_resistance event_SH0217"/>'
               '        <custom_column name="NAT_resistance event2_SH0217"/>'
               '        <custom_column name="NAT_TPP_2ndCall_SH1016"/>'
               '        <custom_column name="NAT_TPP_CALL_SH"/>'
               '        <custom_column name="NAT_TPP_Oct 2016 TPP Activist Call 1_1017SH"/>'
               '        <custom_column name="NAT_TPP_Oct 2016 TPP Activist Call 2_1017SH"/>'
               '        <custom_column name="NJ_Pinelands_Forum_SH0117"/>'
               '        <custom_column name="NJ_Pinelands_Forum2_SH0117"/>'
               '        <custom_column name="NJ_Pinelands Jan 24 Hearing_SH0117"/>'
               '        <custom_column name="NJ_Pinelands Jan 24_SH0117"/>'
               '        <custom_column name="NJ_TeamRetreat_MobileDemo_2_SH0916"/>'
               '        <custom_column name="NJ_TeamRetreat_MobileDemo_3_SH0916"/>'
               '        <custom_column name="NJ_TeamRetreat_MobileDemo_SH0916"/>'
               '        <custom_column name="NTENDrink"/>'
               '        <custom_column name="NY Sheridan Hollow more info 0518"/>'
               '        <custom_column name="OFF_Host Ask_1_SH0417"/>'
               '        <custom_column name="OFF_Host Ask_2_SH0417"/>'
               '        <custom_column name="ombid" created_at="2018-04-20T22:22:54Z" updated_at="2018-04-20T22:22:54Z">'
               '30471        </custom_column>'
               '        <custom_column name="OR Right to Know 091814"/>'
               '        <custom_column name="petition_read_or_sign"/>'
               '        <custom_column name="PLEDGE time of day"/>'
               '        <custom_column name="Resist_address_1"/>'
               '        <custom_column name="Resist_address_2"/>'
               '        <custom_column name="Resist_address_3"/>'
               '        <custom_column name="Resist_address_4"/>'
               '        <custom_column name="REV_Coming_to_Philly"/>'
               '        <custom_column name="Revolution_Opt_in_Coming_Philly"/>'
               '        <custom_column name="Smartphone"/>'
               '        <custom_column name="spanish_english"/>'
               '        <custom_column name="StudentsAct_Interest_SH0916"/>'
               '        <custom_column name="TBTTStudent"/>'
               '        <custom_column name="Top Issue Interest"/>'
               '        <custom_column name="victories_2014election"/>'
               '        <custom_column name="Voted"/>'
               '        <custom_column name="Voter_Registration"/>'
               '        <custom_column name="wolfrally0515"/>'
               '        <custom_column name="WorldWater"/>'
               '        <custom_column name="YES-NO"/>'
               '      </custom_columns>'
               '      <subscriptions>'
               '        <subscription campaign_id="9171" campaign_name="Food &amp; Water Action Master Campaign" campaign_description="" opt_in_path_id="132681" status="Active" opt_in_source="WATCH" created_at="2017-12-11T13:47:54Z" activated_at="2017-12-11T13:47:54Z" opted_out_at="" opt_out_source=""/>'
               '        <subscription campaign_id="82861" campaign_name="New York" campaign_description="" opt_in_path_id="" status="Active" opt_in_source="NY Spectra 12/18 Call Cuomo LS FINAL" created_at="2017-12-18T18:52:37Z" activated_at="2017-12-18T18:52:37Z" opted_out_at="" opt_out_source=""/>'
               '        <subscription campaign_id="89401" campaign_name="Water for the Public" campaign_description="" opt_in_path_id="" status="Active" opt_in_source="NAT Water Privatization Nestle Water Grab LH0318 FINAL" created_at="2018-03-01T23:28:01Z" activated_at="2018-03-01T23:28:01Z" opted_out_at="" opt_out_source=""/>'
               '        <subscription campaign_id="12681" campaign_name="FWW General Campaign" campaign_description="" opt_in_path_id="" status="Active" opt_in_source="NAT_WATER Act Tell Rep to Co-sponsor_LS0418 Final" created_at="2018-04-25T18:16:58Z" activated_at="2018-04-25T18:16:58Z" opted_out_at="" opt_out_source=""/>'
               '        <subscription campaign_id="130917" campaign_name="Fundraising" campaign_description="All opt-in paths for people wanting to donate. " opt_in_path_id="" status="Active" opt_in_source="NAT DEV 2018 Sustainer Drive Monsanto survey engagement LH0718 draft copy 9" created_at="2018-08-02T19:33:41Z" activated_at="2018-08-02T19:33:41Z" opted_out_at="" opt_out_source=""/>'
               '      </subscriptions>'
               '      <clicks>'
               '        <click id="99490859">'
               '          <created_at>2018-09-07 13:28:49 UTC</created_at>'
               '          <url>https://www.surveymonkey.com/r/VKWSMGF</url>'
               '          <remote_addr>24.161.64.199</remote_addr>'
               '          <http_referer>24.161.64.199</http_referer>'
               '          <user_agent>Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1</user_agent>'
               '        </click>'
               '        <click id="116311775">'
               '          <created_at>2018-12-04 20:41:23 UTC</created_at>'
               '          <url>https://secure.foodandwaterwatch.org/act/tell-drbc-we-need-full-ban-fracking?ms=onor_mc_12032018_tell-drbc-we-need-full-ban-fracking&amp;oms=onor_mc_12032018_tell-drbc-we-need-full-ban-fracking&amp;phone=19175144109&amp;profile_city=Woodstock&amp;profile_email=rachelmarcohavens%40gmail.com&amp;profile_first_name=&amp;profile_last_name=&amp;profile_postal_code=12498&amp;profile_state=NY</url>'
               '          <remote_addr>107.77.223.233</remote_addr>'
               '          <http_referer>107.77.223.233</http_referer>'
               '          <user_agent>Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1</user_agent>'
               '        </click>'
               '      </clicks>'
               '    </profile>'
               '  </group>'
               '</response>')

        m.get(self.mc.connection.uri + 'group_members', text=xml)

        # Expected Structure
        expected = ['id', 'first_name', 'last_name', 'phone_number', 'email',
                    'status', 'created_at', 'updated_at', 'opted_out_at',
                    'opted_out_source', 'source', 'address', 'location',
                    'districts', 'custom_columns', 'subscriptions', 'clicks']

        self.assertTrue(
            validate_list(expected, self.mc.group_members(GROUP_ID)))

    @requests_mock.Mocker()
    def test_group_members_group_not_exists(self, m):

        # Initial conditions
        GROUP_ID = 355559

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="false">'
               '  <error id="6" message="Invalid group id"/>'
               '</response>')

        m.get(self.mc.connection.uri + 'group_members', text=xml)

        # Expects None

        self.assertIsNone(self.mc.group_members(GROUP_ID))

    @requests_mock.Mocker()
    def test_group_create(self, m):

        # Initial conditions
        GROUP_NAME = 'This is a TEST group DB'

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <group name="This is a TEST group DB" id="436568" type="UploadedGroup">'
               '  </group>'
               '</response>')

        m.get(self.mc.connection.uri + 'create_group', text=xml)

        # Expected Structure
        expected = ['id', 'type', 'name']

        self.assertTrue(
            validate_list(expected, self.mc.group_create(GROUP_NAME)))

    @requests_mock.Mocker()
    def test_group_create_already_exists(self, m):

        # Initial conditions
        GROUP_NAME = 'This is a TEST group DB'

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="false">'
               '  <error id="18" message="Invalid name"/>'
               '</response>')

        m.get(self.mc.connection.uri + 'create_group', text=xml)

        # Expects None

        self.assertIsNone(self.mc.group_create(GROUP_NAME))

    @requests_mock.Mocker()
    def test_group_add_members(self, m):

        # Initial conditions
        GROUP_ID = 436568
        PHONES = ['7145555555']

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <group name="This is a TEST group DB" id="436568" type="UploadedGroup">'
               '  </group>'
               '</response>')

        m.get(self.mc.connection.uri + 'add_group_member', text=xml)

        # Expected Structure
        expected = ['id', 'type', 'name']

        self.assertTrue(
            validate_list(
                expected, self.mc.group_add_members(GROUP_ID, PHONES)))

    @requests_mock.Mocker()
    def test_group_add_members_invalid_group(self, m):

        # Initial conditions
        GROUP_ID = 436569
        PHONES = ['7145555555']

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="false">'
               '  <error id="6" message="Invalid group id"/>'
               '</response>')

        m.get(self.mc.connection.uri + 'add_group_member', text=xml)

        # Expects None

        self.assertIsNone(self.mc.group_add_members(GROUP_ID, PHONES))

    @requests_mock.Mocker()
    def test_group_remove_members(self, m):

        # Initial conditions
        GROUP_ID = 436568
        PHONES = ['7145555555']

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <group name="This is a TEST group DB" id="436568" type="UploadedGroup">'
               '  </group>'
               '</response>')

        m.get(self.mc.connection.uri + 'remove_group_member', text=xml)

        # Expected Structure
        expected = ['id', 'type', 'name']

        self.assertTrue(
            validate_list(
                expected, self.mc.group_remove_members(GROUP_ID, PHONES)))

    @requests_mock.Mocker()
    def test_group_remove_members_invalid_group(self, m):

        # Initial conditions
        GROUP_ID = 436569
        PHONES = ['7145555555']

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="false">'
               '  <error id="6" message="Invalid group id"/>'
               '</response>')

        m.get(self.mc.connection.uri + 'remove_group_member', text=xml)

        # Expects None

        self.assertIsNone(self.mc.group_remove_members(GROUP_ID, PHONES))

    @requests_mock.Mocker()
    def test_profiles(self, m):

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <profiles num="2" page="1">'
               '    <profile id="258627572">'
               '      <first_name/>'
               '      <last_name/>'
               '      <phone_number>14435042443</phone_number>'
               '      <email/>'
               '      <status>Profiles with no Subscriptions</status>'
               '      <created_at>2017-11-17 14:47:13 UTC</created_at>'
               '      <updated_at>2017-11-17 14:47:13 UTC</updated_at>'
               '      <opted_out_at/>'
               '      <opted_out_source/>'
               '      <source type="API" name="Ryan Zavislak" email="rzavislak@fwwatch.org"/>'
               '      <address>'
               '        <street1/>'
               '        <street2/>'
               '        <city/>'
               '        <state/>'
               '        <postal_code/>'
               '        <country/>'
               '      </address>'
               '      <location>'
               '        <latitude>39.547557</latitude>'
               '        <longitude>-76.321984</longitude>'
               '        <precision>place</precision>'
               '        <city>Bel Air</city>'
               '        <state>MD</state>'
               '        <postal_code>21014</postal_code>'
               '        <country>US</country>'
               '      </location>'
               '      <districts>'
               '        <congressional_district>MD-1</congressional_district>'
               '        <state_upper_district>MD-</state_upper_district>'
               '        <state_lower_district>MD-</state_lower_district>'
               '        <split_district>No</split_district>'
               '      </districts>'
               '      <custom_columns>'
               '      </custom_columns>'
               '      <integrations>'
               '        <integration constituent_id="" type="Salesforce" synchronized_at=""/>'
               '      </integrations>'
               '      <clicks>'
               '      </clicks>'
               '    </profile>'
               '    <profile id="282126752">'
               '      <first_name>Nance</first_name>'
               '      <last_name>Kidwell</last_name>'
               '      <phone_number>70386981280</phone_number>'
               '      <email>nancekidwell@gmail.com</email>'
               '      <status>Undeliverable</status>'
               '      <created_at>2018-03-02 22:21:42 UTC</created_at>'
               '      <updated_at>2018-03-02 22:21:42 UTC</updated_at>'
               '      <opted_out_at>2018-03-02 22:21:42 UTC</opted_out_at>'
               '      <opted_out_source>Opt-out from API</opted_out_source>'
               '      <source type="API" name="Frakture Bot" email="frakturebot@frakture.com"/>'
               '      <address>'
               '        <street1>1462 Spring Vale Ave</street1>'
               '        <street2/>'
               '        <city>Mc Lean</city>'
               '        <state>VA</state>'
               '        <postal_code>22101-3527</postal_code>'
               '        <country>US</country>'
               '      </address>'
               '      <location>'
               '        <latitude>38.932367</latitude>'
               '        <longitude>-77.185224</longitude>'
               '        <precision>rooftop</precision>'
               '        <city>Mc Lean</city>'
               '        <state>VA</state>'
               '        <postal_code>22101</postal_code>'
               '        <country>US</country>'
               '      </location>'
               '      <districts>'
               '        <congressional_district>VA-10</congressional_district>'
               '        <state_upper_district>VA-32</state_upper_district>'
               '        <state_lower_district>VA-48</state_lower_district>'
               '        <split_district>No</split_district>'
               '      </districts>'
               '      <custom_columns>'
               '      </custom_columns>'
               '      <integrations>'
               '      </integrations>'
               '      <clicks>'
               '      </clicks>'
               '    </profile>'
               '  </profiles>'
               '</response>')

        m.get(self.mc.connection.uri + 'profiles', text=xml)

        # Expected Structure
        expected = ['id', 'first_name', 'last_name', 'phone_number', 'email',
                    'status', 'created_at', 'updated_at', 'opted_out_at',
                    'opted_out_source', 'source', 'address', 'location',
                    'districts', 'custom_columns', 'integrations', 'clicks']

        self.assertTrue(validate_list(expected, self.mc.profiles(limit=2)))

    @requests_mock.Mocker()
    def test_profile_get(self, m):

        # Initial conditions
        PHONE = '7145555555'

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <profile id="326709143">'
               '    <first_name>Test</first_name>'
               '    <last_name>User</last_name>'
               '    <phone_number>17145555555</phone_number>'
               '    <email>testuser+7145555555@email.com</email>'
               '    <status>Profiles with no Subscriptions</status>'
               '    <created_at>2018-12-05 01:04:59 UTC</created_at>'
               '    <updated_at>2018-12-05 01:04:59 UTC</updated_at>'
               '    <opted_out_at/>'
               '    <opted_out_source/>'
               '    <source type="API" name="Daniel Bravo" email="daniel@movementcooperative.org"/>'
               '    <address>'
               '      <street1/>'
               '      <street2/>'
               '      <city/>'
               '      <state/>'
               '      <postal_code/>'
               '      <country>US</country>'
               '    </address>'
               '    <location>'
               '      <latitude>33.844983</latitude>'
               '      <longitude>-117.952151</longitude>'
               '      <precision>place</precision>'
               '      <city>Anaheim</city>'
               '      <state>CA</state>'
               '      <postal_code>92801</postal_code>'
               '      <country>US</country>'
               '    </location>'
               '    <districts>'
               '      <congressional_district>CA-</congressional_district>'
               '      <state_upper_district>CA-</state_upper_district>'
               '      <state_lower_district>CA-</state_lower_district>'
               '      <split_district>No</split_district>'
               '    </districts>'
               '    <custom_columns>'
               '    </custom_columns>'
               '    <integrations>'
               '    </integrations>'
               '    <clicks>'
               '    </clicks>'
               '  </profile>'
               '</response>')

        m.get(self.mc.connection.uri + 'profile', text=xml)

        # Expected Structure
        expected = ['id', 'first_name', 'last_name', 'phone_number', 'email',
                    'status', 'created_at', 'updated_at', 'opted_out_at',
                    'opted_out_source', 'source', 'address', 'location',
                    'districts', 'custom_columns', 'integrations', 'clicks']

        self.assertTrue(validate_list(expected, self.mc.profile_get(PHONE)))

    @requests_mock.Mocker()
    def test_profile_get_invalid_phone(self, m):

        # Initial conditions
        PHONE = '71455555558'

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="false">'
               '  <error id="5" message="Invalid phone number"/>'
               '</response>')

        m.get(self.mc.connection.uri + 'profile', text=xml)

        # Expects None

        self.assertIsNone(self.mc.profile_get(PHONE))

    @requests_mock.Mocker()
    def test_profile_update(self, m):

        # Initial conditions
        PHONE = '7145555555'
        NAME = 'Testupdate'

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <profile id="326709143">'
               '    <first_name>Testupdate</first_name>'
               '    <last_name>User</last_name>'
               '    <phone_number>17145555555</phone_number>'
               '    <email>testuser+7145555555@email.com</email>'
               '    <status>Profiles with no Subscriptions</status>'
               '    <created_at>2018-12-05 01:04:59 UTC</created_at>'
               '    <updated_at>2018-12-05 09:00:48 UTC</updated_at>'
               '    <opted_out_at/>'
               '    <opted_out_source/>'
               '    <source type="API" name="Daniel Bravo" email="daniel@movementcooperative.org"/>'
               '    <address>'
               '      <street1/>'
               '      <street2/>'
               '      <city/>'
               '      <state/>'
               '      <postal_code/>'
               '      <country>US</country>'
               '    </address>'
               '    <location>'
               '      <latitude>33.844983</latitude>'
               '      <longitude>-117.952151</longitude>'
               '      <precision>place</precision>'
               '      <city>Anaheim</city>'
               '      <state>CA</state>'
               '      <postal_code>92801</postal_code>'
               '      <country>US</country>'
               '    </location>'
               '    <districts>'
               '      <congressional_district>CA-</congressional_district>'
               '      <state_upper_district>CA-</state_upper_district>'
               '      <state_lower_district>CA-</state_lower_district>'
               '      <split_district>No</split_district>'
               '    </districts>'
               '    <custom_columns>'
               '    </custom_columns>'
               '    <integrations>'
               '    </integrations>'
               '    <clicks>'
               '    </clicks>'
               '  </profile>'
               '</response>')

        m.post(self.mc.connection.uri + 'profile_update', text=xml)

        # Expected Structure
        expected = ['id', 'first_name', 'last_name', 'phone_number', 'email',
                    'status', 'created_at', 'updated_at', 'opted_out_at',
                    'opted_out_source', 'source', 'address', 'location',
                    'districts', 'custom_columns', 'integrations', 'clicks']

        self.assertTrue(
            validate_list(
                expected, self.mc.profile_update(PHONE, first_name=NAME)))

    @requests_mock.Mocker()
    def test_profile_opt_out(self, m):

        # Initial conditions
        PHONE = '7145555555'

        xml = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<response success="true">'
               '  <profile id="301650791">'
               '    <first_name/>'
               '    <last_name/>'
               '    <phone_number>17142706998</phone_number>'
               '    <email/>'
               '    <status>Undeliverable</status>'
               '    <created_at>2018-07-12 19:48:36 UTC</created_at>'
               '    <updated_at>2018-12-05 09:34:51 UTC</updated_at>'
               '    <opted_out_at>2018-12-05 09:34:51 UTC</opted_out_at>'
               '    <opted_out_source>Opt-out from API</opted_out_source>'
               '    <source type="API" name="Daniel Bravo" email="daniel@movementcooperative.org"/>'
               '    <address>'
               '      <street1/>'
               '      <street2/>'
               '      <city/>'
               '      <state/>'
               '      <postal_code/>'
               '      <country>US</country>'
               '    </address>'
               '    <location>'
               '      <latitude>33.844983</latitude>'
               '      <longitude>-117.952151</longitude>'
               '      <precision>place</precision>'
               '      <city>Anaheim</city>'
               '      <state>CA</state>'
               '      <postal_code>92801</postal_code>'
               '      <country>US</country>'
               '    </location>'
               '    <districts>'
               '      <congressional_district>CA-</congressional_district>'
               '      <state_upper_district>CA-</state_upper_district>'
               '      <state_lower_district>CA-</state_lower_district>'
               '      <split_district>No</split_district>'
               '    </districts>'
               '    <custom_columns>'
               '    </custom_columns>'
               '    <subscriptions>'
               '      <subscription campaign_id="184679" campaign_name="TEST Campagin" campaign_description="Test campaign created by Daniel Bravo" opt_in_path_id="272075" status="Opted-Out" opt_in_source="Daniel Bravo" created_at="2018-12-05T09:22:27Z" activated_at="2018-12-05T09:22:27Z" opted_out_at="2018-12-05T09:34:51Z" opt_out_source="Opt-out from API"/>'
               '    </subscriptions>'
               '    <integrations>'
               '    </integrations>'
               '    <clicks>'
               '    </clicks>'
               '  </profile>'
               '</response>')

        m.post(self.mc.connection.uri + 'profile_opt_out', text=xml)

        # Expected Structure
        expected = ['id', 'first_name', 'last_name', 'phone_number', 'email',
                    'status', 'created_at', 'updated_at', 'opted_out_at',
                    'opted_out_source', 'source', 'address', 'location',
                    'districts', 'custom_columns', 'integrations', 'clicks',
                    'subscriptions']

        self.assertTrue(
            validate_list(
                expected, self.mc.profile_opt_out(PHONE)))

if __name__ == "__main__":
    unittest.main()
