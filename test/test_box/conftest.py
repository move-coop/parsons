import random
from string import ascii_letters

import pytest

from parsons import Box, Table


@pytest.fixture(scope="module")
def box_client():
    return Box()


@pytest.fixture(scope="module")
def rand_str():
    return lambda: "".join(random.choice(ascii_letters) for i in range(24))


@pytest.fixture(scope="module")
def small_box_table():
    return Table([{"first": "Bob", "last": "Smith"}])


@pytest.fixture
def big_box_table():
    return Table([{"first": "Bob", "last": "Smith"} for x in range(5000000)])


@pytest.fixture
def temp_test_folder(tmp_path_factory):
    return tmp_path_factory.getbasetemp()


@pytest.fixture
def small_box_table_csv(rand_str, small_box_table, temp_test_folder):
    csv_path = temp_test_folder / f"{rand_str()}.csv"
    small_box_table.to_csv(local_path=str(csv_path))
    return csv_path


@pytest.fixture
def temp_box_test_folder(box_client, rand_str):
    temp_folder = rand_str()
    temp_folder_id = box_client.create_folder(temp_folder)
    yield temp_folder
    box_client.delete_folder_by_id(temp_folder_id)


@pytest.fixture
def temp_box_test_folder_id(box_client, temp_box_test_folder):
    temp_folder_id = box_client.get_item_id(temp_box_test_folder)
    return temp_folder_id


@pytest.fixture(params=["csv", "json"])
def temp_box_test_file(request, box_client, rand_str, small_box_table, temp_box_test_folder):
    table_format = request.param
    temp_file = temp_box_test_folder + "/" + rand_str()
    temp_file_id = box_client.upload_table(small_box_table, temp_file, format=table_format)
    yield temp_file
    box_client.delete_file_by_id(temp_file_id)
