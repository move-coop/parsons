"""Tests for the RockTheVote connector."""

import json

RTV_API = "https://register.rockthevote.com/api/v4"
DOWNLOAD_URL = "https://register.rockthevote.com/download/whatever"


def test_create_registration_report(rtv, requests_mock):
    requests_mock.post(f"{RTV_API}/registrant_reports.json", json={"report_id": "123"})

    assert rtv.create_registration_report() == "123"


def test_get_registration_report(rtv, requests_mock, shared_datadir):
    requests_mock.get(f"{RTV_API}/registrant_reports/1", json={"download_url": DOWNLOAD_URL})
    requests_mock.get(DOWNLOAD_URL, text=(shared_datadir / "registration_report.csv").read_text())

    result = rtv.get_registration_report(report_id=1)

    assert result.num_rows == 1
    assert result[0]["first_name"] == "Carol"
    assert result[0]["last_name"] == "King"


def test_run_registration_report(rtv, requests_mock, shared_datadir):
    requests_mock.post(f"{RTV_API}/registrant_reports.json", json={"report_id": "123"})
    requests_mock.get(f"{RTV_API}/registrant_reports/123", json={"download_url": DOWNLOAD_URL})
    requests_mock.get(DOWNLOAD_URL, text=(shared_datadir / "registration_report.csv").read_text())

    result = rtv.run_registration_report()

    assert result.num_rows == 1
    assert result[0]["first_name"] == "Carol"
    assert result[0]["last_name"] == "King"


def test_get_state_requirements(rtv, requests_mock, shared_datadir):
    expected = json.loads((shared_datadir / "state_requirements.json").read_text())
    requests_mock.get(f"{RTV_API}/state_requirements.json", json=expected)

    result = rtv.get_state_requirements("en", "fl", "33314")

    assert result.num_rows == 1
    assert result[0]["requires_party"]
    assert result[0]["requires_race"]
