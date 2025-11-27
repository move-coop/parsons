import unittest

import requests_mock
from test_quickbookstime_data import (
    mock_geolocations_data,
    mock_groups_data,
    mock_jobcodes_data,
    mock_schedule_calendars_list_data,
    mock_schedule_events_data,
    mock_timesheets_data,
    mock_users_data,
)

from parsons.etl.table import Table
from parsons.quickbooks.quickbookstime import QuickBooksTime


class TestQuickBooksTime(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, mock_request):
        self.qb = QuickBooksTime(token="abc123")
        self.qb.url = "https://rest.tsheets.com/api/v1/"

    def tearDown(self):
        pass

    @requests_mock.Mocker()
    def test_qb_get_request(self, mock_request, end_point="groups"):  # noqa PT028
        # Arrange

        querystring = {"page": 1}
        mock_request.get(requests_mock.ANY, json=mock_groups_data)

        # Act
        result = self.qb.qb_get_request(end_point=end_point, querystring=querystring)

        # Assert
        assert isinstance(result, Table)
        assert isinstance(end_point, str)
        assert isinstance(querystring, dict)
        assert len(result) > 0
        assert result[0]["id"] == list(mock_groups_data["results"]["groups"].values())[0]["id"]

    @requests_mock.Mocker()
    def test_get_groups(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_groups_data)

        # Act
        result = self.qb.get_groups()

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert result[0]["id"] == list(mock_groups_data["results"]["groups"].values())[0]["id"]

    @requests_mock.Mocker()
    def test_get_jobcodes(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_jobcodes_data)

        # Act
        result = self.qb.get_jobcodes()

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert result[0]["id"] == list(mock_jobcodes_data["results"]["jobcodes"].values())[0]["id"]

    @requests_mock.Mocker()
    def test_get_timesheets(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_timesheets_data)

        # Act
        result = self.qb.get_timesheets()

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert (
            result[0]["id"] == list(mock_timesheets_data["results"]["timesheets"].values())[0]["id"]
        )

    @requests_mock.Mocker()
    def test_get_users(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_users_data)

        # Act
        result = self.qb.get_users()

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert result[0]["id"] == list(mock_users_data["results"]["users"].values())[0]["id"]

    @requests_mock.Mocker()
    def test_get_schedule_calendars_list(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_schedule_calendars_list_data)

        # Act
        result = self.qb.get_schedule_calendars_list()

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        # assert that the result is a list of ints
        assert isinstance(result[0], int)

    @requests_mock.Mocker()
    def test_get_schedule_events(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_schedule_events_data)

        # Act
        result = self.qb.get_schedule_events()

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert (
            result[0]["id"]
            == list(mock_schedule_events_data["results"]["schedule_events"].values())[0]["id"]
        )

    @requests_mock.Mocker()
    def test_get_jobcodes_with_params(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_jobcodes_data)
        ids = [1, 2, 3]
        parent_ids = [4, 5, 6]
        name = "test"
        type = "test"
        active = True
        customfields = {"test": "test"}
        modified_before = "2022-01-01"
        modified_since = "2022-01-01"
        supplemental_data = True
        limit = 10
        page = 1

        # Act
        result = self.qb.get_jobcodes(
            ids=ids,
            parent_ids=parent_ids,
            name=name,
            type=type,
            active=active,
            customfields=customfields,
            modified_before=modified_before,
            modified_since=modified_since,
            supplemental_data=supplemental_data,
            limit=limit,
            page=page,
        )

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert result[0]["id"] == list(mock_jobcodes_data["results"]["jobcodes"].values())[0]["id"]

    @requests_mock.Mocker()
    def test_get_users_with_params(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_users_data)
        ids = [1, 2, 3]
        not_ids = [4, 5, 6]
        employee_numbers = [7, 8, 9]
        usernames = ["test1", "test2", "test3"]
        group_ids = [10, 11, 12]
        not_group_ids = [13, 14, 15]
        payroll_ids = [16, 17, 18]
        active = True
        first_name = "test"
        last_name = "test"
        modified_before = "2022-01-01"
        modified_since = "2022-01-01"
        supplemental_data = True
        limit = 10
        page = 1

        # Act
        result = self.qb.get_users(
            ids=ids,
            not_ids=not_ids,
            employee_numbers=employee_numbers,
            usernames=usernames,
            group_ids=group_ids,
            not_group_ids=not_group_ids,
            payroll_ids=payroll_ids,
            active=active,
            first_name=first_name,
            last_name=last_name,
            modified_before=modified_before,
            modified_since=modified_since,
            supplemental_data=supplemental_data,
            limit=limit,
            page=page,
        )

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert result[0]["id"] == list(mock_users_data["results"]["users"].values())[0]["id"]

    @requests_mock.Mocker()
    def test_get_timesheets_with_params(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_timesheets_data)
        ids = [1, 2, 3]
        jobcode_ids = [4, 5, 6]
        payroll_ids = [7, 8, 9]
        user_ids = [10, 11, 12]
        group_ids = [13, 14, 15]
        end_date = "2022-01-01"
        on_the_clock = True
        jobcode_type = "test"
        modified_before = "2022-01-01"
        modified_since = "2022-01-01"
        supplemental_data = True
        limit = 10
        page = 1
        start_date = "2022-01-01"

        # Act
        result = self.qb.get_timesheets(
            ids=ids,
            jobcode_ids=jobcode_ids,
            payroll_ids=payroll_ids,
            user_ids=user_ids,
            group_ids=group_ids,
            end_date=end_date,
            on_the_clock=on_the_clock,
            jobcode_type=jobcode_type,
            modified_before=modified_before,
            modified_since=modified_since,
            supplemental_data=supplemental_data,
            limit=limit,
            page=page,
            start_date=start_date,
        )

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert (
            result[0]["id"] == list(mock_timesheets_data["results"]["timesheets"].values())[0]["id"]
        )

    @requests_mock.Mocker()
    def test_get_schedule_events_with_params(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_schedule_events_data)
        ids = [1, 2, 3]
        users_ids = [4, 5, 6]
        schedule_calendar_ids = [7, 8, 9]
        jobcode_ids = [10, 11, 12]
        start = "2022-01-01"
        end = "2022-01-01"
        active_users = True
        active = True
        draft = True
        team_events = True
        modified_before = "2022-01-01"
        modified_since = "2022-01-01"
        supplemental_data = True
        limit = 10

        # Act
        result = self.qb.get_schedule_events(
            ids=ids,
            users_ids=users_ids,
            schedule_calendar_ids=schedule_calendar_ids,
            jobcode_ids=jobcode_ids,
            start=start,
            end=end,
            active_users=active_users,
            active=active,
            draft=draft,
            team_events=team_events,
            modified_before=modified_before,
            modified_since=modified_since,
            supplemental_data=supplemental_data,
            limit=limit,
        )

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert (
            result[0]["id"]
            == list(mock_schedule_events_data["results"]["schedule_events"].values())[0]["id"]
        )

    @requests_mock.Mocker()
    def test_get_geolocations(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_geolocations_data)

        # Act
        result = self.qb.get_geolocations()

        # Assert
        assert isinstance(result, Table)
        assert len(result) > 0
        assert (
            result[0]["id"]
            == list(mock_geolocations_data["results"]["geolocations"].values())[0]["id"]
        )
