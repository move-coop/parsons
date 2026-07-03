from pathlib import Path

import pytest


@pytest.mark.live
def test_create_job_xml(ts_automation, automation_test_xml):
    # Assert that job xml creates the file correctly
    job_xml = ts_automation.create_job_xml(
        "job_type", "match_job", ["test@gmail.com", "test2@gmail.com"]
    )
    test_xml = Path(automation_test_xml).read_text()
    real_xml = Path(job_xml).read_text()
    assert test_xml == real_xml


@pytest.mark.live
def test_config_status(ts_automation, automation_sftp, automation_job_name, automation_test_xml):
    # Find good configuration
    automation_sftp.put_file(
        automation_test_xml,
        f"{ts_automation.sftp_dir}/{automation_job_name}.job.xml.good",
    )
    assert ts_automation.config_status(automation_job_name)
    ts_automation.remove_files(automation_job_name)

    # Find bad configuration
    automation_sftp.put_file(
        automation_test_xml,
        f"{ts_automation.sftp_dir}/{automation_job_name}.job.xml.bad",
    )
    with pytest.raises(
        ValueError,
        match="Job configuration failed. If you provided an email address, you will be sent more details.",
    ):
        ts_automation.config_status(automation_job_name)


@pytest.mark.live
def test_match_status(ts_automation, automation_sftp, automation_job_name):
    # Find good configuration
    good_match = "test/test_targetsmart/match_good.xml"
    automation_sftp.put_file(
        good_match, f"{ts_automation.sftp_dir}/{automation_job_name}.finish.xml"
    )
    assert ts_automation.match_status(automation_job_name)
    ts_automation.remove_files(automation_job_name)

    # Find bad configuration
    bad_match = "test/test_targetsmart/match_bad.xml"
    automation_sftp.put_file(
        bad_match, f"{ts_automation.sftp_dir}/{automation_job_name}.finish.xml"
    )
    with pytest.raises(ValueError, match="Match job failed"):
        ts_automation.match_status(automation_job_name)


@pytest.mark.live
def test_remove_files(ts_automation, automation_sftp, automation_job_name, automation_test_xml):
    # Add a file
    automation_sftp.put_file(
        automation_test_xml, f"{ts_automation.sftp_dir}/{automation_job_name}.txt"
    )

    # Remove files
    ts_automation.remove_files(automation_job_name)

    # Check that file is not there
    dir_list = automation_sftp.list_directory(f"{ts_automation.sftp_dir}/")
    assert f"{automation_job_name}.txt" not in dir_list
