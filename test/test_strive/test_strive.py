from parsons import Strive
import pytest
import unittest
import strive_test_data


class TestStrive(unittest.TestCase):
    def setUp(self):
        self.strive = Strive()

    def test_get_member(self):
        # Headers
        data = {"limit": "5"}
        # Testing get members
        response = self.strive.get_members(params=data)
        # Convert data into Parsons Table
        data = {"limit": "5"}

        assert self.strive.get_members(data).num_rows == 5
        assert (
            self.strive.get_members(data)[0]
            == strive_test_data.get_members_expected_output
        )

