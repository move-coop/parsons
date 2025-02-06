import unittest
import requests_mock
from parsons.formstack.formstack import Formstack, API_URI
from parsons import Table

from test.test_formstack.formstack_json import (
    folder_json,
    form_json,
    submission_id,
    submission_json,
    form_submissions_json,
    form_fields_json,
)

VALID_RESPONSE_STATUS_CODE = 200


class TestFormstack(unittest.TestCase):
    @requests_mock.Mocker()
    def test_get_folders(self, m):
        fs = Formstack(api_token="token")
        m.get(
            API_URI + "/folder",
            status_code=VALID_RESPONSE_STATUS_CODE,
            json=folder_json,
        )
        folders_data = fs.get_folders()
        self.assertIsInstance(folders_data, Table)

    @requests_mock.Mocker()
    def test_get_forms(self, m):
        fs = Formstack(api_token="token")
        m.get(
            API_URI + "/form",
            status_code=VALID_RESPONSE_STATUS_CODE,
            json=form_json,
        )
        forms_data = fs.get_forms()
        self.assertIsInstance(forms_data, Table)

    @requests_mock.Mocker()
    def test_get_submission(self, m):
        fs = Formstack(api_token="token")
        m.get(
            API_URI + f"/submission/{submission_id}",
            status_code=VALID_RESPONSE_STATUS_CODE,
            json=submission_json,
        )
        submission_data = fs.get_submission(submission_id)
        self.assertIsInstance(submission_data, dict)

    @requests_mock.Mocker()
    def test_get_form_submissions(self, m):
        fs = Formstack(api_token="token")
        m.get(
            API_URI + f"/form/{submission_id}/submission",
            status_code=VALID_RESPONSE_STATUS_CODE,
            json=form_submissions_json,
        )
        form_submissions_data = fs.get_form_submissions(submission_id)
        self.assertIsInstance(form_submissions_data, Table)

    @requests_mock.Mocker()
    def test_get_form_fields(self, m):
        fs = Formstack(api_token="token")
        form_id = 123
        m.get(
            API_URI + f"/form/{form_id}/field",
            status_code=VALID_RESPONSE_STATUS_CODE,
            json=form_fields_json,
        )
        form_fields_data = fs.get_form_fields(form_id)
        self.assertIsInstance(form_fields_data, Table)
