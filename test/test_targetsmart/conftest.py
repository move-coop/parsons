import os

import pytest

from parsons import SFTP, TargetSmartAPI, TargetSmartAutomation


@pytest.fixture
def ts_api():
    """Create a fresh API instance for each test."""
    return TargetSmartAPI(api_key="FAKEKEY")


@pytest.fixture
def ts_automation():
    """Create a fresh TargetSmart Automation instance for each test."""
    return TargetSmartAutomation()


@pytest.fixture
def automation_job_name(ts_automation):
    """Provide a test job name and clean up any files it left behind."""
    job_name = "a-test-job"
    yield job_name
    # Clean up the files that were put on the SFTP.
    ts_automation.remove_files(job_name)


@pytest.fixture
def automation_sftp(ts_automation):
    """Create an SFTP client using the Automation credentials from the environment."""
    return SFTP(
        ts_automation.sftp_host,
        os.environ["TS_SFTP_USERNAME"],
        os.environ["TS_SFTP_PASSWORD"],
        ts_automation.sftp_port,
    )


@pytest.fixture
def automation_test_xml():
    """Path to the reference job configuration XML."""
    return "test/test_targetsmart/job_config.xml"


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
