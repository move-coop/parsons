import os
import unittest
from pathlib import Path

import pytest

from parsons import SFTP, TargetSmartAutomation
from test.utils import mark_live_test


class TestTargetSmartAutomation(unittest.TestCase):
    def setUp(self):
        self.ts = TargetSmartAutomation()
        self.job_name = "a-test-job"
        self.sftp = SFTP(
            self.ts.sftp_host,
            os.environ["TS_SFTP_USERNAME"],
            os.environ["TS_SFTP_PASSWORD"],
            self.ts.sftp_port,
        )
        self.test_xml = "test/test_targetsmart/job_config.xml"

    def tearDown(self):
        # Clean up the files were put on the SFTP
        self.ts.remove_files(self.job_name)

    @mark_live_test
    def test_create_job_xml(self):
        # Assert that job xml creates the file correctly
        job_xml = self.ts.create_job_xml(
            "job_type", "match_job", ["test@gmail.com", "test2@gmail.com"]
        )
        test_xml = Path(self.test_xml).read_text()
        real_xml = Path(job_xml).read_text()
        assert test_xml == real_xml

    @mark_live_test
    def test_config_status(self):
        # Find good configuration
        self.sftp.put_file(self.test_xml, f"{self.ts.sftp_dir}/{self.job_name}.job.xml.good")
        assert self.ts.config_status(self.job_name)
        self.ts.remove_files(self.job_name)

        # Find bad configuration
        self.sftp.put_file(self.test_xml, f"{self.ts.sftp_dir}/{self.job_name}.job.xml.bad")
        with pytest.raises(
            ValueError,
            match="Job configuration failed. If you provided an email address, you will be sent more details.",
        ):
            self.ts.config_status(self.job_name)

    @mark_live_test
    def test_match_status(self):
        # Find good configuration
        good_match = "test/test_targetsmart/match_good.xml"
        self.sftp.put_file(good_match, f"{self.ts.sftp_dir}/{self.job_name}.finish.xml")
        assert self.ts.match_status(self.job_name)
        self.ts.remove_files(self.job_name)

        # Find bad configuration
        bad_match = "test/test_targetsmart/match_bad.xml"
        self.sftp.put_file(bad_match, f"{self.ts.sftp_dir}/{self.job_name}.finish.xml")
        with pytest.raises(ValueError, match="Match job failed"):
            self.ts.match_status(self.job_name)

    @mark_live_test
    def test_remove_files(self):
        # Add a file
        self.sftp.put_file(self.test_xml, f"{self.ts.sftp_dir}/{self.job_name}.txt")

        # Remove files
        self.ts.remove_files(self.job_name)

        # Check that file is not there
        dir_list = self.sftp.list_directory(f"{self.ts.sftp_dir}/")
        assert f"{self.job_name}.txt" not in dir_list
