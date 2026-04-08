import gzip
import re
from zipfile import ZipFile

import pytest

from parsons import CatalistMatch, Table


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
        sftp_root / remote.lstrip("/")
    ).parent.mkdir(parents=True, exist_ok=True) or __import__("shutil").copy2(
        local, sftp_root / remote.lstrip("/")
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


def test_validate_table_logic(client):
    """Ensure validation catches missing required columns."""
    bad_tbl = Table([{"first_name": "OnlyName"}])  # Missing last_name

    with pytest.raises(ValueError, match="missing_required_columns"):
        client.validate_table(bad_tbl)
