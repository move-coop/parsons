import logging
import os
import unittest
import unittest.mock as mock

from parsons import Alchemer

logger = logging.getLogger(__name__)


class TestAlchemErGetResponses(unittest.TestCase):
    def setUp(self):
        os.environ["ALCHEMER_API_TOKEN"] = "MYFAKEAPITOKEN"
        os.environ["ALCHEMER_API_TOKEN_SECRET"] = "MYFAKETOKENSECRET"
        os.environ["ALCHEMER_API_VERSION"] = "MYFAKEVERSION"

        self.alchemer = Alchemer()
        self.alchemer._client = mock.MagicMock()

        self.test_survey_id = "1234567"

    def test_adds_survey_id(self):
        api_return = self._get_responses_return_single_page()
        self.alchemer._client.api.surveyresponse.list.return_value = api_return

        actual_responses = self.alchemer.get_survey_responses(self.test_survey_id)

        assert self.test_survey_id, actual_responses["survey_id"]

    def test_get_responses_single_page(self):
        api_return = self._get_responses_return_single_page()
        self.alchemer._client.api.surveyresponse.list.return_value = api_return

        actual_responses = self.alchemer.get_survey_responses(self.test_survey_id)

        assert actual_responses.num_rows == 2
        for i in range(0, 1):
            assert api_return["data"][i]["session_id"] == actual_responses[i]["session_id"]

    def _get_responses_return_single_page(self):
        return {
            "result_ok": True,
            "total_count": 2,
            "page": 1,
            "total_pages": 1,
            "results_per_page": 50,
            "data": [
                {
                    "id": "1",
                    "contact_id": "",
                    "status": "Complete",
                    "is_test_data": "0",
                    "date_submitted": "2018-09-27 10:42:26 EDT",
                    "session_id": "1538059336_5bacec4869caa2.27680217",
                    "language": "English",
                    "date_started": "2018-09-27 10:42:16 EDT",
                    "link_id": "7473882",
                    "url_variables": [],
                    "ip_address": "50.232.185.226",
                    "referer": "https://app.surveygizmo.com/distribute/share/id/4599075",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
                    "response_time": 10,
                    "data_quality": [],
                    "longitude": "-105.20369720459",
                    "latitude": "40.050701141357",
                    "country": "United States",
                    "city": "Boulder",
                    "region": "CO",
                    "postal": "80301",
                    "dma": "751",
                    "survey_data": {
                        "2": {
                            "id": 2,
                            "type": "RADIO",
                            "question": "Will you attend the event?",
                            "section_id": 1,
                            "original_answer": "Yes",
                            "answer": "1",
                            "answer_id": 10001,
                            "shown": True,
                        },
                        "3": {
                            "id": 3,
                            "type": "TEXTBOX",
                            "question": "How many guests will you bring?",
                            "section_id": 1,
                            "answer": "3",
                            "shown": True,
                        },
                        "4": {
                            "id": 4,
                            "type": "TEXTBOX",
                            "question": "How many guests are under the age of 18?",
                            "section_id": 1,
                            "answer": "2",
                            "shown": True,
                        },
                    },
                },
                {
                    "id": "2",
                    "contact_id": "",
                    "status": "Complete",
                    "is_test_data": "0",
                    "date_submitted": "2018-09-27 10:43:11 EDT",
                    "session_id": "1538059381_5bacec751e41f4.51482165",
                    "language": "English",
                    "date_started": "2018-09-27 10:43:01 EDT",
                    "link_id": "7473882",
                    "url_variables": {
                        "__dbget": {"key": "__dbget", "value": "True", "type": "url"}
                    },
                    "ip_address": "50.232.185.226",
                    "referer": "",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
                    "response_time": 10,
                    "data_quality": [],
                    "longitude": "-105.20369720459",
                    "latitude": "40.050701141357",
                    "country": "United States",
                    "city": "Boulder",
                    "region": "CO",
                    "postal": "80301",
                    "dma": "751",
                    "survey_data": {
                        "2": {
                            "id": 2,
                            "type": "RADIO",
                            "question": "Will you attend the event?",
                            "section_id": 1,
                            "original_answer": "1",
                            "answer": "1",
                            "answer_id": 10001,
                            "shown": True,
                        },
                        "3": {
                            "id": 3,
                            "type": "TEXTBOX",
                            "question": "How many guests will you bring?",
                            "section_id": 1,
                            "answer": "2",
                            "shown": True,
                        },
                        "4": {
                            "id": 4,
                            "type": "TEXTBOX",
                            "question": "How many guests are under the age of 18?",
                            "section_id": 1,
                            "answer": "0",
                            "shown": True,
                        },
                    },
                },
            ],
        }
