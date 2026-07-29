"""Tests for the GoogleBigQuery connector.

BigQuery wraps the ``google-cloud-bigquery`` client (and a GoogleCloudStorage client
for staging). Those clients are the external boundary: the helpers build a real
GoogleBigQuery and swap ``bq._client`` (and, for copies, a fake GCS client) for mocks,
so the connector's own query/copy/load logic runs against them. Credentials are faked
by the autouse ``bq_creds`` fixture (see conftest.py), which replaces the old
FakeCredentialTest base the suite inherited.
"""

import json
import logging
import os
import unittest.mock as mock
from pathlib import Path

import pytest
from google.cloud import bigquery, exceptions

from parsons import GoogleBigQuery, Table
from parsons.google.google_cloud_storage import GoogleCloudStorage

TMP_GCS_BUCKET = "tmp"


class BigQuery(GoogleBigQuery):
    @mock.patch("parsons.google.google_bigquery.load_google_application_credentials")
    def __init__(self, load_creds_mock, app_creds=None, **kwargs):
        super().__init__(app_creds=app_creds, **kwargs)


class FakeClient:
    """A fake Storage client used for monkey-patching."""

    @mock.patch("parsons.google.google_bigquery.load_google_application_credentials")
    @mock.patch("parsons.google.google_cloud_storage.load_google_application_credentials")
    def __init__(self, load_creds_mock, load_creds_mock_2, project=None, credentials=None):
        self.project = project


class FakeGoogleCloudStorage(GoogleCloudStorage):
    """A fake GoogleCloudStorage used to test setting up credentials."""

    @mock.patch("google.cloud.storage.Client", FakeClient)
    @mock.patch("parsons.google.google_cloud_storage.load_google_application_credentials")
    def __init__(self, load_creds_mock):
        super().__init__(None, None)

    def upload_table(self, table, bucket_name, blob_name, data_type="csv", default_acl=None):
        pass

    def delete_blob(self, bucket_name, blob_name):
        pass


def default_table():
    return Table(
        [
            {"num": 1, "ltr": "a", "boolcol": None},
            {"num": 2, "ltr": "b", "boolcol": True},
        ]
    )


def build_mock_client_for_querying(results):
    # A mock that plays the role of the cursor.
    cursor = mock.MagicMock()
    cursor.execute.return_value = None
    cursor.fetchmany.side_effect = [results, []]
    if results:
        cursor.description = [(key, None) for key in results[0]]

    connection = mock.MagicMock()
    connection.cursor.return_value = cursor

    dbapi = mock.MagicMock()
    dbapi.connect.return_value = connection

    bq = BigQuery()
    bq._client = mock.MagicMock()
    bq._dbapi = dbapi
    return bq


def build_mock_client_for_copying(table_exists=True, app_creds=None):
    bq_client = mock.MagicMock()
    if not table_exists:
        bq_client.get_table.side_effect = exceptions.NotFound("not found")
    bq = BigQuery(app_creds=app_creds)
    bq._client = bq_client
    return bq


def build_mock_base_client(app_creds=None):
    bq = BigQuery(app_creds=app_creds)
    bq._client = mock.MagicMock()
    return bq


def build_mock_cloud_storage_client(tmp_blob_uri=""):
    gcs_client = mock.MagicMock()
    gcs_client.upload_table.return_value = tmp_blob_uri
    return gcs_client


def test_query():
    bq = build_mock_client_for_querying([{"one": 1, "two": 2}])

    result = bq.query("select * from table")

    assert result.num_rows == 1
    assert result.columns == ["one", "two"]
    assert result[0] == {"one": 1, "two": 2}


def test_query__no_results():
    bq = build_mock_client_for_querying([])

    result = bq.query("select * from table limit 0")

    assert isinstance(result, Table)
    assert not len(result)
    assert tuple(result.columns) == ()


@mock.patch("parsons.utilities.files.create_temp_file")
def test_query__no_return(create_temp_file_mock):
    bq = build_mock_client_for_querying([{"one": 1, "two": 2}])
    bq._fetch_query_results = mock.MagicMock()

    result = bq.query("select * from table", return_values=False)

    assert result is None
    bq._fetch_query_results.assert_not_called()


@mock.patch("parsons.utilities.files.create_temp_file")
def test_query_with_transaction(create_temp_file_mock):
    queries = ["select * from table", "select foo from bar"]
    parameters = ["baz"]
    bq = build_mock_client_for_querying([{"one": 1, "two": 2}])
    bq.query = mock.MagicMock()

    result = bq.query_with_transaction(queries=queries, parameters=parameters)
    keyword_args = bq.query.call_args[1]

    assert result is None
    assert all(text in keyword_args["sql"] for text in [*queries, "BEGIN TRANSACTION", "COMMIT"])
    assert keyword_args["parameters"] == parameters
    assert not keyword_args["return_values"]


def test_extract():
    gcs_bucket = "tmp"
    gcs_blob_name = "file/*"
    gs_tmp_destination = f"gs://{gcs_bucket}/{gcs_blob_name}"
    bq = build_mock_client_for_copying(table_exists=False)

    bq.extract(
        gcs_bucket=gcs_bucket, gcs_blob_name=gcs_blob_name, dataset="dataset", table_name="table"
    )

    assert bq.client.extract_table.call_count == 1
    load_call_args = bq.client.extract_table.call_args
    assert load_call_args[1]["destination_uris"] == gs_tmp_destination
    assert load_call_args[1]["job_config"].destination_format == bigquery.DestinationFormat.CSV


def test_get_job():
    tmp_job_id = "1234567890"
    bq = build_mock_base_client()

    bq.client.get_job(job_id=tmp_job_id)

    assert bq.client.get_job.call_count == 1
    assert bq.client.get_job.call_args[1]["job_id"] == tmp_job_id


def test_copy_gcs():
    tmp_blob_uri = "gs://tmp/file"
    bq = build_mock_client_for_copying(table_exists=False)

    bq.copy_from_gcs(gcs_blob_uri=tmp_blob_uri, table_name="dataset.table")

    assert bq.client.load_table_from_uri.call_count == 1
    load_call_args = bq.client.load_table_from_uri.call_args
    assert load_call_args[1]["source_uris"] == tmp_blob_uri
    assert (
        load_call_args[1]["job_config"].write_disposition == bigquery.WriteDisposition.WRITE_EMPTY
    )


def test_copy_gcs__if_exists_truncate():
    tmp_blob_uri = "gs://tmp/file"
    bq = build_mock_client_for_copying(table_exists=False)

    bq.copy_from_gcs(gcs_blob_uri=tmp_blob_uri, table_name="dataset.table", if_exists="truncate")

    load_call_args = bq.client.load_table_from_uri.call_args
    assert load_call_args[1]["source_uris"] == tmp_blob_uri
    assert (
        load_call_args[1]["job_config"].write_disposition
        == bigquery.WriteDisposition.WRITE_TRUNCATE
    )


def test_copy_gcs__if_exists_append():
    tmp_blob_uri = "gs://tmp/file"
    bq = build_mock_client_for_copying(table_exists=False)

    bq.copy_from_gcs(gcs_blob_uri=tmp_blob_uri, table_name="dataset.table", if_exists="append")

    load_call_args = bq.client.load_table_from_uri.call_args
    assert load_call_args[1]["source_uris"] == tmp_blob_uri
    assert (
        load_call_args[1]["job_config"].write_disposition == bigquery.WriteDisposition.WRITE_APPEND
    )


def test_copy_gcs__if_exists_fail():
    tmp_blob_uri = "gs://tmp/file"
    bq = build_mock_client_for_copying(table_exists=False)

    bq.copy_from_gcs(gcs_blob_uri=tmp_blob_uri, table_name="dataset.table", if_exists="truncate")
    bq.table_exists = mock.MagicMock()
    bq.table_exists.return_value = True

    with pytest.raises(Exception, match="Table already exists"):
        bq.copy_from_gcs(
            default_table(),
            "dataset.table",
            tmp_gcs_bucket=TMP_GCS_BUCKET,
            gcs_client=build_mock_cloud_storage_client(),
        )


def test_copy_gcs__if_exists_drop():
    tmp_blob_uri = "gs://tmp/file"
    bq = build_mock_client_for_copying(table_exists=False)
    bq.table_exists = mock.MagicMock()
    bq.table_exists.return_value = True

    bq.copy_from_gcs(gcs_blob_uri=tmp_blob_uri, table_name="dataset.table", if_exists="drop")

    assert bq.client.delete_table.call_count == 1


def test_copy_gcs__bad_if_exists():
    tmp_blob_uri = "gs://tmp/file"
    bq = build_mock_client_for_copying(table_exists=False)
    bq.table_exists = mock.MagicMock()
    bq.table_exists.return_value = True

    if_exists = "foobar"
    with pytest.raises(
        ValueError, match=f"Unexpected value for if_exists: {if_exists}, must be one of"
    ):
        bq.copy_from_gcs(gcs_blob_uri=tmp_blob_uri, table_name="dataset.table", if_exists=if_exists)


@mock.patch("google.cloud.storage.Client")
@mock.patch("parsons.google.google_cloud_storage.load_google_application_credentials")
@mock.patch.object(GoogleCloudStorage, "split_uri", return_value=("tmp", "file.gzip"))
@mock.patch.object(GoogleCloudStorage, "unzip_blob", return_value="gs://tmp/file.csv")
def test_copy_large_compressed_file_from_gcs(unzip_mock, split_mock, *_):
    tmp_blob_uri = "gs://tmp/file.gzip"
    bq = build_mock_client_for_copying(table_exists=False)

    bq.copy_large_compressed_file_from_gcs(gcs_blob_uri=tmp_blob_uri, table_name="dataset.table")

    split_mock.assert_has_calls(
        [mock.call(gcs_uri="gs://tmp/file.gzip"), mock.call(gcs_uri="gs://tmp/file.csv")]
    )
    unzip_mock.assert_called_once_with(
        bucket_name="tmp", blob_name="file.gzip", new_file_extension="csv", compression_type="gzip"
    )
    assert bq.client.load_table_from_uri.call_count == 1
    load_call_args = bq.client.load_table_from_uri.call_args
    assert load_call_args[1]["source_uris"] == "gs://tmp/file.csv"
    assert (
        load_call_args[1]["job_config"].write_disposition == bigquery.WriteDisposition.WRITE_EMPTY
    )


def test_copy_s3():
    table_name = "table_name"
    bucket = "aws_bucket"
    key = "file.gzip"
    aws_access_key_id = "AAAAAA"
    aws_secret_access_key = "BBBBB"
    tmp_gcs_bucket = "tmp"
    bq = build_mock_client_for_copying(table_exists=False)
    gcs_client = build_mock_cloud_storage_client()
    bq.copy_from_gcs = mock.MagicMock()

    bq.copy_s3(
        table_name=table_name,
        bucket=bucket,
        key=key,
        gcs_client=gcs_client,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        tmp_gcs_bucket=tmp_gcs_bucket,
    )

    gcs_client.copy_s3_to_gcs.assert_called_once_with(
        aws_source_bucket=bucket,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        gcs_sink_bucket=tmp_gcs_bucket,
        aws_s3_key=key,
    )
    bq.copy_from_gcs.assert_called_once()
    gcs_client.delete_blob.assert_called_once()


def test_copy():
    tmp_blob_uri = "gs://tmp/file"
    gcs_client = build_mock_cloud_storage_client(tmp_blob_uri)
    tbl = default_table()
    bq = build_mock_client_for_copying(table_exists=False)
    bq._load_table_from_uri = mock.MagicMock()
    bq.get_table_ref = mock.Mock(wraps=bq.get_table_ref)
    table_name = "dataset.table"

    bq.copy(tbl, table_name, tmp_gcs_bucket=TMP_GCS_BUCKET, gcs_client=gcs_client)

    assert gcs_client.upload_table.call_count == 1
    upload_call_args = gcs_client.upload_table.call_args
    assert upload_call_args[0][0] == tbl
    assert upload_call_args[0][1] == TMP_GCS_BUCKET
    tmp_blob_name = upload_call_args[0][2]

    assert bq._load_table_from_uri.call_count == 1
    load_call_args = bq._load_table_from_uri.call_args
    column_types = [
        schema_field.field_type for schema_field in load_call_args[1]["job_config"].schema
    ]
    assert column_types == ["INTEGER", "STRING", "BOOLEAN"]
    assert load_call_args[1]["source_uris"] == tmp_blob_uri

    assert bq.get_table_ref.call_count == 2
    assert bq.get_table_ref.call_args[1]["table_name"] == table_name

    assert gcs_client.delete_blob.call_count == 1
    delete_call_args = gcs_client.delete_blob.call_args
    assert delete_call_args[0][0] == TMP_GCS_BUCKET
    assert delete_call_args[0][1] == tmp_blob_name


def test_copy__credentials_are_correctly_set__from_filepath(bq_creds, mocker):
    mocker.patch("parsons.google.google_cloud_storage.load_google_application_credentials")
    mocker.patch("parsons.google.google_bigquery.load_google_application_credentials")
    bq = build_mock_client_for_copying(table_exists=False, app_creds=bq_creds.cred_path)

    bq.copy(
        default_table(),
        "dataset.table",
        tmp_gcs_bucket=TMP_GCS_BUCKET,
        gcs_client=FakeGoogleCloudStorage(),
    )

    actual_str = Path(os.environ[bq.env_credential_path]).read_text()
    assert actual_str == Path(bq_creds.cred_path).read_text()
    assert bq_creds.cred_contents == json.loads(actual_str)


def test_copy__credentials_are_correctly_set__from_env(bq_creds, mocker):
    mocker.patch("parsons.google.google_cloud_storage.load_google_application_credentials")
    mocker.patch("parsons.google.google_bigquery.load_google_application_credentials")
    # GOOGLE_APPLICATION_CREDENTIALS is already set by the bq_creds fixture; no app_creds passed.
    bq = build_mock_client_for_copying(table_exists=False)

    bq.copy(
        default_table(),
        "dataset.table",
        tmp_gcs_bucket=TMP_GCS_BUCKET,
        gcs_client=FakeGoogleCloudStorage(),
    )

    actual_str = Path(os.environ[bq.env_credential_path]).read_text()
    assert actual_str == Path(bq_creds.cred_path).read_text()
    assert bq_creds.cred_contents == json.loads(actual_str)


def test_copy__credentials_are_correctly_set__from_dict(bq_creds, mocker):
    mocker.patch("parsons.google.google_cloud_storage.load_google_application_credentials")
    mocker.patch("parsons.google.google_bigquery.load_google_application_credentials")
    cred_dict = json.loads(Path(bq_creds.cred_path).read_text())
    bq = build_mock_client_for_copying(table_exists=False, app_creds=cred_dict)

    bq.copy(
        default_table(),
        "dataset.table",
        tmp_gcs_bucket=TMP_GCS_BUCKET,
        gcs_client=FakeGoogleCloudStorage(),
    )

    actual_str = Path(os.environ[bq.env_credential_path]).read_text()
    assert actual_str == Path(bq_creds.cred_path).read_text()
    assert bq_creds.cred_contents == json.loads(actual_str)


def test_copy__if_exists_passed_through():
    tmp_blob_uri = "gs://tmp/file"
    gcs_client = build_mock_cloud_storage_client(tmp_blob_uri)
    tbl = default_table()
    bq = build_mock_client_for_copying(table_exists=False)
    bq._load_table_from_uri = mock.MagicMock()
    bq._process_job_config = mock.Mock(wraps=bq._process_job_config)
    if_exists = "drop"

    bq.copy(
        tbl,
        "dataset.table",
        tmp_gcs_bucket=TMP_GCS_BUCKET,
        gcs_client=gcs_client,
        if_exists=if_exists,
    )

    assert bq._load_table_from_uri.call_count == 1
    assert bq._process_job_config.call_args[1]["if_exists"] == if_exists


@mock.patch.object(BigQuery, "table_exists", return_value=False)
@mock.patch.object(BigQuery, "query", return_value=None)
def test_duplicate_table(query_mock, table_exists_mock):
    source_table = "vendor_table"
    destination_table = "raw_table"
    expected_query = f"""
            CREATE TABLE
            {destination_table}
            CLONE {source_table}
        """
    bq = build_mock_client_for_querying(results=None)

    bq.duplicate_table(source_table=source_table, destination_table=destination_table)

    query_mock.assert_called_once()
    assert query_mock.call_args[1]["sql"] == expected_query


@mock.patch.object(BigQuery, "table_exists", return_value=False)
@mock.patch.object(BigQuery, "delete_table", return_value=None)
@mock.patch.object(BigQuery, "query", return_value=None)
def test_duplicate_table_with_drop(query_mock, delete_mock, table_exists_mock):
    source_table = "vendor_table"
    destination_table = "raw_table"
    bq = build_mock_client_for_querying(results=None)

    bq.duplicate_table(
        source_table=source_table, destination_table=destination_table, drop_source_table=True
    )

    delete_mock.assert_called_once_with(table_name=source_table)


@mock.patch.object(BigQuery, "table_exists", return_value=True)
@mock.patch.object(BigQuery, "query_with_transaction", return_value=None)
@mock.patch.object(BigQuery, "copy", return_value=None)
def test_upsert(copy_mock, query_mock, *_):
    upsert_tbl = Table([["id", "name"], [1, "Jane"]])
    target_table = "my_dataset.my_target_table"
    bq = build_mock_client_for_querying(results=[])

    bq.upsert(
        table_obj=upsert_tbl, target_table=target_table, primary_key="id", distinct_check=False
    )

    copy_mock.assert_called_once()
    assert copy_mock.call_args[1]["tbl"] == upsert_tbl
    assert copy_mock.call_args[1]["template_table"] == target_table

    query_mock.assert_called_once()
    actual_queries = query_mock.call_args[1]["queries"]
    assert "DELETE" in actual_queries[0]
    assert "INSERT" in actual_queries[1]


@mock.patch.object(BigQuery, "query")
def test_get_row_count(query_mock):
    schema = "foo"
    table_name = "bar"
    query_mock.return_value = Table([{"row_count": 2}])
    expected_query = f"SELECT COUNT(*) AS row_count FROM `{schema}.{table_name}`"
    bq = build_mock_client_for_querying(results=Table([{"row_count": 2}]))

    row_count = bq.get_row_count(schema=schema, table_name=table_name)

    query_mock.assert_called_once()
    assert query_mock.call_args[1]["sql"] == expected_query
    assert row_count == 2


# --- copy_between_projects ---
# NOTE: these tests mock the entire GoogleBigQuery object, so they only exercise the
# mock (and, for the logging cases, the stdlib logger) rather than the real connector.
# They are ported faithfully; writing real coverage for copy_between_projects is a
# follow-up.

SOURCE_PROJECT = ("project1",)
SOURCE_DATASET = ("dataset1",)
SOURCE_TABLE = ("table1",)
DESTINATION_PROJECT = ("project2",)
DESTINATION_DATASET = ("dataset2",)
DESTINATION_TABLE = ("table2",)
IF_DATASET_NOT_EXISTS = ("fail",)
IF_TABLE_EXISTS = "fail"


@pytest.fixture
def bq_mock(mocker):
    return mocker.Mock(spec=GoogleBigQuery)


def _call_copy_between_projects(bq_mock):
    bq_mock.copy_between_projects(
        source_project=SOURCE_PROJECT,
        source_dataset=DESTINATION_DATASET,
        source_table=SOURCE_TABLE,
        destination_project=DESTINATION_PROJECT,
        destination_dataset=DESTINATION_DATASET,
        destination_table=DESTINATION_TABLE,
        if_dataset_not_exists=IF_DATASET_NOT_EXISTS,
        if_table_exists=IF_TABLE_EXISTS,
    )


def test_copy_between_projects_called_once_with(bq_mock):
    _call_copy_between_projects(bq_mock)

    bq_mock.copy_between_projects.assert_called_once_with(
        source_project=SOURCE_PROJECT,
        source_dataset=DESTINATION_DATASET,
        source_table=SOURCE_TABLE,
        destination_project=DESTINATION_PROJECT,
        destination_dataset=DESTINATION_DATASET,
        destination_table=DESTINATION_TABLE,
        if_dataset_not_exists=IF_DATASET_NOT_EXISTS,
        if_table_exists=IF_TABLE_EXISTS,
    )


def test_copy_between_projects_logs_dataset_does_not_exist(bq_mock, caplog):
    message = (
        f"Dataset {DESTINATION_DATASET} does not exist and if_dataset_not_exists "
        f"set to {IF_DATASET_NOT_EXISTS}"
    )
    with caplog.at_level(logging.ERROR):
        logging.getLogger().error(message)
        _call_copy_between_projects(bq_mock)

    assert message in caplog.text


def test_copy_between_projects_logs_table_exists(bq_mock, caplog):
    message = (
        f"BigQuery copy failed, Table {DESTINATION_TABLE} exists and if_table_exists "
        f"set to {IF_TABLE_EXISTS}"
    )
    with caplog.at_level(logging.ERROR):
        logging.getLogger().error(message)
        _call_copy_between_projects(bq_mock)

    assert message in caplog.text
