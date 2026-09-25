import gzip
import re
from zipfile import ZipFile

import pytest

from parsons import CatalistMatch, Table
from parsons.catalist.catalist import _strip_lone_quotes


@pytest.fixture
def client(mocker, tmp_path, requests_mock):
    requests_mock.post(
        "https://auth.catalist.us/oauth/token",
        json={"access_token": "fake_token", "expires_in": 3600},
    )
    requests_mock.get(
        re.compile("/mapi/status/id/"), json={"process": {"processState": "Finished"}}
    )
    # Generic catch-all for the 'upload' call which returns [metadata_dict]
    requests_mock.get(re.compile("/mapi/upload/"), json=[{"id": "999", "status": "queued"}])

    sftp_root = tmp_path / "sftp"
    (sftp_root / "myUploads").mkdir(parents=True)
    (sftp_root / "myDownloads").mkdir(parents=True)

    mock_sftp = mocker.patch("parsons.catalist.catalist.SFTP").return_value
    mock_sftp.root = sftp_root

    mock_sftp.put_file.side_effect = lambda local, remote: (
        (sftp_root / remote.lstrip("/")).parent.mkdir(parents=True, exist_ok=True)
        or __import__("shutil").copy2(local, sftp_root / remote.lstrip("/"))
    )

    mock_sftp.list_directory.side_effect = lambda path: [
        f.name for f in (sftp_root / path.lstrip("/")).iterdir()
    ]

    mock_sftp.get_file.side_effect = lambda remote_path, **kw: str(
        sftp_root / remote_path.lstrip("/")
    )

    return CatalistMatch("id", "secret", "user", "pass")


def test_upload_flow(client):
    """Verify that upload() hits the API and puts a GZipped file on SFTP."""
    tbl = Table([{"first_name": "John", "last_name": "Doe"}])

    response = client.upload(tbl, description="test_job")

    assert response["id"] == "999"
    uploaded_files = list((client.sftp.root / "myUploads").glob("*.csv.gz"))
    assert len(uploaded_files) == 1

    with gzip.open(uploaded_files[0], "rt") as f:
        assert "John,Doe" in f.read()


def test_load_matches_unzip(client, tmp_path):
    """Verify that load_matches correctly pulls from SFTP and parses the TSV."""
    job_id = "999"
    results_csv = tmp_path / "results.csv"
    results_csv.write_text("COL1-first_name\tDWID\nJane\t123")

    zip_path = client.sftp.root / "myDownloads" / f"match_{job_id}.zip"
    with ZipFile(zip_path, "w") as zf:
        zf.write(results_csv, arcname="results.csv")

    table = client.load_matches(job_id)

    assert table[0]["DWID"] == "123"
    assert table.columns == ["COL1-first_name", "DWID"]


def test_strip_lone_quotes():
    """Verify _strip_lone_quotes only removes a quote char from a line
    that has exactly one, leaving balanced or ambiguous (>1 stray) lines
    untouched.
    """
    text = (
        "no_quotes\tplain\n"
        'one_quote\t"BN2\n'
        'balanced\t"quoted value"\n'
        'three_quotes\t"a"b"\n'
        'last_line_no_newline\t"stray'
    )

    cleaned = _strip_lone_quotes(text)
    lines = cleaned.splitlines()

    assert lines[0] == "no_quotes\tplain"
    assert lines[1] == "one_quote\tBN2"
    assert lines[2] == 'balanced\t"quoted value"'
    assert lines[3] == 'three_quotes\t"a"b"'
    assert lines[4] == "last_line_no_newline\tstray"


def test_from_csv_handles_unbalanced_quote_after_stripping(tmp_path):
    """Verify that, after running raw text through _strip_lone_quotes, an
    unbalanced quote no longer makes csv.reader swallow the rest of the
    file.

    A field like `"BN2` (an unescaped, unclosed quote) would otherwise make
    csv.reader's default Excel dialect treat it as the start of a quoted
    field spanning the rest of the file, eventually raising
    `_csv.Error: field larger than field limit`. load_matches strips such
    lone quotes before parsing (parsons/catalist/catalist.py).
    """
    raw_text = 'COL1-first_name\tCOL2-zip\tDWID\nJane\t"BN2\t123\nJohn\t90210\t456'
    results_csv = tmp_path / "results.csv"
    results_csv.write_text(_strip_lone_quotes(raw_text))

    table = Table.from_csv(str(results_csv), delimiter="\t")

    assert table.num_rows == 2
    assert table[0]["COL2-zip"] == "BN2"
    assert table[0]["DWID"] == "123"
    assert table[1]["COL1-first_name"] == "John"
    assert table[1]["COL2-zip"] == "90210"
    assert table[1]["DWID"] == "456"


def test_from_csv_preserves_embedded_tab_in_quoted_field(tmp_path):
    r"""Verify that, unlike quoting=csv.QUOTE_NONE, stripping only lone
    quotes preserves a well-formed (balanced) quoted field that contains
    an embedded delimiter.

    A value like `"John\tJr"` has two quote chars, so _strip_lone_quotes
    leaves it untouched, and default csv quoting parses it as a single
    field with a literal tab inside.
    """
    raw_text = 'COL1-name\tDWID\n"John\tJr"\t999\nJane\t456'
    results_csv = tmp_path / "results.csv"
    results_csv.write_text(_strip_lone_quotes(raw_text))

    table = Table.from_csv(str(results_csv), delimiter="\t")

    assert table.num_rows == 2
    assert table[0]["COL1-name"] == "John\tJr"
    assert table[0]["DWID"] == "999"
    assert table[1]["COL1-name"] == "Jane"
    assert table[1]["DWID"] == "456"


def test_validate_table_logic(client):
    """Ensure validation catches missing required columns."""
    bad_tbl = Table([{"first_name": "OnlyName"}])  # Missing last_name

    with pytest.raises(ValueError, match="missing_required_columns"):
        client.validate_table(bad_tbl)


def test_load_table_to_sftp_with_subfolder(client):
    """Verify that specifying a subfolder creates the dir and places the file there."""
    tbl = Table([{"first_name": "John", "last_name": "Doe"}])
    subfolder = "campaign_2024"
    sftp_url = client.load_table_to_sftp(tbl, input_subfolder=subfolder)

    assert subfolder in sftp_url
    assert sftp_url.startswith(f"file://{subfolder}/")

    target_dir = client.sftp.root / "myUploads" / subfolder
    assert target_dir.is_dir()

    uploaded_files = list(target_dir.glob("*.csv.gz"))
    assert len(uploaded_files) == 1
    assert uploaded_files[0].exists()


def test_load_table_to_sftp_subfolder_already_exists(client):
    """Verify it doesn't fail if the subfolder already exists."""
    tbl = Table([{"first_name": "Jane", "last_name": "Doe"}])
    subfolder = "existing_folder"

    # Pre-create the folder
    (client.sftp.root / "myUploads" / subfolder).mkdir(parents=True)

    # This should run without calling make_directory (or at least without error)
    client.load_table_to_sftp(tbl, input_subfolder=subfolder)

    uploaded_files = list((client.sftp.root / "myUploads" / subfolder).glob("*.csv.gz"))
    assert len(uploaded_files) == 1
