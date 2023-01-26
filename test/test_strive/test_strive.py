from parsons import Strive
import pytest
import unittest
import strive_test_data
from parsons import Table


class TestStrive(unittest.TestCase):
    def setUp(self):
        self.strive = Strive()

    def test_get_member(self):
        # Headers
        data = {"limit": "5"}
        # Testing get members
        response = self.strive.get_members(params=data)

        assert response.num_rows == 5

        assert isinstance(response, Table)

        # TO DO
        # Validate content of response

    def test_get_broadcasts(self):
        # Headers
        data = {"apple" : "yummy"}

        # Testing get broadcasts with bad params 
        import ipdb; ipdb.set_trace()
        
        response = self.strive.get_broadcasts(params=data) 

        

        print("Done")
                 
        # assert (
        #     self.strive.get_members(data)[0]
        #     == strive_test_data.get_members_expected_output
        # )

