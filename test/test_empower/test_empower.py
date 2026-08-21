"""Tests for the Empower connector.

Empower exposes one export endpoint; each ``get_*`` method reshapes a slice of
that cached payload, so these tests assert the resulting Table columns.
"""

import pytest

from parsons import Table

PROFILE_COLUMNS = [
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

CTA_COLUMNS = [
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


@pytest.mark.parametrize(
    ("method", "expected_columns"),
    [
        ("get_profiles", PROFILE_COLUMNS),
        ("get_profiles_active_ctas", ["eid", "activeCtaIds"]),
        ("get_ctas", CTA_COLUMNS),
        (
            "get_cta_results",
            [
                "profileEid",
                "ctaId",
                "contactedMts",
                "notes",
                "answerIdsByPromptId",
                "answer_id",
            ],
        ),
        (
            "get_cta_prompts",
            [
                "id",
                "answerInputType",
                "dependsOnInitialDispositionResponse",
                "id",
                "isDeleted",
                "ordering",
                "promptText",
                "vanId",
            ],
        ),
        (
            "get_cta_prompt_answers",
            ["id", "answerText", "id", "isDeleted", "ordering", "promptId", "vanId"],
        ),
        ("get_cta_regions", ["id", "regionIds"]),
        (
            "get_cta_shareables",
            ["id", "shareables_displayLabel", "shareables_type", "shareables_url"],
        ),
        ("get_cta_prioritizations", ["id", "prioritizations"]),
    ],
)
def test_export_slices_have_expected_columns(empower, method, expected_columns):
    assert getattr(empower, method)().columns == expected_columns


def test_get_regions(empower, export_data):
    assert empower.get_regions().columns == Table(export_data["regions"]).columns


def test_export_is_fetched_once_at_construction(empower, requests_mock):
    """The connector caches the export; reading slices makes no further requests."""
    before = len(requests_mock.request_history)

    empower.get_profiles()
    empower.get_ctas()

    assert len(requests_mock.request_history) == before
