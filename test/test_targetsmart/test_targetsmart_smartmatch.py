import csv
import io
import gzip

import petl
import pytest
from parsons.targetsmart.targetsmart_api import TargetSmartAPI


@pytest.fixture
def intable():
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
def raw_outtable(intable):
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
def prep_intable(intable):
    return intable.addrownumbers(field="matchback_id")


@pytest.fixture
def raw_outcsv(raw_outtable):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(list(raw_outtable))
    return buf.getvalue()


@pytest.fixture
def raw_outgz(raw_outcsv):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="w") as gz:
        gz.write(raw_outcsv.encode("utf8"))
    return buf.getvalue()


@pytest.fixture
def final_outtable(prep_intable, raw_outtable):
    return petl.leftjoin(prep_intable, raw_outtable, key="matchback_id").cutout("matchback_id")


@pytest.fixture
def submit_filename():
    return "parsons_test.csv"


def test_smartmatch(
    intable,
    submit_filename,
    raw_outgz,
    raw_outcsv,
    raw_outtable,
    final_outtable,
    requests_mock,
):
    ts = TargetSmartAPI("mockkey")
    resp1 = {"url": "https://mock_smartmatch_upload_endpoint", "error": None}
    poll_resp = {"url": "https://mock_smartmatch_download_endpoint", "error": None}
    requests_mock.get("https://api.targetsmart.com/service/smartmatch", json=resp1)
    requests_mock.put(resp1["url"])
    requests_mock.get("https://api.targetsmart.com/service/smartmatch/poll", json=poll_resp)
    requests_mock.get(poll_resp["url"], content=raw_outgz)

    results = ts.smartmatch(intable).to_petl()
    assert list(final_outtable) == list(results)
