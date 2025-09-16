import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pytest

from parsons.tools import credential_tools as ct


class TestCredentialTool(unittest.TestCase):
    def setUp(self):
        os.environ["TES_VAR1"] = "variable1"
        os.environ["TES_VAR2"] = "variable2"

        self.tmp_folder = tempfile.mkdtemp()
        self.json_file = "credentials.json"

        with (Path(self.tmp_folder) / self.json_file).open(mode="w") as f:
            f.write(json.dumps({"json": "file"}))

    def tearDown(self):
        # Delete tmp folder and files
        shutil.rmtree(self.tmp_folder)

    def test_decode_credential(self):
        encoded_cred = (
            "PRSNSENVeyJFTkNfVkFSMSI6ICJlbmNvZGVkLXZhcmlhYmxl"
            "LTEiLCAiRU5DX1ZBUjIiOiAiZW5jLXZhci0yIn0="
        )

        expected = {"ENC_VAR1": "encoded-variable-1", "ENC_VAR2": "enc-var-2"}

        assert ct.decode_credential(encoded_cred, export=False) == expected

    def test_decode_credential_export(self):
        encoded_cred = (
            "PRSNSENVeyJFTkNfVkFSMSI6ICJlbmNvZGVkLXZhcmlhYmxl"
            "LTEiLCAiRU5DX1ZBUjIiOiAiZW5jLXZhci0yIn0="
        )

        expected = {"ENC_VAR1": "encoded-variable-1", "ENC_VAR2": "enc-var-2"}

        assert "ENC_VAR1" not in os.environ
        assert "ENC_VAR2" not in os.environ

        ct.decode_credential(encoded_cred)

        assert "ENC_VAR1" in os.environ
        assert "ENC_VAR2" in os.environ

        assert os.environ["ENC_VAR1"] == expected["ENC_VAR1"]
        assert os.environ["ENC_VAR2"] == expected["ENC_VAR2"]

    def test_decode_credential_save(self):
        encoded_cred = (
            "PRSNSENVeyJFTkNfVkFSMSI6ICJlbmNvZGVkLXZhcmlhYmxl"
            "LTEiLCAiRU5DX1ZBUjIiOiAiZW5jLXZhci0yIn0="
        )

        expected = {"ENC_VAR1": "encoded-variable-1", "ENC_VAR2": "enc-var-2"}

        file_path = Path(self.tmp_folder) / "saved_credentials.json"
        assert not file_path.is_file()

        ct.decode_credential(encoded_cred, export=False, save_path=str(file_path))

        assert file_path.is_file()

        with file_path.open(mode="r") as f:
            cred = json.load(f)

        assert cred == expected

    def test_decode_credential_error(self):
        non_json = "non-json string"

        with pytest.raises(ValueError, match="Invalid Parsons variable"):
            ct.decode_credential(non_json)

    def test_encode_from_json_str(self):
        json_str = '{"json": "string"}'
        expected = "PRSNSENVeyJqc29uIjogInN0cmluZyJ9"

        assert ct.encode_from_json_str(json_str) == expected

    def test_encode_from_json_file(self):
        json_path = f"{self.tmp_folder}/{self.json_file}"
        expected = "PRSNSENVeyJqc29uIjogImZpbGUifQ=="

        assert ct.encode_from_json_file(json_path) == expected

    def testencode_from_env(self):
        lst = ["TES_VAR1", "TES_VAR2"]
        expected = "PRSNSENVeyJURVNfVkFSMSI6ICJ2YXJpYWJsZTEiLCAiVEVTX1ZBUjIiOiAidmFyaWFibGUyIn0="

        assert ct.encode_from_env(lst) == expected

    def test_encode_from_dict(self):
        dct = {"dict": "variable"}
        expected = "PRSNSENVeyJkaWN0IjogInZhcmlhYmxlIn0="

        assert ct.encode_from_dict(dct) == expected


if __name__ == "__main__":
    unittest.main()
