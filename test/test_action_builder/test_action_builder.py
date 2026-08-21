"""Tests for the ActionBuilder connector."""

import json

import pytest

from parsons import Table
from test.conftest import assert_matching_tables

EMPTY_TAGS = {"_embedded": {"osdi:tags": []}}
FAKE_ENTITY_ID = "fake-entity-id-1"
FAKE_SECTION = "Fake Section 1"


def all_tags(load) -> list:
    """The two tag pages concatenated — what a full fetch should return."""
    return (
        load("tags_list_1")["_embedded"]["osdi:tags"]
        + load("tags_list_2")["_embedded"]["osdi:tags"]
    )


def dict_key_intersection(dict1: dict, dict2: dict) -> tuple[dict, dict]:
    """Restrict both dicts to their common, non-list (non-nested) keys for comparison."""
    common = {k for k, v in dict1.items() if k in dict2 and not isinstance(v, list)}
    return ({k: dict1[k] for k in common}, {k: dict2[k] for k in common})


def tagging_callback(request, context):
    """Return the posted tag data, sorted for a predictable comparison."""
    return sorted(request.json()["add_tags"], key=lambda k: k["action_builder:name"])


def connect_callback(request, context):
    """Echo the posted connection data, stamping in an id parsed from the URL."""
    post_data = request.json()
    connection_data = post_data if request.method == "PUT" else post_data["connection"]

    url_pieces = [x for x in request.url.split("/") if x]
    if url_pieces.index("connections") == len(url_pieces) - 2:
        connection_data["identifiers"] = [f"action_builder:{url_pieces[-1]}"]
    return connection_data


def test_get_page_max_cap(bldr, api_url, campaign, requests_mock, load):
    """per_page is capped, so 25 and 26 request the same page."""
    requests_mock.get(f"{api_url}/tags?page=2&per_page=25", text=json.dumps(load("tags_list_2")))

    assert bldr._get_page(campaign, "tags", 2, per_page=25) == bldr._get_page(
        campaign, "tags", 2, per_page=26
    )


def test_get_page(bldr, api_url, campaign, requests_mock, load):
    tags_list_2 = load("tags_list_2")
    requests_mock.get(f"{api_url}/tags?page=2&per_page=2", text=json.dumps(tags_list_2))

    assert bldr._get_page(campaign, "tags", 2, 2) == tags_list_2


def _mock_two_tag_pages(requests_mock, api_url, load):
    requests_mock.get(f"{api_url}/tags?page=1&per_page=25", text=json.dumps(load("tags_list_1")))
    requests_mock.get(f"{api_url}/tags?page=2&per_page=25", text=json.dumps(load("tags_list_2")))
    requests_mock.get(f"{api_url}/tags?page=3&per_page=25", text=json.dumps(EMPTY_TAGS))


def test_get_all_records(bldr, api_url, campaign, requests_mock, load):
    _mock_two_tag_pages(requests_mock, api_url, load)

    assert_matching_tables(bldr._get_all_records(campaign, "tags"), Table(all_tags(load)))


def test_get_all_records_limit(bldr, api_url, campaign, requests_mock, load):
    _mock_two_tag_pages(requests_mock, api_url, load)

    assert_matching_tables(
        bldr._get_all_records(campaign, "tags", limit=2), Table(all_tags(load)[:2])
    )


def test_get_campaign_tags(bldr, api_url, requests_mock, load):
    _mock_two_tag_pages(requests_mock, api_url, load)

    assert_matching_tables(bldr.get_campaign_tags(), Table(all_tags(load)))


def test_get_tag_by_name(bldr, api_url, requests_mock, load):
    search_result = load("tag_name_search_result")
    requests_mock.get(f"{api_url}/tags?filter=name eq 'Fake Tag 1'", text=json.dumps(search_result))
    requests_mock.get(
        f"{api_url}/tags?page=2&per_page=25&filter=name eq 'Fake Tag 1'",
        text=json.dumps(EMPTY_TAGS),
    )

    assert_matching_tables(
        bldr.get_tag_by_name("Fake Tag 1"),
        Table([search_result["_embedded"]["osdi:tags"][0]]),
    )


def test_upsert_entity(bldr, api_url, campaign, requests_mock, load):
    requests_mock.post(f"{api_url}/people", text=json.dumps(load("upserted_response")))

    upsert_person = load("upsert_person")["person"]
    response = bldr._upsert_entity(load("upsert_person"), campaign)

    person_comp, response_comp = dict_key_intersection(upsert_person, response)
    email_comp, response_email_comp = dict_key_intersection(
        upsert_person["email_addresses"][0], response["email_addresses"][0]
    )

    assert person_comp == response_comp
    assert email_comp == response_email_comp


def test_insert_entity_record(bldr, api_url, requests_mock, load):
    requests_mock.post(f"{api_url}/people", text=json.dumps(load("upserted_response")))

    insert_arg = load("insert_person")
    expected = {
        **{k: v for k, v in insert_arg.items() if k != "data"},
        **insert_arg["data"]["person"],
    }
    response = bldr.insert_entity_record(**insert_arg)

    person_comp, response_comp = dict_key_intersection(expected, response)
    assert person_comp == response_comp


def test_update_entity_record(bldr, api_url, requests_mock, load):
    requests_mock.post(f"{api_url}/people", text=json.dumps(load("upserted_response")))

    update_arg = load("update_person")
    expected = {
        **{k: v for k, v in update_arg.items() if k != "data"},
        **update_arg["data"]["person"],
    }
    response = bldr.update_entity_record(**update_arg)

    person_comp, response_comp = dict_key_intersection(expected, response)
    assert person_comp == response_comp


def test_remove_entity_record_from_campaign(bldr, api_url, requests_mock):
    message = "{'message': 'Entity has been removed from the campaign'}"
    requests_mock.delete(f"{api_url}/people/{FAKE_ENTITY_ID}", json=message)

    assert bldr.remove_entity_record_from_campaign(FAKE_ENTITY_ID) == message


def test_add_section_field_values_to_record(bldr, api_url, requests_mock, load):
    requests_mock.post(f"{api_url}/people", json=tagging_callback)

    response = bldr.add_section_field_values_to_record(
        FAKE_ENTITY_ID, FAKE_SECTION, load("field_values")
    )

    assert response == load("tagging")


def test_remove_tagging(bldr, api_url, requests_mock, load):
    remove_resp = load("remove_tag_resp")
    requests_mock.delete(f"{api_url}/tags/fake_tag_id/taggings/fake_tagging_id", json=remove_resp)

    result = bldr.remove_tagging(tag_id="fake_tag_id", tagging_id="fake_tagging_id")

    assert result == remove_resp


def test_remove_tagging_missing_tag(bldr, api_url, requests_mock, load):
    requests_mock.delete(
        f"{api_url}/tags/fake_tag_id/taggings/fake_tagging_id", json=load("remove_tag_resp")
    )

    with pytest.raises(ValueError, match="Please supply a tag_name or tag_id"):
        bldr.remove_tagging(tag_id=None, tag_name=None, tagging_id="fake_tagging_id")


def test_remove_tagging_missing_identifiers(bldr, api_url, requests_mock, load):
    requests_mock.delete(
        f"{api_url}/tags/fake_tag_id/taggings/fake_tagging_id", json=load("remove_tag_resp")
    )

    with pytest.raises(
        ValueError, match="Please supply an entity or connection identifier, or a tagging id"
    ):
        bldr.remove_tagging(tag_id="fake_tag_id", tagging_id=None, identifier=None)


def test_upsert_connection(bldr, api_url, requests_mock, load):
    requests_mock.post(f"{api_url}/people/{FAKE_ENTITY_ID}/connections", json=connect_callback)
    connection = load("connection")

    response = bldr.upsert_connection([FAKE_ENTITY_ID, "fake-entity-id-2"])

    assert response == {
        **{k: v for k, v in connection.items() if k != "identifiers"},
        "inactive": False,
    }


def test_upsert_connection_missing_identifiers(bldr, api_url, requests_mock):
    requests_mock.post(f"{api_url}/people/{FAKE_ENTITY_ID}/connections", json=connect_callback)

    with pytest.raises(ValueError, match="Must provide identifiers as a list"):
        bldr.upsert_connection(FAKE_ENTITY_ID)
    with pytest.raises(ValueError, match="Must provide exactly two identifiers"):
        bldr.upsert_connection([FAKE_ENTITY_ID])
    with pytest.raises(ValueError, match="Must provide exactly two identifiers"):
        bldr.upsert_connection([FAKE_ENTITY_ID, "fake-entity-id-2", "fake-entity-id-3"])


def test_upsert_connection_tag_data(bldr, api_url, requests_mock):
    requests_mock.post(f"{api_url}/people/{FAKE_ENTITY_ID}/connections", json=connect_callback)

    with pytest.raises(ValueError, match="Must provide tag_data as a dict or list of dicts"):
        bldr.upsert_connection([FAKE_ENTITY_ID, "fake-entity-id-2"], tag_data=["string", "yarn"])


def test_upsert_connection_reactivate(bldr, api_url, requests_mock):
    requests_mock.post(f"{api_url}/people/{FAKE_ENTITY_ID}/connections", json=connect_callback)

    reactivated = bldr.upsert_connection([FAKE_ENTITY_ID, "fake-entity-id-2"], reactivate=True)
    assert not reactivated["inactive"]

    not_reactivated = bldr.upsert_connection([FAKE_ENTITY_ID, "fake-entity-id-2"], reactivate=False)
    assert "inactive" not in not_reactivated


def test_deactivate_connection_post(bldr, api_url, requests_mock, load):
    requests_mock.post(f"{api_url}/people/{FAKE_ENTITY_ID}/connections", json=connect_callback)
    connection = load("connection")

    response = bldr.deactivate_connection(FAKE_ENTITY_ID, to_identifier="fake-entity-id-2")

    assert response == {
        **{k: v for k, v in connection.items() if k != "identifiers"},
        "inactive": True,
    }


def test_deactivate_connection_put(bldr, api_url, requests_mock, load):
    endpoint = f"{api_url}/people/{FAKE_ENTITY_ID}/connections/fake-connection-id"
    requests_mock.put(endpoint, json=connect_callback)
    connection = load("connection")

    response = bldr.deactivate_connection(
        FAKE_ENTITY_ID, connection_identifier="fake-connection-id"
    )

    assert response == {
        **{k: v for k, v in connection.items() if k != "person_id"},
        "inactive": True,
    }


def test_deactivate_connection_missing_identifiers(bldr, api_url, requests_mock):
    requests_mock.post(f"{api_url}/people/{FAKE_ENTITY_ID}/connections", json=connect_callback)

    with pytest.raises(
        ValueError, match="Must provide a connection ID or an ID for the second entity"
    ):
        bldr.deactivate_connection(FAKE_ENTITY_ID, to_identifier=None)
