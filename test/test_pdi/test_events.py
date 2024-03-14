from test.utils import mark_live_test
from parsons import Table

#####

START_DATE = "2020-01-01"
END_DATE = "2022-12-31"
EXPAND = True
LOWER_LIMIT = 1

# TODO: Invoke this, it should fail as 2000 is the max limit for
# all of the relevant events functions
UPPER_LIMIT = 2001


@mark_live_test
def test_get_calendars(live_pdi):
    response = live_pdi.get_calendars()

    assert isinstance(response, Table)


@mark_live_test
def test_get_calendars_with_limit(live_pdi):
    response = live_pdi.get_calendars(limit=LOWER_LIMIT)

    assert response.num_rows == 1


@mark_live_test
def test_get_event_activities(live_pdi):
    response = live_pdi.get_event_activities(start_date=START_DATE, end_date=END_DATE)

    assert isinstance(response, Table)


@mark_live_test
def test_get_event_activities_with_limit(live_pdi):
    response = live_pdi.get_event_activities(
        start_date=START_DATE, end_date=END_DATE, limit=LOWER_LIMIT
    )

    assert response.num_rows == 1


@mark_live_test
def test_get_event_activity_assignments(live_pdi):
    response = live_pdi.get_event_activity_assignments(
        start_date=START_DATE, end_date=END_DATE, expand=EXPAND
    )

    assert isinstance(response, Table)


@mark_live_test
def test_get_event_activity_assignments_with_limit(live_pdi):
    response = live_pdi.get_event_activity_assignments(
        start_date=START_DATE, end_date=END_DATE, expand=EXPAND
    )

    assert response.num_rows == 1
