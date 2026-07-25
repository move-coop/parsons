"""Tests for the QuickBooks Time connector.

Each ``get_*`` method fetches a page and flattens the id-keyed ``results`` dict
into a Table, so the tests assert the first row's id matches the payload.
"""

from requests_mock import ANY

from parsons.etl.table import Table


def _first_id(payload: dict, collection: str):
    """The id of the first record in a QuickBooks Time ``results`` collection."""
    return next(iter(payload["results"][collection].values()))["id"]


def test_qb_get_request(quickbooks, requests_mock, load):
    groups = load("groups")
    requests_mock.get(ANY, json=groups)

    result = quickbooks.qb_get_request(end_point="groups", querystring={"page": 1})

    assert isinstance(result, Table)
    assert len(result) > 0
    assert result[0]["id"] == _first_id(groups, "groups")


def test_get_groups(quickbooks, requests_mock, load):
    groups = load("groups")
    requests_mock.get(ANY, json=groups)

    result = quickbooks.get_groups()

    assert result[0]["id"] == _first_id(groups, "groups")


def test_get_jobcodes(quickbooks, requests_mock, load):
    jobcodes = load("jobcodes")
    requests_mock.get(ANY, json=jobcodes)

    result = quickbooks.get_jobcodes()

    assert result[0]["id"] == _first_id(jobcodes, "jobcodes")


def test_get_timesheets(quickbooks, requests_mock, load):
    timesheets = load("timesheets")
    requests_mock.get(ANY, json=timesheets)

    result = quickbooks.get_timesheets()

    assert result[0]["id"] == _first_id(timesheets, "timesheets")


def test_get_users(quickbooks, requests_mock, load):
    users = load("users")
    requests_mock.get(ANY, json=users)

    result = quickbooks.get_users()

    assert result[0]["id"] == _first_id(users, "users")


def test_get_schedule_calendars_list(quickbooks, requests_mock, load):
    requests_mock.get(ANY, json=load("schedule_calendars_list"))

    result = quickbooks.get_schedule_calendars_list()

    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], int)


def test_get_schedule_events(quickbooks, requests_mock, load):
    events = load("schedule_events")
    requests_mock.get(ANY, json=events)

    result = quickbooks.get_schedule_events()

    assert result[0]["id"] == _first_id(events, "schedule_events")


def test_get_geolocations(quickbooks, requests_mock, load):
    geolocations = load("geolocations")
    requests_mock.get(ANY, json=geolocations)

    result = quickbooks.get_geolocations()

    assert result[0]["id"] == _first_id(geolocations, "geolocations")


def test_get_jobcodes_with_params(quickbooks, requests_mock, load):
    jobcodes = load("jobcodes")
    requests_mock.get(ANY, json=jobcodes)

    result = quickbooks.get_jobcodes(
        ids=[1, 2, 3],
        parent_ids=[4, 5, 6],
        name="test",
        type="test",
        active=True,
        customfields={"test": "test"},
        modified_before="2022-01-01",
        modified_since="2022-01-01",
        supplemental_data=True,
        limit=10,
        page=1,
    )

    assert result[0]["id"] == _first_id(jobcodes, "jobcodes")


def test_get_users_with_params(quickbooks, requests_mock, load):
    users = load("users")
    requests_mock.get(ANY, json=users)

    result = quickbooks.get_users(
        ids=[1, 2, 3],
        not_ids=[4, 5, 6],
        employee_numbers=[7, 8, 9],
        usernames=["test1", "test2", "test3"],
        group_ids=[10, 11, 12],
        not_group_ids=[13, 14, 15],
        payroll_ids=[16, 17, 18],
        active=True,
        first_name="test",
        last_name="test",
        modified_before="2022-01-01",
        modified_since="2022-01-01",
        supplemental_data=True,
        limit=10,
        page=1,
    )

    assert result[0]["id"] == _first_id(users, "users")


def test_get_timesheets_with_params(quickbooks, requests_mock, load):
    timesheets = load("timesheets")
    requests_mock.get(ANY, json=timesheets)

    result = quickbooks.get_timesheets(
        ids=[1, 2, 3],
        jobcode_ids=[4, 5, 6],
        payroll_ids=[7, 8, 9],
        user_ids=[10, 11, 12],
        group_ids=[13, 14, 15],
        end_date="2022-01-01",
        on_the_clock=True,
        jobcode_type="test",
        modified_before="2022-01-01",
        modified_since="2022-01-01",
        supplemental_data=True,
        limit=10,
        page=1,
        start_date="2022-01-01",
    )

    assert result[0]["id"] == _first_id(timesheets, "timesheets")


def test_get_schedule_events_with_params(quickbooks, requests_mock, load):
    events = load("schedule_events")
    requests_mock.get(ANY, json=events)

    result = quickbooks.get_schedule_events(
        ids=[1, 2, 3],
        users_ids=[4, 5, 6],
        schedule_calendar_ids=[7, 8, 9],
        jobcode_ids=[10, 11, 12],
        start="2022-01-01",
        end="2022-01-01",
        active_users=True,
        active=True,
        draft=True,
        team_events=True,
        modified_before="2022-01-01",
        modified_since="2022-01-01",
        supplemental_data=True,
        limit=10,
    )

    assert result[0]["id"] == _first_id(events, "schedule_events")
