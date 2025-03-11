import csv
import gzip
import io
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import petl
import pytest
from petl.util.base import TableWrapper

from parsons.targetsmart.targetsmart_api import TargetSmartAPI


@pytest.fixture
def intable() -> TableWrapper:
    return petl.wrap(
        [
            [
                "first_name",
                "last_name",
                "address1",
                "email",
                "phone",
                "some_unknown_field",
            ],
            ["Bob", "Smith", "123 Main", "bob@example.com", "1231231234", "foo"],
            ["Alice", "Example", "123 Main", "", "", "bar"],
            ["Sally", "Example", "123 Main", "", "", ""],
        ]
    )


@pytest.fixture
def raw_outtable(intable: TableWrapper) -> tuple:
    return (
        intable.addrownumbers(field="ts__input_row")
        .addrownumbers(field="ts__row")
        .addrownumbers(field="matchback_id")
        .convert("ts__input_row", str)
        .convert("ts__row", str)
        .addfield("tsmart_match_code", "Y")
        .addfield("vb.voterbase_id", "OH-123")
    )


@pytest.fixture
def prep_intable(intable: TableWrapper) -> TableWrapper:
    return intable.addrownumbers(field="matchback_id")


@pytest.fixture
def raw_outcsv(raw_outtable: tuple) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(list(raw_outtable))
    return buf.getvalue()


@pytest.fixture
def raw_outgz(raw_outcsv: str) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="w") as gz:
        gz.write(raw_outcsv.encode("utf8"))
    return buf.getvalue()


@pytest.fixture
def final_outtable(prep_intable: TableWrapper, raw_outtable: tuple) -> TableWrapper:
    return petl.leftjoin(prep_intable, raw_outtable, key="matchback_id").cutout("matchback_id")


def smartmatch_requests_mock(requests_mock: MagicMock, raw_outgz: bytes):
    resp1 = {"url": "https://mock_smartmatch_upload_endpoint", "error": None}
    requests_mock.get("https://api.targetsmart.com/service/smartmatch", json=resp1)
    requests_mock.put(resp1["url"])
    poll_resp = {"url": "https://mock_smartmatch_download_endpoint", "error": None}
    requests_mock.get("https://api.targetsmart.com/service/smartmatch/poll", json=poll_resp)
    requests_mock.get(poll_resp["url"], content=raw_outgz)
    return requests_mock


def test_smartmatch_returned_petl(
    intable: TableWrapper,
    raw_outgz: bytes,
    final_outtable: TableWrapper,
    requests_mock: MagicMock,
):
    ts = TargetSmartAPI("mockkey")
    smartmatch_requests_mock(requests_mock, raw_outgz)

    results = ts.smartmatch(intable).to_petl()
    assert list(final_outtable) == list(results)


def test_smartmatch_output_csv_exists(
    intable: TableWrapper,
    raw_outgz: bytes,
    requests_mock: MagicMock,
):
    ts = TargetSmartAPI("mockkey")
    smartmatch_requests_mock(requests_mock, raw_outgz)

    temp_dir = tempfile.mkdtemp()
    ts.smartmatch(intable, tmp_location=temp_dir)
    assert sorted(Path(temp_dir).glob("smartmatch_output*.csv")) != []


def test_smartmatch_keep_smartmatch_input_csv(
    intable: TableWrapper,
    raw_outgz: bytes,
    requests_mock: MagicMock,
):
    ts = TargetSmartAPI("mockkey")
    smartmatch_requests_mock(requests_mock, raw_outgz)

    temp_dir = tempfile.mkdtemp()
    ts.smartmatch(intable, tmp_location=temp_dir, keep_smartmatch_input_file=True)
    assert sorted(Path(temp_dir).glob("smartmatch_input*.csv")) != []


def test_smartmatch_keep_smartmatch_input_csv_false(
    intable: TableWrapper,
    raw_outgz: bytes,
    requests_mock: MagicMock,
):
    ts = TargetSmartAPI("mockkey")
    smartmatch_requests_mock(requests_mock, raw_outgz)

    temp_dir = tempfile.mkdtemp()
    ts.smartmatch(intable, tmp_location=temp_dir, keep_smartmatch_input_file=False)
    assert sorted(Path(temp_dir).glob("smartmatch_input*.csv")) == []


def test_smartmatch_keep_smartmatch_output_gz(
    intable: TableWrapper,
    raw_outgz: bytes,
    requests_mock: MagicMock,
):
    ts = TargetSmartAPI("mockkey")
    smartmatch_requests_mock(requests_mock, raw_outgz)

    temp_dir = tempfile.mkdtemp()
    ts.smartmatch(intable, tmp_location=temp_dir, keep_smartmatch_output_gz_file=True)
    assert sorted(Path(temp_dir).glob("smartmatch_output*.csv.gz")) != []


def test_smartmatch_keep_smartmatch_output_gz_false(
    intable: TableWrapper,
    raw_outgz: bytes,
    requests_mock: MagicMock,
):
    ts = TargetSmartAPI("mockkey")
    smartmatch_requests_mock(requests_mock, raw_outgz)

    temp_dir = tempfile.mkdtemp()
    ts.smartmatch(intable, tmp_location=temp_dir, keep_smartmatch_output_gz_file=False)
    assert sorted(Path(temp_dir).glob("smartmatch_output*.csv.gz")) == []
