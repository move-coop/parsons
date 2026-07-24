"""Tests for the Formstack connector."""

from parsons import Table
from parsons.formstack.formstack import API_URI

SUBMISSION_ID = 332525567


def test_get_folders(formstack, requests_mock, load):
    requests_mock.get(f"{API_URI}/folder", json=load("folder"))

    tbl = formstack.get_folders()

    assert isinstance(tbl, Table)
    assert tbl.num_rows == 5
    assert tbl.columns == ["id", "name", "parent", "permissions"]


def test_get_forms(formstack, requests_mock, load):
    requests_mock.get(f"{API_URI}/form", json=load("form"))

    tbl = formstack.get_forms()

    assert isinstance(tbl, Table)
    assert tbl.num_rows == 2
    assert "id" in tbl.columns


def test_get_submission(formstack, requests_mock, load):
    submission = load("submission")
    requests_mock.get(f"{API_URI}/submission/{SUBMISSION_ID}", json=submission)

    result = formstack.get_submission(SUBMISSION_ID)

    assert result == submission


def test_get_form_submissions(formstack, requests_mock, load):
    requests_mock.get(f"{API_URI}/form/{SUBMISSION_ID}/submission", json=load("form_submissions"))

    tbl = formstack.get_form_submissions(SUBMISSION_ID)

    assert isinstance(tbl, Table)


def test_get_form_fields(formstack, requests_mock, load):
    form_id = 123
    requests_mock.get(f"{API_URI}/form/{form_id}/field", json=load("form_fields"))

    tbl = formstack.get_form_fields(form_id)

    assert isinstance(tbl, Table)
    assert tbl.num_rows == 2
    assert "label" in tbl.columns
