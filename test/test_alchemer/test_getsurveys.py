import logging
import os
import unittest
import unittest.mock as mock

from parsons import Alchemer

logger = logging.getLogger(__name__)

# Relevant links
# V5 API Documentation https://apihelp.alchemer.com/help/version-5


class TestAlchemErGetSurveys(unittest.TestCase):
    def setUp(self):
        os.environ["ALCHEMER_API_TOKEN"] = "MYFAKEAPITOKEN"
        os.environ["ALCHEMER_API_TOKEN_SECRET"] = "MYFAKETOKENSECRET"
        os.environ["ALCHEMER_API_VERSION"] = "MYFAKEVERSION"

        self.alchemer = Alchemer()
        self.alchemer._client = mock.MagicMock()

    def test_get_surveys_single_page(self):
        api_return = self._get_surveys_return_single_page()
        self.alchemer._client.api.survey.list.return_value = api_return

        actual_surveys = self.alchemer.get_surveys()

        assert actual_surveys.num_rows == 2
        for i in range(0, 1):
            assert api_return["data"][i]["title"] == actual_surveys[i]["title"]

    def test_removes_links_field(self):
        api_return = self._get_surveys_return_single_page()
        self.alchemer._client.api.survey.list.return_value = api_return

        actual_surveys = self.alchemer.get_surveys()

        assert "links" not in actual_surveys.columns

    def _get_surveys_return_single_page(self):
        return {
            "result_ok": True,
            "total_count": "1461",
            "page": 1,
            "total_pages": 1,
            "results_per_page": 50,
            "data": [
                {
                    "id": "1234567",
                    "team": "433737",
                    "type": "Standard Survey",
                    "status": "Launched",
                    "created_on": "2017-04-24 10:44:23",
                    "modified_on": "2017-04-24 10:58:20",
                    "title": "Survey",
                    "statistics": {"Partial": 4, "Complete": 2},
                    "links": {
                        "edit": "[Link to Build Tab]",
                        "publish": "[Link to Share Tab]",
                        "default": "[Default Share Link]",
                    },
                },
                {
                    "id": "1234568",
                    "team": "433737",
                    "type": "Standard Survey",
                    "status": "Launched",
                    "created_on": "2017-04-24 09:53:01",
                    "modified_on": "2017-04-24 09:53:55",
                    "title": "Survey",
                    "statistics": {"Partial": 1},
                    "links": {
                        "edit": "[Link to Build Tab]",
                        "publish": "[Link to Share Tab]",
                        "default": "[Default Share Link]",
                    },
                },
            ],
        }
