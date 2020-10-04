import logging
import os
import pprint
import random
import string
import tempfile
import unittest

from parsons.box import Box
from parsons.etl import Table
from parsons.utilities import files

"""Prior to running, you should ensure that the relevant environment
variables have been set, e.g. via

export BOX_CLIENT_ID=txqedp4rqi0cz5qckz361fziavdtdwxz
export BOX_CLIENT_SECRET=bk264KHMDLVy89TeuUpSRa4CN5o35u9h
export BOX_ACCESS_TOKEN=boK97B39m3ozIGyTcazbWRbi5F2SSZ5J
"""
TEST_CLIENT_ID = os.getenv('BOX_CLIENT_ID')
TEST_BOX_CLIENT_SECRET = os.getenv('BOX_CLIENT_SECRET')
TEST_ACCESS_TOKEN = os.getenv('BOX_ACCESS_TOKEN')

def generate_random_string(length):
    """Utility to generate random alpha string for file/folder names"""
    letters = string.ascii_letters
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

@unittest.skipIf(not os.getenv('LIVE_TEST'), 'Skipping because not running live test')
class TestBoxStorage(unittest.TestCase):

    def setUp(self) -> None:
        # Create a client that we'll use to manipulate things behind the scenes
        self.client = Box()
        # Create test folder that we'll use for all our manipulations
        self.temp_folder_name = generate_random_string(24)
        logging.info(f'Creating temp folder {self.temp_folder_name}')
        self.temp_folder_id = self.client.create_folder(self.temp_folder_name)

    def tearDown(self) -> None:
        logging.info(f'Deleting temp folder {self.temp_folder_name}')
        self.client.delete_folder(self.temp_folder_id)

    def test_list_files(self) -> None:
        # Count on environment variables being set
        box = Box()

        subfolder = box.create_folder(folder_name='subfolder',
                                      parent_folder=self.temp_folder_id)

        # Create a couple of files in the temp folder
        table = Table([['phone_number', 'last_name', 'first_name'],
                       ['4435705355', 'Warren', 'Elizabeth'],
                       ['5126993336', 'Obama', 'Barack']])

        box.upload_table(table, 'temp1', folder_id=subfolder)
        box.upload_table(table, 'temp2', folder_id=subfolder)
        box.create_folder(folder_name='temp_folder1', parent_folder=subfolder)
        box.create_folder(folder_name='temp_folder2', parent_folder=subfolder)

        file_list = box.list_files(folder_id=subfolder)['name']
        self.assertEqual(['temp1', 'temp2'], file_list)

        folder_list = box.list_folders(folder_id=subfolder)['name']
        self.assertEqual(['temp_folder1', 'temp_folder2'], folder_list)

    def test_list_folders(self) -> None:
        # Count on environment variables being set
        box = Box()
        file_list = box.list_files()
        print('File list:\n{}'.format(pprint.pformat(file_list)))

    def test_upload_file(self) -> None:
        # Count on environment variables being set
        box = Box()

        table = Table([['phone_number', 'last_name', 'first_name'],
                     ['4435705355', 'Warren', 'Elizabeth'],
                     ['5126993336', 'Obama', 'Barack']])
        box_file = box.upload_table(table, 'phone_numbers', folder_id=self.temp_folder_id)

        new_table = box.get_table(box_file.id)

        # Check that what we saved is equal to what we got back
        self.assertEquals(str(table), str(new_table))
