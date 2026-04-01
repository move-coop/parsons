import pytest

from parsons import Table, TargetSmartAPI
from test.conftest import validate_list
from test.responses.ts_responses import (
    address_response,
    district_expected,
    district_point,
    district_zip,
    phone_expected,
    phone_response,
    radius_response,
    zip_expected,
)


@pytest.fixture
def ts_api():
    """Create a fresh API instance for each test."""
    return TargetSmartAPI(api_key="FAKEKEY")


@pytest.fixture(scope="session")
def output_list():
    return [
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


@pytest.fixture(scope="session")
def expected_data_enhance_keys(output_list):
    return output_list[0].keys()


@pytest.fixture(scope="session")
def expected_radius_keys():
    return [
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


def test_data_search_id_type_not_found(ts_api, output_list, requests_mock):
    json = {
        "input": {"search_id": "IL-12568670", "search_id_type": "invalid_search_id_type"},
        "error": None,
        "output": output_list,
        "output_size": 1,
        "match_found": True,
        "gateway_id": "b8c86f27-fb32-11e8-9cc1-45bc340a4d22",
        "function_id": "b8c98093-fb32-11e8-8b25-e99c70f6fe74",
    }

    requests_mock.get(ts_api.connection.uri + "person/data-enhance", json=json)

    pytest.raises(ValueError, match="Search_id_type is not valid")


def test_data_enhance(ts_api, output_list, expected_data_enhance_keys, requests_mock):
    json = {
        "input": {"search_id": "IL-12568670", "search_id_type": "voterbase"},
        "error": None,
        "output": output_list,
        "output_size": 1,
        "match_found": True,
        "gateway_id": "b8c86f27-fb32-11e8-9cc1-45bc340a4d22",
        "function_id": "b8c98093-fb32-11e8-8b25-e99c70f6fe74",
    }

    requests_mock.get(ts_api.connection.uri + "person/data-enhance", json=json)

    # Assert response is expected structure
    assert validate_list(expected_data_enhance_keys, ts_api.data_enhance("IL-12568678"))

    # Assert exception on missing state
    with pytest.raises(KeyError, match=r"Search ID type .+ requires state kwarg"):
        ts_api.data_enhance("vb0001", search_id_type="votebuilder")

    # Assert exception on missing state
    with pytest.raises(KeyError, match=r"Search ID type .+ requires state kwarg"):
        ts_api.data_enhance("vb0001", search_id_type="smartvan")

    # Assert exception on missing state
    with pytest.raises(KeyError, match=r"Search ID type .+ requires state kwarg"):
        ts_api.data_enhance("vb0001", search_id_type="voter")

    # Assert works with state provided
    for i in ["votebuilder", "voter", "smartvan"]:
        assert validate_list(
            expected_data_enhance_keys,
            ts_api.data_enhance("IL-12568678", search_id_type=i, state="IL"),
        )


def test_radius_search(ts_api, expected_radius_keys, requests_mock):
    """Assert response is expected structure"""
    requests_mock.get(ts_api.connection.uri + "person/radius-search", json=radius_response)

    def rad_search():
        return ts_api.radius_search(
            first_name="BILLY",
            last_name="Burchard",
            radius_size=100,
            address="908 N Washtenaw, Chicago, IL",
        )

    assert validate_list(expected_radius_keys, rad_search())


def test_rad_search_no_first_name(ts_api):
    with pytest.raises(ValueError, match="First name is required"):
        ts_api.radius_search(
            first_name=None,
            last_name="Burchard",
            radius_size=100,
            address="908 N Washtenaw, Chicago, IL",
        )


def test_rad_search_no_last_name(ts_api):
    with pytest.raises(ValueError, match="Last name is required"):
        ts_api.radius_search(
            first_name="BILLY",
            last_name=None,
            radius_size=100,
            address="908 N Washtenaw, Chicago, IL",
        )


def test_rad_search_no_address_or_latlon(ts_api):
    """Assert response is expected structure"""
    with pytest.raises(ValueError, match="Lat/Long or Address required"):
        ts_api.radius_search(
            first_name="BILLY",
            last_name="Burchard",
            radius_size=100,
            address=None,
        )


def test_district_args(ts_api):
    with pytest.raises(KeyError, match="Invalid 'search_type' provided"):
        ts_api.district(search_type="invalid_search_type")
    with pytest.raises(ValueError, match="Search type 'address' requires 'address' argument"):
        ts_api.district(search_type="address")
    with pytest.raises(ValueError, match="Search type 'zip' requires 'zip5' and 'zip4' arguments"):
        ts_api.district(search_type="zip", zip4=9)
    with pytest.raises(ValueError, match="Search type 'zip' requires 'zip5' and 'zip4' arguments"):
        ts_api.district(search_type="zip", zip5=0)
    with pytest.raises(
        ValueError, match="Search type 'point' requires 'latitude' and 'longitude' arguments"
    ):
        ts_api.district(search_type="point")
    with pytest.raises(ValueError, match="Search type 'zip' requires 'zip5' and 'zip4' arguments"):
        ts_api.district(search_type="zip")


def test_district_point(ts_api, requests_mock):
    """Test Points"""
    requests_mock.get(ts_api.connection.uri + "service/district", json=district_point)
    assert validate_list(
        district_expected,
        ts_api.district(search_type="point", latitude="41.898369", longitude="-87.694382"),
    )


def test_district_zip(ts_api, requests_mock):
    """Test Zips"""
    requests_mock.get(ts_api.connection.uri + "service/district", json=district_zip)
    assert validate_list(
        zip_expected, ts_api.district(search_type="zip", zip5="60622", zip4="7194")
    )


def test_district_address(ts_api, requests_mock):
    """Test Address"""
    requests_mock.get(ts_api.connection.uri + "service/district", json=address_response)
    assert validate_list(
        district_expected,
        ts_api.district(search_type="address", address="908 N Main St, Chicago, IL 60611"),
    )


def test_phone(ts_api, requests_mock):
    """Test phone"""
    requests_mock.get(ts_api.connection.uri + "person/phone-search", json=phone_response)
    assert validate_list(phone_expected, ts_api.phone(Table([{"phone": 4435705355}])))


@pytest.mark.parametrize(
    ("vanid", "expected_url"),
    [
        (55895, "https://www.targetsmartvan.com/ContactsDetails.aspx?VANID=EID75ADQ"),
        (55901, "https://www.targetsmartvan.com/ContactsDetails.aspx?VANID=EIDD5ADF"),
        ("337052", "https://www.targetsmartvan.com/ContactsDetails.aspx?VANID=EIDC9425K"),
        ("337,052", "https://www.targetsmartvan.com/ContactsDetails.aspx?VANID=EIDC9425K"),
    ],
)
def test_get_ngp_url_from_vanid(ts_api, vanid: int | str, expected_url: str) -> None:
    targetsmart_url = ts_api.get_ngp_url_from_vanid(vanid)
    assert targetsmart_url == expected_url


@pytest.mark.parametrize(
    ("url", "expected_vanid"),
    [
        ("https://www.targetsmartvan.com/ContactsDetails.aspx?VANID=EID75ADQ", 55895),
        ("https://www.targetsmartvan.com/ContactsDetails.aspx?VANID=EIDD5ADF", 55901),
        ("https://www.targetsmartvan.com/ContactsDetails.aspx?VANID=EIDC9425K", 337052),
    ],
)
def test_get_vanid_from_ngp_url(ts_api, url: str, expected_vanid: int | str) -> None:
    vanid = ts_api.get_vanid_from_ngp_url(url)
    assert vanid == expected_vanid
