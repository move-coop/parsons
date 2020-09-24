import os
import unittest
import unittest.mock as mock
from parsons.surveygizmo.surveygizmo import SurveyGizmo, Table
import logging

logger = logging.getLogger(__name__)

class TestSurveyGizmoGetResponses(unittest.TestCase):
    def setUp(self):
        os.environ['SURVEYGIZMO_API_TOKEN'] = 'MYFAKEAPITOKEN'
        os.environ['SURVEYGIZMO_API_TOKEN_SECRET'] = 'MYFAKETOKENSECRET'
        os.environ['SURVEYGIZMO_API_VERSION'] = 'MYFAKEVERSION'

        self.surveygizmo = SurveyGizmo()
        self.surveygizmo._client = mock.MagicMock()

    def test_foo(self):
        pass
