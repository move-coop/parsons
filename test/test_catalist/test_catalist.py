import gzip
import time
from zipfile import ZipFile

import pytest

from parsons import CatalistMatch, Table

TEST_CREDS = {
    "client_id": "id",
    "client_secret": "secret",
    "sftp_username": "user",
    "sftp_password": "pw",
}


@pytest.fixture
def client(fake_sftp_backend):
    """Provides a CatalistMatch client using the fake SFTP backend."""
    match = CatalistMatch(**TEST_CREDS)
    match._token_expired_at = time.time() + 99999
    return match


def test_load_table_to_sftp_integrity(client):
    """Verify that the .gz file is real and has the right CSV content."""
    tbl = Table([{"first_name": "John", "last_name": "Doe"}])

    sftp_url = client.load_table_to_sftp(tbl)

    filename = sftp_url.replace("file://", "")
    uploaded_path = client.sftp.root / "myUploads" / filename

    assert uploaded_path.exists()

    with gzip.open(uploaded_path, "rt") as f:
        content = f.read()
        assert "first_name,last_name" in content
        assert "John,Doe" in content


def test_load_matches_unzip_logic(client, tmp_path):
    """Test that we can handle a real ZIP file from the 'remote' server."""
    job_id = "999"

    csv_data = "COL1-first_name\tDWID\nJane\t123"
    csv_file = tmp_path / "results.csv"
    csv_file.write_text(csv_data)

    zip_path = client.sftp.root / "myDownloads" / f"match_{job_id}.zip"
    with ZipFile(zip_path, "w") as zf:
        zf.write(csv_file, arcname="results.csv")

    result_table = client.load_matches(job_id)

    assert result_table[0]["DWID"] == "123"
    assert "COL1-first_name" in result_table.columns


def test_validate_table_errors(client):
    """Test validation logic using a real Table object."""
    bad_table = Table([{"first_name": "NoLastName"}])

    with pytest.raises(ValueError, match="missing_required_columns"):
        client.validate_table(bad_table)
