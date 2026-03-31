import os

import pytest
from box_sdk_gen import BoxDeveloperTokenAuth
from box_sdk_gen.box.errors import BoxAPIError, BoxSDKError

from parsons import Box, Table
from test.conftest import mark_live_test

"""Prior to running, you should ensure that the relevant environment
variables have been set, e.g. via

..code-block:: bash
  :caption: Fake key, provided as example.
    export BOX_ACCESS_TOKEN=boK97B39m3ozIGyTcazbWRbi5F2SSZ5J
..code-block:: powershell
  :caption: Fake key, provided as example.
    [System.Environment]::SetEnvironmentVariable('BOX_ACCESS_TOKEN','boK97B39m3ozIGyTcazbWRbi5F2SSZ5J')
"""
TEST_ACCESS_TOKEN = os.getenv("BOX_ACCESS_TOKEN")


@mark_live_test
def test_box_create_folder(box_client, rand_str) -> None:
    new_test_folder = rand_str()
    new_test_folder_id = box_client.create_folder(new_test_folder)
    assert new_test_folder_id is not None
    box_client.delete_folder_by_id(new_test_folder_id)


@mark_live_test
def test_box_create_folder_with_forward_slash(box_client, rand_str, temp_box_test_folder) -> None:
    new_test_folder = temp_box_test_folder + "/" + rand_str()
    new_test_folder_id = box_client.create_folder(new_test_folder)
    assert new_test_folder_id is not None
    box_client.delete_folder_by_id(new_test_folder_id)


@mark_live_test
def test_box_create_folder_with_backward_slash(box_client, rand_str, temp_box_test_folder) -> None:
    new_test_folder = temp_box_test_folder + "\\" + rand_str()
    new_test_folder_id = box_client.create_folder(new_test_folder)
    assert new_test_folder_id is not None
    box_client.delete_folder_by_id(new_test_folder_id)


@mark_live_test
def test_box_delete_folder(box_client, rand_str) -> None:
    new_test_folder = rand_str()
    new_test_folder_id = box_client.create_folder(new_test_folder)
    assert new_test_folder_id is not None
    box_client.delete_folder(new_test_folder)


@mark_live_test
def test_box_delete_folder_with_slash(box_client, rand_str, temp_box_test_folder) -> None:
    new_test_folder = temp_box_test_folder + "/" + rand_str()
    new_test_folder_id = box_client.create_folder(new_test_folder)
    assert new_test_folder_id is not None
    box_client.delete_folder(new_test_folder)


@mark_live_test
def test_box_upload_table(box_client, rand_str, small_box_table) -> None:
    new_test_file_name = rand_str()
    new_test_file = box_client.upload_table(small_box_table, path=new_test_file_name)
    assert new_test_file is not None
    box_client.delete_file_by_id(new_test_file)


@mark_live_test
def test_box_upload_table_big(box_client, rand_str, big_box_table) -> None:
    new_test_file_name = rand_str()
    new_test_file = box_client.upload_table(big_box_table, path=new_test_file_name)
    assert new_test_file is not None
    box_client.delete_file_by_id(new_test_file)


@mark_live_test
def test_box_upload_table_with_slash(
    box_client, rand_str, small_box_table, temp_box_test_folder
) -> None:
    new_test_file_name = rand_str()
    new_test_path = temp_box_test_folder + "/" + new_test_file_name
    new_test_file = box_client.upload_table(small_box_table, path=new_test_path)
    assert new_test_file is not None


@mark_live_test
def test_box_upload_table_with_format_json(box_client, rand_str, small_box_table) -> None:
    new_test_file_name = rand_str()
    new_test_file = box_client.upload_table(small_box_table, path=new_test_file_name, format="json")
    assert new_test_file is not None
    box_client.delete_file_by_id(new_test_file)


@mark_live_test
def test_box_upload_file(box_client, small_box_table_csv) -> None:
    new_test_file = box_client.upload_file(small_box_table_csv)
    assert new_test_file is not None
    box_client.delete_file_by_id(new_test_file)


@mark_live_test
def test_box_upload_file_with_slash(
    box_client, rand_str, small_box_table_csv, temp_box_test_folder
) -> None:
    new_test_file_name = rand_str()
    new_test_path = temp_box_test_folder + "/" + new_test_file_name
    new_test_file = box_client.upload_file(small_box_table_csv, path=new_test_path)
    assert new_test_file is not None


@mark_live_test
def test_box_delete_file(box_client, rand_str, small_box_table) -> None:
    new_test_file_name = rand_str()
    new_test_file = box_client.upload_table(small_box_table, path=new_test_file_name)
    assert new_test_file is not None
    box_client.delete_file(new_test_file_name)


@mark_live_test
def test_box_list(box_client, small_box_table, temp_box_test_folder) -> None:
    file_dict = {}
    file_dict["test_file_1"] = temp_box_test_folder + "/test_list_file_1"
    file_dict["test_file_2"] = temp_box_test_folder + "/test_list_file_2"
    file_dict["test_file_3"] = temp_box_test_folder + "/test_list_file_3"
    file_dict["test_file_id_1"] = box_client.upload_table(
        small_box_table, path=file_dict["test_file_1"]
    )
    file_dict["test_file_id_2"] = box_client.upload_table(
        small_box_table, path=file_dict["test_file_2"]
    )
    file_dict["test_file_id_3"] = box_client.upload_table(
        small_box_table, path=file_dict["test_file_3"]
    )
    assert file_dict["test_file_id_1"] is not None
    assert file_dict["test_file_id_2"] is not None
    assert file_dict["test_file_id_3"] is not None
    items = box_client.list(temp_box_test_folder)

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


@mark_live_test
def test_box_list_default_folder_id(box_client, temp_box_test_folder_id) -> None:
    items = box_client.list()
    assert temp_box_test_folder_id in items["id"]


@mark_live_test
def test_box_list_files(box_client, small_box_table, temp_box_test_folder) -> None:
    file_dict = {}
    file_dict["test_file_1"] = temp_box_test_folder + "/test_list_file_1"
    file_dict["test_file_2"] = temp_box_test_folder + "/test_list_file_2"
    file_dict["test_file_3"] = temp_box_test_folder + "/test_list_file_3"
    file_dict["test_file_id_1"] = box_client.upload_table(
        small_box_table, path=file_dict["test_file_1"]
    )
    file_dict["test_file_id_2"] = box_client.upload_table(
        small_box_table, path=file_dict["test_file_2"]
    )
    file_dict["test_file_id_3"] = box_client.upload_table(
        small_box_table, path=file_dict["test_file_3"]
    )
    assert file_dict["test_file_id_1"] is not None
    assert file_dict["test_file_id_2"] is not None
    assert file_dict["test_file_id_3"] is not None
    items = box_client.list(temp_box_test_folder, item_type="file")

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


@mark_live_test
def test_box_list_files_empty_folder(box_client, small_box_table, temp_box_test_folder) -> None:
    items = box_client.list(temp_box_test_folder)
    assert items.num_rows == 0


@mark_live_test
def test_box_list_folders(box_client, temp_box_test_folder) -> None:
    file_dict = {}
    file_dict["test_folder_1"] = temp_box_test_folder + "/test_list_folder_1"
    file_dict["test_folder_2"] = temp_box_test_folder + "/test_list_folder_2"
    file_dict["test_folder_3"] = temp_box_test_folder + "/test_list_folder_3"
    file_dict["test_folder_id_1"] = box_client.create_folder(file_dict["test_folder_1"])
    file_dict["test_folder_id_2"] = box_client.create_folder(file_dict["test_folder_2"])
    file_dict["test_folder_id_3"] = box_client.create_folder(file_dict["test_folder_3"])
    assert file_dict["test_folder_id_1"] is not None
    assert file_dict["test_folder_id_2"] is not None
    assert file_dict["test_folder_id_3"] is not None
    items = box_client.list(temp_box_test_folder, item_type="folder")

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


@mark_live_test
def test_box_list_files_by_id(
    box_client, small_box_table, temp_box_test_folder, temp_box_test_folder_id
) -> None:
    file_dict = {}
    file_dict["test_file_1"] = temp_box_test_folder + "/test_list_file_1"
    file_dict["test_file_2"] = temp_box_test_folder + "/test_list_file_2"
    file_dict["test_file_3"] = temp_box_test_folder + "/test_list_file_3"
    file_dict["test_file_id_1"] = box_client.upload_table(
        small_box_table, path=file_dict["test_file_1"]
    )
    file_dict["test_file_id_2"] = box_client.upload_table(
        small_box_table, path=file_dict["test_file_2"]
    )
    file_dict["test_file_id_3"] = box_client.upload_table(
        small_box_table, path=file_dict["test_file_3"]
    )
    assert file_dict["test_file_id_1"] is not None
    assert file_dict["test_file_id_2"] is not None
    assert file_dict["test_file_id_3"] is not None
    items = box_client.list_files_by_id(temp_box_test_folder_id)

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


@mark_live_test
def test_box_list_files_by_id_default_folder_id(box_client, rand_str, small_box_table) -> None:
    test_table_name = rand_str()
    test_table_id = box_client.upload_table(small_box_table, test_table_name)
    items = box_client.list_files_by_id()
    assert test_table_id in items["id"]
    box_client.delete_file_by_id(test_table_id)


@mark_live_test
def test_box_list_folders_by_id(box_client, temp_box_test_folder, temp_box_test_folder_id) -> None:
    file_dict = {}
    file_dict["test_folder_1"] = temp_box_test_folder + "/test_list_folder_1"
    file_dict["test_folder_2"] = temp_box_test_folder + "/test_list_folder_2"
    file_dict["test_folder_3"] = temp_box_test_folder + "/test_list_folder_3"
    file_dict["test_folder_id_1"] = box_client.create_folder(file_dict["test_folder_1"])
    file_dict["test_folder_id_2"] = box_client.create_folder(file_dict["test_folder_2"])
    file_dict["test_folder_id_3"] = box_client.create_folder(file_dict["test_folder_3"])
    assert file_dict["test_folder_id_1"] is not None
    assert file_dict["test_folder_id_2"] is not None
    assert file_dict["test_folder_id_3"] is not None
    items = box_client.list_folders_by_id(temp_box_test_folder_id)

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


@mark_live_test
def test_box_list_folders_by_id_default_folder_id(box_client, temp_box_test_folder_id) -> None:
    items = box_client.list_folders_by_id()
    assert temp_box_test_folder_id in items["id"]


@mark_live_test
def test_box_upload_file_to_folder_id_no_file_name(box_client, small_box_table_csv):
    test_file_id = box_client.upload_file_to_folder_id(small_box_table_csv, folder_id="0")
    items = box_client.list()
    box_client.delete_file_by_id(test_file_id)
    assert test_file_id in items["id"]


@mark_live_test
def test_box_upload_file_to_folder_id_no_folder_id(box_client, rand_str, small_box_table_csv):
    test_file_name = rand_str()
    test_file_id = box_client.upload_file_to_folder_id(small_box_table_csv, test_file_name)
    items = box_client.list()
    box_client.delete_file_by_id(test_file_id)
    assert test_file_id in items["id"]


@mark_live_test
def test_box_download_file(box_client, rand_str, small_box_table, temp_box_test_folder):
    test_file_name = temp_box_test_folder + "/" + rand_str()
    test_file_id = box_client.upload_table(small_box_table, path=test_file_name)
    local_file = str(box_client.download_file(test_file_name).absolute())
    box_client.delete_file_by_id(test_file_id)
    downloaded_table = Table.from_csv(local_file)
    assert str(downloaded_table) == str(small_box_table)


@mark_live_test
def test_box_download_file_with_local_path(
    box_client, rand_str, small_box_table, temp_test_folder, temp_box_test_folder
):
    test_file_name = temp_box_test_folder + "/" + rand_str()
    test_file_id = box_client.upload_table(small_box_table, path=test_file_name)
    local_path = temp_test_folder / rand_str()
    local_file = box_client.download_file(test_file_name, local_path=local_path)
    box_client.delete_file_by_id(test_file_id)
    downloaded_table = Table.from_csv(str(local_file))
    assert str(downloaded_table) == str(small_box_table)


@pytest.mark.parametrize(
    "table_format",
    [
        pytest.param("csv", marks=mark_live_test),
        pytest.param("json", marks=mark_live_test),
    ],
)
def test_box_get_table(table_format, box_client, rand_str, small_box_table, temp_box_test_folder):
    test_file_name = temp_box_test_folder + "/" + rand_str()
    test_file_id = box_client.upload_table(
        small_box_table, path=test_file_name, format=table_format
    )
    local_table = box_client.get_table(test_file_name, format=table_format)
    box_client.delete_file_by_id(test_file_id)
    assert str(local_table) == str(small_box_table)


@mark_live_test
def test_box_error_get_item_id_trailing_backslash(box_client, temp_box_test_folder):
    test_path = temp_box_test_folder + "\\"
    with pytest.raises(ValueError, match='Illegal trailing "/" in file path'):
        box_client.get_item_id(test_path)


@mark_live_test
def test_box_error_get_item_id_trailing_forwardslash(box_client, temp_box_test_folder):
    test_path = temp_box_test_folder + "/"
    with pytest.raises(ValueError, match='Illegal trailing "/" in file path'):
        box_client.get_item_id(test_path)


@mark_live_test
def test_box_error_get_item_id_bad_folder(box_client, rand_str, temp_box_test_file):
    test_path = temp_box_test_file + "/" + rand_str()
    with pytest.raises(ValueError, match="Invalid folder"):
        box_client.get_item_id(test_path)


@mark_live_test
def test_box_error_bad_format_upload(box_client, small_box_table) -> None:
    with pytest.raises(ValueError, match="Format argument must be in one of"):
        box_client.upload_table_to_folder_id(
            small_box_table, "test_error_bad_format", format="bad_format"
        )


@mark_live_test
def test_box_error_bad_format_get(box_client) -> None:
    nonexistent_id = "9999999"
    with pytest.raises(ValueError, match="Format argument must be in one of"):
        box_client.get_table_by_file_id(file_id=nonexistent_id, format="bad_format")


@mark_live_test
def test_box_error_nonexistent_id_upload(box_client, small_box_table) -> None:
    nonexistent_id = "9999999"
    with pytest.raises(BoxAPIError, match="Message: 404 Not Found"):
        box_client.upload_table_to_folder_id(
            small_box_table, "test_error_nonexistent_id_upload", folder_id=nonexistent_id
        )


@mark_live_test
def test_box_error_nonexistent_id_get(box_client) -> None:
    nonexistent_id = "9999999"
    with pytest.raises(BoxAPIError, match="Message: 404 Could not find the specified resource"):
        box_client.get_table_by_file_id(nonexistent_id, format="json")


@mark_live_test
def test_box_error_nonexistent_path_create(box_client) -> None:
    with pytest.raises(ValueError, match="No file or folder named"):
        box_client.create_folder("nonexistent_path/path")


@mark_live_test
def test_box_error_nonexistent_id_create(box_client) -> None:
    nonexistent_id = "9999999"
    with pytest.raises(BoxAPIError, match="Message: 404 Not Found"):
        box_client.create_folder_by_id(folder_name="subfolder", parent_folder_id=nonexistent_id)


@mark_live_test
def test_box_error_bad_credentials() -> None:
    oauth = BoxDeveloperTokenAuth(token="5345345345")
    box = Box(auth=oauth)
    with pytest.raises(BoxSDKError, match="Developer token has expired. Please provide a new one."):
        box.list_files_by_id()
