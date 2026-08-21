import json
import os
from pathlib import Path

import pytest

from parsons.utilities import credential_tools as ct

# A Parsons-encoded credential (the "PRSNSENV" prefix + base64 JSON) and its plaintext.
ENCODED_CRED = (
    "PRSNSENVeyJFTkNfVkFSMSI6ICJlbmNvZGVkLXZhcmlhYmxlLTEiLCAiRU5DX1ZBUjIiOiAiZW5jLXZhci0yIn0="
)
DECODED_CRED = {"ENC_VAR1": "encoded-variable-1", "ENC_VAR2": "enc-var-2"}


@pytest.fixture
def json_file(tmp_path: Path) -> Path:
    path = tmp_path / "credentials.json"
    path.write_text(json.dumps({"json": "file"}))
    return path


def test_decode_credential():
    assert ct.decode_credential(ENCODED_CRED, export=False) == DECODED_CRED


def test_decode_credential_export(preserve_environ):
    assert "ENC_VAR1" not in os.environ
    assert "ENC_VAR2" not in os.environ

    ct.decode_credential(ENCODED_CRED)

    assert os.environ["ENC_VAR1"] == DECODED_CRED["ENC_VAR1"]
    assert os.environ["ENC_VAR2"] == DECODED_CRED["ENC_VAR2"]


def test_decode_credential_save(tmp_path: Path):
    file_path = tmp_path / "saved_credentials.json"
    assert not file_path.is_file()

    ct.decode_credential(ENCODED_CRED, export=False, save_path=str(file_path))

    assert file_path.is_file()
    assert json.loads(file_path.read_text()) == DECODED_CRED


def test_decode_credential_error():
    with pytest.raises(ValueError, match="Invalid Parsons variable"):
        ct.decode_credential("non-json string")


def test_encode_from_json_str():
    assert ct.encode_from_json_str('{"json": "string"}') == "PRSNSENVeyJqc29uIjogInN0cmluZyJ9"


def test_encode_from_json_file(json_file: Path):
    assert ct.encode_from_json_file(str(json_file)) == "PRSNSENVeyJqc29uIjogImZpbGUifQ=="


def test_encode_from_env(monkeypatch):
    monkeypatch.setenv("TES_VAR1", "variable1")
    monkeypatch.setenv("TES_VAR2", "variable2")

    expected = "PRSNSENVeyJURVNfVkFSMSI6ICJ2YXJpYWJsZTEiLCAiVEVTX1ZBUjIiOiAidmFyaWFibGUyIn0="
    assert ct.encode_from_env(["TES_VAR1", "TES_VAR2"]) == expected


def test_encode_from_dict():
    assert ct.encode_from_dict({"dict": "variable"}) == "PRSNSENVeyJkaWN0IjogInZhcmlhYmxlIn0="
