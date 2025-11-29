import unittest

import requests_mock

from parsons import Empower, Table
from test.test_empower.dummy_empower_data import dummy_data

TEST_EMPOWER_API_KEY = "MYKEY"
EMPOWER_API_ENDPOINT = "https://api.getempower.com/v1/export"


class TestEmpower(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        m.get(EMPOWER_API_ENDPOINT, json=dummy_data)
        self.empower = Empower(api_key=TEST_EMPOWER_API_KEY)

    @requests_mock.Mocker()
    def test_get_profiles(self, m):
        exp_columns = [
            "eid",
            "parentEid",
            "role",
            "firstName",
            "lastName",
            "email",
            "phone",
            "city",
            "state",
            "zip",
            "address",
            "address2",
            "vanId",
            "myCampaignVanId",
            "lastUsedEmpowerMts",
            "notes",
            "regionId",
            "createdMts",
            "updatedMts",
            "currentCtaId",
        ]

        assert self.empower.get_profiles().columns == exp_columns

    @requests_mock.Mocker()
    def test_get_profiles_active_ctas(self, m):
        exp_columns = ["eid", "activeCtaIds"]

        assert self.empower.get_profiles_active_ctas().columns == exp_columns

    @requests_mock.Mocker()
    def test_get_regions(self, m):
        exp_columns = Table(dummy_data["regions"]).columns

        assert self.empower.get_regions().columns == exp_columns

    @requests_mock.Mocker()
    def test_get_cta_results(self, m):
        exp_columns = [
            "profileEid",
            "ctaId",
            "contactedMts",
            "notes",
            "answerIdsByPromptId",
            "answer_id",
        ]

        assert self.empower.get_cta_results().columns == exp_columns

    @requests_mock.Mocker()
    def test_get_ctas(self, m):
        exp_columns = [
            "id",
            "name",
            "description",
            "instructionsHtml",
            "createdMts",
            "updatedMts",
            "organizationId",
            "recruitmentQuestionType",
            "recruitmentTrainingUrl",
            "isIntroCta",
            "scheduledLaunchTimeMts",
            "activeUntilMts",
            "shouldUseAdvancedTargeting",
            "advancedTargetingFilter",
            "defaultPriorityLabelKey",
            "actionType",
            "spokeCampaignId",
            "textCanvassingType",
            "turfCuttingType",
            "conversationStarter",
            "isPersonal",
            "isGeocodingDone",
            "customRecruitmentPromptText",
            "isBatchImportDone",
            "hasAssignableTurfs",
            "associatedElectionId",
            "shouldDisplayElectionDayPollingLocation",
            "shouldDisplayEarlyVotingPollingLocation",
            "shouldShowMatchButton",
        ]

        assert self.empower.get_ctas().columns == exp_columns

    @requests_mock.Mocker()
    def test_get_cta_prompts(self, m):
        exp_columns = [
            "id",
            "answerInputType",
            "dependsOnInitialDispositionResponse",
            "id",
            "isDeleted",
            "ordering",
            "promptText",
            "vanId",
        ]

        assert self.empower.get_cta_prompts().columns == exp_columns

    @requests_mock.Mocker()
    def test_get_cta_prompt_answers(self, m):
        exp_columns = [
            "id",
            "answerText",
            "id",
            "isDeleted",
            "ordering",
            "promptId",
            "vanId",
        ]

        assert self.empower.get_cta_prompt_answers().columns == exp_columns

    @requests_mock.Mocker()
    def test_get_cta_regions(self, m):
        exp_columns = ["id", "regionIds"]

        assert self.empower.get_cta_regions().columns == exp_columns

    @requests_mock.Mocker()
    def test_get_cta_shareables(self, m):
        exp_columns = [
            "id",
            "shareables_displayLabel",
            "shareables_type",
            "shareables_url",
        ]

        assert self.empower.get_cta_shareables().columns == exp_columns

    @requests_mock.Mocker()
    def test_get_cta_prioritizations(self, m):
        exp_columns = ["id", "prioritizations"]

        assert self.empower.get_cta_prioritizations().columns == exp_columns
