import unittest
import requests_mock
from parsons import TargetSmartAPI, Table
from test.utils import validate_list
from test.responses.ts_responses import (
    address_response,
    district_point,
    district_expected,
    district_zip,
    zip_expected,
    phone_response,
    phone_expected,
    radius_response,
)

output_list = [
    {
        "vb.tsmart_zip": "60625",
        "vb.vf_g2014": "Y",
        "vb.vf_g2016": "Y",
        "vb.tsmart_middle_name": "H",
        "ts.tsmart_midterm_general_turnout_score": "85.5",
        "vb.tsmart_name_suffix": "",
        "vb.voterbase_gender": "Male",
        "vb.tsmart_city": "CHICAGO",
        "vb.tsmart_full_address": "908 N MAIN AVE APT 2",
        "vb.voterbase_phone": "5125705356",
        "vb.tsmart_partisan_score": "99.6",
        "vb.tsmart_last_name": "BLANKS",
        "vb.voterbase_id": "IL-12568670",
        "vb.tsmart_first_name": "BILLY",
        "vb.voterid": "Q8W8R82Z",
        "vb.voterbase_age": "37",
        "vb.tsmart_state": "IL",
        "vb.voterbase_registration_status": "Registered",
    }
]


class TestTargetSmartAPI(unittest.TestCase):
    def setUp(self):

        self.ts = TargetSmartAPI(api_key="FAKEKEY")

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_data_enhance(self, m):

        json = {
            "input": {"search_id": "IL-12568670", "search_id_type": "voterbase"},
            "error": None,
            "output": output_list,
            "output_size": 1,
            "match_found": True,
            "gateway_id": "b8c86f27-fb32-11e8-9cc1-45bc340a4d22",
            "function_id": "b8c98093-fb32-11e8-8b25-e99c70f6fe74",
        }

        expected = [
            "vb.tsmart_zip",
            "vb.vf_g2014",
            "vb.vf_g2016",
            "vb.tsmart_middle_name",
            "ts.tsmart_midterm_general_turnout_score",
            "vb.tsmart_name_suffix",
            "vb.voterbase_gender",
            "vb.tsmart_city",
            "vb.tsmart_full_address",
            "vb.voterbase_phone",
            "vb.tsmart_partisan_score",
            "vb.tsmart_last_name",
            "vb.voterbase_id",
            "vb.tsmart_first_name",
            "vb.voterid",
            "vb.voterbase_age",
            "vb.tsmart_state",
            "vb.voterbase_registration_status",
        ]

        m.get(self.ts.connection.uri + "person/data-enhance", json=json)

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.ts.data_enhance("IL-12568678")))

        # Assert exception on missing state
        with self.assertRaises(Exception):
            self.ts.data_enhance("vb0001", search_id_type="votebuilder")

        # Assert exception on missing state
        with self.assertRaises(Exception):
            self.ts.data_enhance("vb0001", search_id_type="smartvan")

        # Assert exception on missing state
        with self.assertRaises(Exception):
            self.ts.data_enhance("vb0001", search_id_type="voter")

        # Assert works with state provided
        for i in ["votebuilder", "voter", "smartvan"]:
            self.assertTrue(
                validate_list(
                    expected,
                    self.ts.data_enhance("IL-12568678", search_id_type=i, state="IL"),
                )
            )

    @requests_mock.Mocker()
    def test_radius_search(self, m):

        m.get(self.ts.connection.uri + "person/radius-search", json=radius_response)

        expected = [
            "similarity_score",
            "distance_km",
            "distance_meters",
            "distance_miles",
            "distance_feet",
            "proximity_score",
            "composite_score",
            "uniqueness_score",
            "confidence_indicator",
            "ts.tsmart_midterm_general_turnout_score",
            "vb.tsmart_city",
            "vb.tsmart_first_name",
            "vb.tsmart_full_address",
            "vb.tsmart_last_name",
            "vb.tsmart_middle_name",
            "vb.tsmart_name_suffix",
            "vb.tsmart_partisan_score",
            "vb.tsmart_precinct_id",
            "vb.tsmart_precinct_name",
            "vb.tsmart_state",
            "vb.tsmart_zip",
            "vb.tsmart_zip4",
            "vb.vf_earliest_registration_date",
            "vb.vf_g2014",
            "vb.vf_g2016",
            "vb.vf_precinct_id",
            "vb.vf_precinct_name",
            "vb.vf_reg_cass_address_full",
            "vb.vf_reg_cass_city",
            "vb.vf_reg_cass_state",
            "vb.vf_reg_cass_zip",
            "vb.vf_reg_cass_zip4",
            "vb.vf_registration_date",
            "vb.voterbase_age",
            "vb.voterbase_gender",
            "vb.voterbase_id",
            "vb.voterbase_phone",
            "vb.voterbase_registration_status",
            "vb.voterid",
        ]

        # Assert response is expected structure
        def rad_search():
            return self.ts.radius_search(
                "BILLY",
                "Burchard",
                radius_size=100,
                address="908 N Washtenaw, Chicago, IL",
            )

        self.assertTrue(validate_list(expected, rad_search()))

    def test_district_args(self):

        self.assertRaises(ValueError, self.ts.district, search_type="address")
        self.assertRaises(ValueError, self.ts.district, search_type="zip", zip4=9)
        self.assertRaises(ValueError, self.ts.district, search_type="zip", zip5=0)
        self.assertRaises(ValueError, self.ts.district, search_type="point")
        self.assertRaises(ValueError, self.ts.district, search_type="zip")

    @requests_mock.Mocker()
    def test_district_point(self, m):

        # Test Points
        m.get(self.ts.connection.uri + "service/district", json=district_point)
        self.assertTrue(
            validate_list(
                district_expected,
                self.ts.district(search_type="point", latitude="41.898369", longitude="-87.694382"),
            )
        )

    @requests_mock.Mocker()
    def test_district_zip(self, m):
        # Test Zips
        m.get(self.ts.connection.uri + "service/district", json=district_zip)
        self.assertTrue(
            validate_list(
                zip_expected,
                self.ts.district(search_type="zip", zip5="60622", zip4="7194"),
            )
        )

    @requests_mock.Mocker()
    def test_district_address(self, m):
        # Test Address
        m.get(self.ts.connection.uri + "service/district", json=address_response)
        self.assertTrue(
            validate_list(
                district_expected,
                self.ts.district(search_type="address", address="908 N Main St, Chicago, IL 60611"),
            )
        )

    @requests_mock.Mocker()
    def test_phone(self, m):

        # Test phone
        m.get(self.ts.connection.uri + "person/phone-search", json=phone_response)
        self.assertTrue(
            validate_list(phone_expected, self.ts.phone(Table([{"phone": 4435705355}])))
        )
