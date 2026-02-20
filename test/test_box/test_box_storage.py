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

        # Create a small test table we can reuse
        self.test_table = Table(
            [
                ["phone_number", "last_name", "first_name"],
                ["4435705355", "Warren", "Elizabeth"],
                ["5126993336", "Obama", "Barack"],
            ]
        )
        self.test_table_csv = Path(self.test_table.to_csv())

    def tearDown(self) -> None:
        logging.info(f"Deleting temp folder {self.temp_folder_name}")
        self.client.delete_folder_by_id(self.temp_folder_id)
        Path.unlink(self.test_table_csv)

    def test_create_folder(self) -> None:
        new_test_folder = generate_random_string(24)
        new_test_folder_id = self.client.create_folder(new_test_folder)
        assert new_test_folder_id is not None
        self.client.delete_folder_by_id(new_test_folder_id)

    def test_create_folder_with_forward_slash(self) -> None:
        new_test_folder = self.temp_folder_name + "/" + generate_random_string(24)
        new_test_folder_id = self.client.create_folder(new_test_folder)
        assert new_test_folder_id is not None
        self.client.delete_folder_by_id(new_test_folder_id)

    def test_create_folder_with_backward_slash(self) -> None:
        new_test_folder = self.temp_folder_name + "\\" + generate_random_string(24)
        new_test_folder_id = self.client.create_folder(new_test_folder)
        assert new_test_folder_id is not None
        self.client.delete_folder_by_id(new_test_folder_id)

    def test_delete_folder(self) -> None:
        new_test_folder = generate_random_string(24)
        new_test_folder_id = self.client.create_folder(new_test_folder)
        assert new_test_folder_id is not None
        self.client.delete_folder(new_test_folder)

    def test_delete_folder_with_slash(self) -> None:
        new_test_folder = self.temp_folder_name + "/" + generate_random_string(24)
        new_test_folder_id = self.client.create_folder(new_test_folder)
        assert new_test_folder_id is not None
        self.client.delete_folder(new_test_folder)

    def test_upload_table(self) -> None:
        new_test_file_name = generate_random_string(24)
        new_test_file = self.client.upload_table(self.test_table, path=new_test_file_name)
        assert new_test_file is not None
        self.client.delete_file_by_id(new_test_file.id)

    def test_upload_table_with_slash(self) -> None:
        new_test_file_name = generate_random_string(24)
        new_test_path = self.temp_folder_name + "/" + new_test_file_name
        new_test_file = self.client.upload_table(self.test_table, path=new_test_path)
        assert new_test_file is not None

    def test_upload_table_with_format_json(self) -> None:
        new_test_file_name = generate_random_string(24)
        self.temp_folder_name + "/" + new_test_file_name
        new_test_file = self.client.upload_table(
            self.test_table, path=new_test_file_name, format="json"
        )
        assert new_test_file is not None
        self.client.delete_file_by_id(new_test_file.id)

    def test_upload_file(self) -> None:
        new_test_file = self.client.upload_file(self.test_table_csv)
        assert new_test_file is not None
        self.client.delete_file_by_id(new_test_file.id)

    def test_upload_file_with_slash(self) -> None:
        new_test_file_name = generate_random_string(24)
        new_test_path = self.temp_folder_name + "/" + new_test_file_name
        new_test_file = self.client.upload_file(self.test_table_csv, path=new_test_path)
        assert new_test_file is not None

    def test_delete_file(self) -> None:
        new_test_file_name = generate_random_string(24)
        new_test_file = self.client.upload_table(self.test_table, path=new_test_file_name)
        assert new_test_file is not None
        self.client.delete_file(new_test_file_name)

    def test_list(self) -> None:
        file_dict = {}
        file_dict["test_file_1"] = self.temp_folder_name + "/test_list_file_1"
        file_dict["test_file_2"] = self.temp_folder_name + "/test_list_file_2"
        file_dict["test_file_3"] = self.temp_folder_name + "/test_list_file_3"
        file_dict["test_file_id_1"] = self.client.upload_table(
            self.test_table, path=file_dict["test_file_1"]
        ).id
        file_dict["test_file_id_2"] = self.client.upload_table(
            self.test_table, path=file_dict["test_file_2"]
        ).id
        file_dict["test_file_id_3"] = self.client.upload_table(
            self.test_table, path=file_dict["test_file_3"]
        ).id
        assert file_dict["test_file_id_1"] is not None
        assert file_dict["test_file_id_2"] is not None
        assert file_dict["test_file_id_3"] is not None
        items = self.client.list(self.temp_folder_name)

        for item in items:
            if item["id"] == file_dict["test_file_id_1"]:
                file_dict["test_file_found_1"] = True
            elif item["id"] == file_dict["test_file_id_2"]:
                file_dict["test_file_found_2"] = True
            elif item["id"] == file_dict["test_file_id_3"]:
                file_dict["test_file_found_3"] = True

            if (
                "test_file_found_1" in file_dict
                and "test_file_found_2" in file_dict
                and "test_file_found_3" in file_dict
            ):
                break

        assert "test_file_found_1" in file_dict
        assert "test_file_found_2" in file_dict
        assert "test_file_found_3" in file_dict

    def test_list_default_folder_id(self) -> None:
        items = self.client.list()
        assert self.temp_folder_id in items["id"]

    def test_list_files(self) -> None:
        file_dict = {}
        file_dict["test_file_1"] = self.temp_folder_name + "/test_list_file_1"
        file_dict["test_file_2"] = self.temp_folder_name + "/test_list_file_2"
        file_dict["test_file_3"] = self.temp_folder_name + "/test_list_file_3"
        file_dict["test_file_id_1"] = self.client.upload_table(
            self.test_table, path=file_dict["test_file_1"]
        ).id
        file_dict["test_file_id_2"] = self.client.upload_table(
            self.test_table, path=file_dict["test_file_2"]
        ).id
        file_dict["test_file_id_3"] = self.client.upload_table(
            self.test_table, path=file_dict["test_file_3"]
        ).id
        assert file_dict["test_file_id_1"] is not None
        assert file_dict["test_file_id_2"] is not None
        assert file_dict["test_file_id_3"] is not None
        items = self.client.list(self.temp_folder_name, item_type="file")

        for item in items:
            if item["id"] == file_dict["test_file_id_1"]:
                file_dict["test_file_found_1"] = True
            elif item["id"] == file_dict["test_file_id_2"]:
                file_dict["test_file_found_2"] = True
            elif item["id"] == file_dict["test_file_id_3"]:
                file_dict["test_file_found_3"] = True

            if (
                "test_file_found_1" in file_dict
                and "test_file_found_2" in file_dict
                and "test_file_found_3" in file_dict
            ):
                break

        assert "test_file_found_1" in file_dict
        assert "test_file_found_2" in file_dict
        assert "test_file_found_3" in file_dict

    def test_list_folders(self) -> None:
        file_dict = {}
        file_dict["test_folder_1"] = self.temp_folder_name + "/test_list_folder_1"
        file_dict["test_folder_2"] = self.temp_folder_name + "/test_list_folder_2"
        file_dict["test_folder_3"] = self.temp_folder_name + "/test_list_folder_3"
        file_dict["test_folder_id_1"] = self.client.create_folder(file_dict["test_folder_1"])
        file_dict["test_folder_id_2"] = self.client.create_folder(file_dict["test_folder_2"])
        file_dict["test_folder_id_3"] = self.client.create_folder(file_dict["test_folder_3"])
        assert file_dict["test_folder_id_1"] is not None
        assert file_dict["test_folder_id_2"] is not None
        assert file_dict["test_folder_id_3"] is not None
        items = self.client.list(self.temp_folder_name, item_type="folder")

        for item in items:
            if item["id"] == file_dict["test_folder_id_1"]:
                file_dict["test_folder_found_1"] = True
            elif item["id"] == file_dict["test_folder_id_2"]:
                file_dict["test_folder_found_2"] = True
            elif item["id"] == file_dict["test_folder_id_3"]:
                file_dict["test_folder_found_3"] = True

            if (
                "test_folder_found_1" in file_dict
                and "test_folder_found_2" in file_dict
                and "test_folder_found_3" in file_dict
            ):
                break

        assert "test_folder_found_1" in file_dict
        assert "test_folder_found_2" in file_dict
        assert "test_folder_found_3" in file_dict

    def test_list_files_by_id(self) -> None:
        file_dict = {}
        file_dict["test_file_1"] = self.temp_folder_name + "/test_list_file_1"
        file_dict["test_file_2"] = self.temp_folder_name + "/test_list_file_2"
        file_dict["test_file_3"] = self.temp_folder_name + "/test_list_file_3"
        file_dict["test_file_id_1"] = self.client.upload_table(
            self.test_table, path=file_dict["test_file_1"]
        ).id
        file_dict["test_file_id_2"] = self.client.upload_table(
            self.test_table, path=file_dict["test_file_2"]
        ).id
        file_dict["test_file_id_3"] = self.client.upload_table(
            self.test_table, path=file_dict["test_file_3"]
        ).id
        assert file_dict["test_file_id_1"] is not None
        assert file_dict["test_file_id_2"] is not None
        assert file_dict["test_file_id_3"] is not None
        items = self.client.list_files_by_id(self.temp_folder_id)

        for item in items:
            if item["id"] == file_dict["test_file_id_1"]:
                file_dict["test_file_found_1"] = True
            elif item["id"] == file_dict["test_file_id_2"]:
                file_dict["test_file_found_2"] = True
            elif item["id"] == file_dict["test_file_id_3"]:
                file_dict["test_file_found_3"] = True

            if (
                "test_file_found_1" in file_dict
                and "test_file_found_2" in file_dict
                and "test_file_found_3" in file_dict
            ):
                break

        assert "test_file_found_1" in file_dict
        assert "test_file_found_2" in file_dict
        assert "test_file_found_3" in file_dict

    def test_list_files_by_id_default_folder_id(self) -> None:
        test_table_name = generate_random_string(24)
        test_table_id = self.client.upload_table(self.test_table, test_table_name).id
        items = self.client.list_files_by_id()
        assert test_table_id in items["id"]
        self.client.delete_file_by_id(test_table_id)

    def test_list_folders_by_id(self) -> None:
        file_dict = {}
        file_dict["test_folder_1"] = self.temp_folder_name + "/test_list_folder_1"
        file_dict["test_folder_2"] = self.temp_folder_name + "/test_list_folder_2"
        file_dict["test_folder_3"] = self.temp_folder_name + "/test_list_folder_3"
        file_dict["test_folder_id_1"] = self.client.create_folder(file_dict["test_folder_1"])
        file_dict["test_folder_id_2"] = self.client.create_folder(file_dict["test_folder_2"])
        file_dict["test_folder_id_3"] = self.client.create_folder(file_dict["test_folder_3"])
        assert file_dict["test_folder_id_1"] is not None
        assert file_dict["test_folder_id_2"] is not None
        assert file_dict["test_folder_id_3"] is not None
        items = self.client.list_folders_by_id(self.temp_folder_id)

        for item in items:
            if item["id"] == file_dict["test_folder_id_1"]:
                file_dict["test_folder_found_1"] = True
            elif item["id"] == file_dict["test_folder_id_2"]:
                file_dict["test_folder_found_2"] = True
            elif item["id"] == file_dict["test_folder_id_3"]:
                file_dict["test_folder_found_3"] = True

            if (
                "test_folder_found_1" in file_dict
                and "test_folder_found_2" in file_dict
                and "test_folder_found_3" in file_dict
            ):
                break

        assert "test_folder_found_1" in file_dict
        assert "test_folder_found_2" in file_dict
        assert "test_folder_found_3" in file_dict

    def test_list_folders_by_id_default_folder_id(self) -> None:
        items = self.client.list_folders_by_id()
        assert self.temp_folder_id in items["id"]

    def test_upload_file_to_folder_id_no_file_name(self):
        test_file_id = self.client.upload_file_to_folder_id(self.test_table_csv, folder_id="0")
        items = self.client.list()
        self.client.delete_file_by_id(test_file_id)
        assert test_file_id in items["id"]

    def test_upload_file_to_folder_id_no_folder_id(self):
        test_file_name = generate_random_string(24)
        test_file_id = self.client.upload_file_to_folder_id(self.test_table_csv, test_file_name)
        items = self.client.list()
        self.client.delete_file_by_id(test_file_id)
        assert test_file_id in items["id"]

    def test_download_file(self):
        test_file_name = self.temp_folder_path + "/" + generate_random_string(24)
        test_file_id = self.client.upload_table(self.test_table, path=test_file_name).id
        local_file = str(self.client.download_file().absolute())
        self.client.delete_file_by_id(test_file_id)
        downloaded_table = Table.from_csv(local_file)
        assert str(downloaded_table) == str(self.test_table)

    def test_error_bad_format_upload(self) -> None:
        with pytest.raises(ValueError, match="Format argument must be in one of"):
            self.client.upload_table_to_folder_id(
                self.test_table, "test_error_bad_format", format="bad_format"
            )

    def test_error_bad_format_get(self) -> None:
        nonexistent_id = "9999999"
        with pytest.raises(ValueError, match="Format argument must be in one of"):
            self.client.get_table_by_file_id(file_id=nonexistent_id, format="bad_format")

    def test_error_nonexistent_id_upload(self) -> None:
        nonexistent_id = "9999999"
        with pytest.raises(BoxAPIError, match="Message: 404 Not Found"):
            self.client.upload_table_to_folder_id(
                self.test_table, "test_error_nonexistent_id_upload", folder_id=nonexistent_id
            )

    def test_error_nonexistent_id_get(self) -> None:
        nonexistent_id = "9999999"
        with pytest.raises(BoxAPIError, match="Message: 404 Could not find the specified resource"):
            self.client.get_table_by_file_id(nonexistent_id, format="json")

    def test_error_nonexistent_path_create(self) -> None:
        with pytest.raises(ValueError, match="No file or folder named"):
            self.client.create_folder("nonexistent_path/path")

    def test_error_nonexistent_id_create(self) -> None:
        nonexistent_id = "9999999"
        with pytest.raises(BoxAPIError, match="Message: 404 Not Found"):
            self.client.create_folder_by_id(
                folder_name="subfolder", parent_folder_id=nonexistent_id
            )

    def test_error_bad_credentials(self) -> None:
        box = Box(access_token="5345345345")
        with pytest.raises(
            BoxSDKError, match="Developer token has expired. Please provide a new one."
        ):
            box.list_files_by_id()
