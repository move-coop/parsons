import json
import unittest
from pathlib import Path

import requests_mock

from parsons import RockTheVote

_dir = Path(__file__).parent


class TestRockTheVote(unittest.TestCase):
    @requests_mock.Mocker()
    def test_create_registration_report(self, mocker):
        report_id = "123"
        partner_id = "1"
        partner_api_key = "abcd"
        mocker.post(
            "https://register.rockthevote.com/api/v4/registrant_reports.json",
            json={"report_id": report_id},
        )

        rtv = RockTheVote(partner_id=partner_id, partner_api_key=partner_api_key)

        result = rtv.create_registration_report()
        self.assertEqual(result, report_id)

    @requests_mock.Mocker()
    def test_get_registration_report(self, mocker):
        partner_id = "1"
        partner_api_key = "abcd"
        mocker.get(
            "https://register.rockthevote.com/api/v4/registrant_reports/1",
            json={"download_url": "https://register.rockthevote.com/download/whatever"},
        )
        mocker.get(
            "https://register.rockthevote.com/download/whatever",
            text=(Path(_dir) / "sample.csv").read_text(),
        )

        rtv = RockTheVote(partner_id=partner_id, partner_api_key=partner_api_key)

        result = rtv.get_registration_report(report_id=1)
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result[0]["first_name"], "Carol")
        self.assertEqual(result[0]["last_name"], "King")

    @requests_mock.Mocker()
    def test_run_registration_report(self, mocker):
        report_id = "123"
        partner_id = "1"
        partner_api_key = "abcd"
        mocker.post(
            "https://register.rockthevote.com/api/v4/registrant_reports.json",
            json={"report_id": report_id},
        )
        mocker.get(
            "https://register.rockthevote.com/api/v4/registrant_reports/123",
            json={"download_url": "https://register.rockthevote.com/download/whatever"},
        )
        mocker.get(
            "https://register.rockthevote.com/download/whatever",
            text=(Path(_dir) / "sample.csv").read_text(),
        )

        rtv = RockTheVote(partner_id=partner_id, partner_api_key=partner_api_key)

        result = rtv.run_registration_report()
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result[0]["first_name"], "Carol")
        self.assertEqual(result[0]["last_name"], "King")

    @requests_mock.Mocker()
    def test_get_state_requirements(self, mocker):
        partner_id = "1"
        partner_api_key = "abcd"

        with (_dir / "sample.json").open(mode="r") as j:
            expected_json = json.load(j)

        mocker.get(
            "https://register.rockthevote.com/api/v4/state_requirements.json",
            json=expected_json,
        )

        rtv = RockTheVote(partner_id=partner_id, partner_api_key=partner_api_key)

        result = rtv.get_state_requirements("en", "fl", "33314")
        print(result.columns)

        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result[0]["requires_party"], True)
        self.assertEqual(result[0]["requires_race"], True)
