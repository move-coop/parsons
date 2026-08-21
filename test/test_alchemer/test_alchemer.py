"""Tests for the Alchemer connector.

Alchemer wraps a third-party ``surveygizmo.SurveyGizmo`` client, so that client is the
boundary we mock (see the ``alchemer`` fixture in conftest.py). The connector's own
paging and table-shaping logic runs for real. Canned API responses live in ``data/``.
"""

from copy import deepcopy
from unittest.mock import call


def _page(single, page, total_pages, rows):
    """Build one page of a paginated surveygizmo response from the single-page fixture."""
    payload = deepcopy(single)
    payload.update(page=page, total_pages=total_pages, data=rows)
    return payload


# --- get_surveys -----------------------------------------------------------------


def test_get_surveys_single_page(alchemer, load):
    surveys = load("surveys_single_page")
    alchemer._client.api.survey.list.return_value = surveys

    tbl = alchemer.get_surveys()

    assert tbl.num_rows == 2
    assert tbl["title"] == [row["title"] for row in surveys["data"]]
    assert tbl["id"] == ["1234567", "1234568"]
    # No page requested -> the whole first (and only) page is fetched with page=None.
    assert alchemer._client.api.survey.list.call_args_list == [call(None)]


def test_get_surveys_removes_links_and_unpacks_statistics(alchemer, load):
    alchemer._client.api.survey.list.return_value = load("surveys_single_page")

    tbl = alchemer.get_surveys()

    # The links column is dropped and the statistics dict is unpacked into columns.
    assert "links" not in tbl.columns
    assert "statistics" not in tbl.columns
    assert tbl["Partial"] == [4, 1]
    assert tbl["Complete"] == [2, None]


def test_get_surveys_paginates(alchemer, load):
    single = load("surveys_single_page")
    page_1 = _page(single, page=1, total_pages=2, rows=[single["data"][0]])
    page_2 = _page(single, page=2, total_pages=2, rows=[single["data"][1]])
    alchemer._client.api.survey.list.side_effect = [page_1, page_2]

    tbl = alchemer.get_surveys()

    # Both pages are fetched and concatenated.
    assert tbl.num_rows == 2
    assert tbl["id"] == ["1234567", "1234568"]
    assert alchemer._client.api.survey.list.call_args_list == [call(None), call(page=2)]


def test_get_surveys_specific_page_skips_pagination(alchemer, load):
    # total_pages=5, but an explicit page means only that page is fetched.
    single = load("surveys_single_page")
    alchemer._client.api.survey.list.return_value = _page(
        single, page=2, total_pages=5, rows=single["data"]
    )

    alchemer.get_surveys(page=2)

    assert alchemer._client.api.survey.list.call_args_list == [call(2)]


# --- get_survey_responses --------------------------------------------------------


def test_get_survey_responses_single_page(alchemer, load):
    responses = load("responses_single_page")
    alchemer._client.api.surveyresponse.list.return_value = responses

    tbl = alchemer.get_survey_responses("1234567")

    assert tbl.num_rows == 2
    assert tbl["session_id"] == [row["session_id"] for row in responses["data"]]
    assert alchemer._client.api.surveyresponse.list.call_args_list == [call("1234567", None)]


def test_get_survey_responses_adds_survey_id_column(alchemer, load):
    alchemer._client.api.surveyresponse.list.return_value = load("responses_single_page")

    tbl = alchemer.get_survey_responses("1234567")

    # survey_id is added for every row, as the second column (index=1).
    assert tbl["survey_id"] == ["1234567", "1234567"]
    assert tbl.columns[1] == "survey_id"


def test_get_survey_responses_paginates(alchemer, load):
    single = load("responses_single_page")
    page_1 = _page(single, page=1, total_pages=2, rows=[single["data"][0]])
    page_2 = _page(single, page=2, total_pages=2, rows=[single["data"][1]])
    alchemer._client.api.surveyresponse.list.side_effect = [page_1, page_2]

    tbl = alchemer.get_survey_responses("1234567")

    assert tbl.num_rows == 2
    assert tbl["id"] == ["1", "2"]
    assert alchemer._client.api.surveyresponse.list.call_args_list == [
        call("1234567", None),
        call("1234567", page=2),
    ]


def test_get_survey_responses_specific_page_skips_pagination(alchemer, load):
    single = load("responses_single_page")
    alchemer._client.api.surveyresponse.list.return_value = _page(
        single, page=2, total_pages=5, rows=single["data"]
    )

    alchemer.get_survey_responses("1234567", page=2)

    assert alchemer._client.api.surveyresponse.list.call_args_list == [call("1234567", 2)]
