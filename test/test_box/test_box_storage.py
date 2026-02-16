import logging
import os
import random
import string
import unittest
import warnings
from pathlib import Path

import pytest
from box_sdk_gen.box.errors import BoxAPIError, BoxSDKError

from parsons import Box, Table
from test.conftest import mark_live_test

"""Prior to running, you should ensure that the relevant environment
variables have been set, e.g. via

# Note: these are fake keys, provided as examples.
export BOX_ACCESS_TOKEN=boK97B39m3ozIGyTcazbWRbi5F2SSZ5J
"""
TEST_CLIENT_ID = os.getenv("BOX_CLIENT_ID")
TEST_BOX_CLIENT_SECRET = os.getenv("BOX_CLIENT_SECRET")
TEST_ACCESS_TOKEN = os.getenv("BOX_ACCESS_TOKEN")


def generate_random_string(length):
    """Utility to generate random alpha string for file/folder names"""
    return "".join(random.choice(string.ascii_letters) for i in range(length))


@mark_live_test
class TestBoxStorage(unittest.TestCase):
    def setUp(self) -> None:
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

        # Create a client that we'll use to manipulate things behind the scenes
        self.client = Box()
        # Create test folder that we'll use for all our manipulations
        self.temp_folder_name = generate_random_string(24)
        logging.info(f"Creating temp folder {self.temp_folder_name}")
        self.temp_folder_id = self.client.create_folder(self.temp_folder_name)

    def tearDown(self) -> None:
        logging.info(f"Deleting temp folder {self.temp_folder_name}")
        self.client.delete_folder_by_id(self.temp_folder_id)

    def test_list_files_by_id(self) -> None:
        # Count on environment variables being set
        box = Box()

        subfolder = box.create_folder_by_id(
            folder_name="id_subfolder", parent_folder_id=self.temp_folder_id
        )

        # Create a couple of files in the temp folder
        table = Table(
            [
                ["phone_number", "last_name", "first_name"],
                ["4435705355", "Warren", "Elizabeth"],
                ["5126993336", "Obama", "Barack"],
            ]
        )

        box.upload_table_to_folder_id(table, "temp1", folder_id=subfolder)
        box.upload_table_to_folder_id(table, "temp2", folder_id=subfolder)
        box.create_folder_by_id(folder_name="temp_folder1", parent_folder_id=subfolder)
        box.create_folder_by_id(folder_name="temp_folder2", parent_folder_id=subfolder)

        file_list = box.list_files_by_id(folder_id=subfolder)
        assert file_list["name"] == ["temp1", "temp2"]

        # Check that if we delete a file, it's no longer there
        for box_file in file_list:
            if box_file["name"] == "temp1":
                box.delete_file_by_id(box_file["id"])
                break
        file_list = box.list_files_by_id(folder_id=subfolder)
        assert file_list["name"] == ["temp2"]

        folder_list = box.list_folders_by_id(folder_id=subfolder)["name"]
        assert folder_list == ["temp_folder1", "temp_folder2"]

    def test_list_files_by_path(self) -> None:
        # Count on environment variables being set
        box = Box()

        # Make sure our test folder is in the right place
        found_default = False
        for item in box.list():
            if item["name"] == self.temp_folder_name:
                found_default = True
                break
        assert found_default, (
            f"Failed to find test folder f{self.temp_folder_name} in default Box folder"
        )

        subfolder_name = "path_subfolder"
        subfolder_path = f"{self.temp_folder_name}/{subfolder_name}"
        box.create_folder(path=subfolder_path)

        # Create a couple of files in the temp folder
        table = Table(
            [
                ["phone_number", "last_name", "first_name"],
                ["4435705355", "Warren", "Elizabeth"],
                ["5126993336", "Obama", "Barack"],
            ]
        )

        box.upload_table(table, f"{subfolder_path}/temp1")
        box.upload_table(table, f"{subfolder_path}/temp2")
        box.create_folder(f"{subfolder_path}/temp_folder1")
        box.create_folder(f"{subfolder_path}/temp_folder2")

        file_list = box.list(path=subfolder_path, item_type="file")
        assert file_list["name"] == ["temp1", "temp2"]

        # Check that if we delete a file, it's no longer there
        for box_file in file_list:
            if box_file["name"] == "temp1":
                box.delete_file(path=f"{subfolder_path}/temp1")
                break
        file_list = box.list(path=subfolder_path, item_type="file")
        assert file_list["name"] == ["temp2"]

        folder_list = box.list(path=subfolder_path, item_type="folder")
        assert folder_list["name"] == ["temp_folder1", "temp_folder2"]

        # Make sure we can delete by path
        box.delete_folder(f"{subfolder_path}/temp_folder1")
        folder_list = box.list(path=subfolder_path, item_type="folder")
        assert folder_list["name"] == ["temp_folder2"]

    def test_upload_file(self) -> None:
        # Count on environment variables being set
        box = Box()

        table = Table(
            [
                ["phone_number", "last_name", "first_name"],
                ["4435705355", "Warren", "Elizabeth"],
                ["5126993336", "Obama", "Barack"],
            ]
        )
        box_file = box.upload_table_to_folder_id(
            table, "phone_numbers", folder_id=self.temp_folder_id
        )

        new_table = box.get_table_by_file_id(box_file.id)

        # Check that what we saved is equal to what we got back
        assert str(table) == str(new_table)

        # Check that things also work in JSON
        box_file = box.upload_table_to_folder_id(
            table, "phone_numbers_json", folder_id=self.temp_folder_id, format="json"
        )

        new_table = box.get_table_by_file_id(box_file.id, format="json")

        # Check that what we saved is equal to what we got back
        assert str(table) == str(new_table)

        # Now check the same thing with paths instead of file_id
        path_filename = "path_phone_numbers"
        box_file = box.upload_table(table, f"{self.temp_folder_name}/{path_filename}")
        new_table = box.get_table(path=f"{self.temp_folder_name}/{path_filename}")

        # Check that we throw an exception with bad formats
        with pytest.raises(ValueError):  # noqa: PT011
            box.upload_table_to_folder_id(table, "phone_numbers", format="illegal_format")
        with pytest.raises(ValueError):  # noqa: PT011
            box.get_table_by_file_id(box_file.id, format="illegal_format")

    def test_download_file(self) -> None:
        box = Box()

        table = Table(
            [
                ["phone_number", "last_name", "first_name"],
                ["4435705355", "Warren", "Elizabeth"],
                ["5126993336", "Obama", "Barack"],
            ]
        )
        uploaded_file = Path(table.to_csv())

        path_filename = Path(self.temp_folder_name) / "my_path"
        box.upload_table(table, str(path_filename))

        downloaded_file = Path(box.download_file(str(path_filename)))

        assert uploaded_file.read_text() == downloaded_file.read_text()

    def test_get_item_id(self) -> None:
        # Count on environment variables being set
        box = Box()

        # Create a subfolder in which we'll do this test
        sub_sub_folder_name = "item_subfolder"
        sub_sub_folder_id = box.create_folder_by_id(
            folder_name=sub_sub_folder_name, parent_folder_id=self.temp_folder_id
        )

        table = Table(
            [
                ["phone_number", "last_name", "first_name"],
                ["4435705355", "Warren", "Elizabeth"],
                ["5126993336", "Obama", "Barack"],
            ]
        )
        box_file = box.upload_table_to_folder_id(
            table, "file_in_subfolder", folder_id=self.temp_folder_id
        )

        box_file = box.upload_table_to_folder_id(
            table, "phone_numbers", folder_id=sub_sub_folder_id
        )

        # Now try getting various ids
        file_path = f"{self.temp_folder_name}/item_subfolder/phone_numbers"
        assert box_file.id == box.get_item_id(path=file_path)

        file_path = f"{self.temp_folder_name}/item_subfolder"
        assert sub_sub_folder_id == box.get_item_id(path=file_path)

        file_path = self.temp_folder_name
        assert self.temp_folder_id == box.get_item_id(path=file_path)

        # Trailing "/"
        file_path = f"{self.temp_folder_name}/item_subfolder/phone_numbers/"
        with pytest.raises(ValueError):  # noqa: PT011
            box.get_item_id(path=file_path)

        # Nonexistent file
        file_path = f"{self.temp_folder_name}/item_subfolder/nonexistent/phone_numbers"
        with pytest.raises(ValueError):  # noqa: PT011
            box.get_item_id(path=file_path)

        # File (rather than folder) in middle of path
        file_path = f"{self.temp_folder_name}/file_in_subfolder/phone_numbers"
        with pytest.raises(ValueError):  # noqa: PT011
            box.get_item_id(path=file_path)

    def test_errors(self) -> None:
        # Count on environment variables being set
        box = Box()

        nonexistent_id = "9999999"
        table = Table(
            [
                ["phone_number", "last_name", "first_name"],
                ["4435705355", "Warren", "Elizabeth"],
                ["5126993336", "Obama", "Barack"],
            ]
        )

        # Upload a bad format
        with pytest.raises(ValueError):  # noqa: PT011
            box.upload_table_to_folder_id(table, "temp1", format="bad_format")

        # Download a bad format
        with pytest.raises(ValueError):  # noqa: PT011
            box.get_table_by_file_id(file_id=nonexistent_id, format="bad_format")

        # Upload to non-existent folder
        with pytest.raises(BoxAPIError):
            box.upload_table_to_folder_id(table, "temp1", folder_id=nonexistent_id)

        # Download a non-existent file
        with pytest.raises(BoxAPIError):
            box.get_table_by_file_id(nonexistent_id, format="json")

        # Create folder in non-existent parent
        with pytest.raises(ValueError):  # noqa: PT011
            box.create_folder("nonexistent_path/path")

        # Create folder in non-existent parent
        with pytest.raises(BoxAPIError):
            box.create_folder_by_id(folder_name="subfolder", parent_folder_id=nonexistent_id)

        # Try using bad credentials
        box = Box(access_token="5345345345")
        with pytest.raises(BoxSDKError):
            box.list_files_by_id()
