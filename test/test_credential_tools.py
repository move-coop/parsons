from parsons.tools import credential_tools as ct
import json
import os
import shutil
import unittest


class TestCredentialTool(unittest.TestCase):
    def setUp(self):

        os.environ["TES_VAR1"] = "variable1"
        os.environ["TES_VAR2"] = "variable2"

        self.tmp_folder = "tmp"
        self.json_file = "credentials.json"
        os.mkdir(self.tmp_folder)

        with open(f"{self.tmp_folder}/{self.json_file}", "w") as f:
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

        self.assertDictEqual(ct.decode_credential(encoded_cred, export=False), expected)

    def test_decode_credential_export(self):
        encoded_cred = (
            "PRSNSENVeyJFTkNfVkFSMSI6ICJlbmNvZGVkLXZhcmlhYmxl"
            "LTEiLCAiRU5DX1ZBUjIiOiAiZW5jLXZhci0yIn0="
        )

        expected = {"ENC_VAR1": "encoded-variable-1", "ENC_VAR2": "enc-var-2"}

        self.assertNotIn("ENC_VAR1", os.environ)
        self.assertNotIn("ENC_VAR2", os.environ)

        ct.decode_credential(encoded_cred)

        self.assertIn("ENC_VAR1", os.environ)
        self.assertIn("ENC_VAR2", os.environ)

        self.assertEqual(os.environ["ENC_VAR1"], expected["ENC_VAR1"])
        self.assertEqual(os.environ["ENC_VAR2"], expected["ENC_VAR2"])

    def test_decode_credential_save(self):
        encoded_cred = (
            "PRSNSENVeyJFTkNfVkFSMSI6ICJlbmNvZGVkLXZhcmlhYmxl"
            "LTEiLCAiRU5DX1ZBUjIiOiAiZW5jLXZhci0yIn0="
        )

        expected = {"ENC_VAR1": "encoded-variable-1", "ENC_VAR2": "enc-var-2"}

        file_path = f"{self.tmp_folder}/saved_credentials.json"
        self.assertFalse(os.path.isfile(file_path))

        ct.decode_credential(encoded_cred, export=False, save_path=file_path)

        self.assertTrue(os.path.isfile(file_path))

        with open(file_path, "r") as f:
            cred = json.load(f)

        self.assertDictEqual(cred, expected)

    def test_decode_credential_error(self):
        non_json = "non-json string"

        self.assertRaises(ValueError, ct.decode_credential, non_json)

    def test_encode_from_json_str(self):
        json_str = '{"json": "string"}'
        expected = "PRSNSENVeyJqc29uIjogInN0cmluZyJ9"

        self.assertEqual(ct.encode_from_json_str(json_str), expected)

    def test_encode_from_json_file(self):
        json_path = f"{self.tmp_folder}/{self.json_file}"
        expected = "PRSNSENVeyJqc29uIjogImZpbGUifQ=="

        self.assertEqual(ct.encode_from_json_file(json_path), expected)

    def testencode_from_env(self):
        lst = ["TES_VAR1", "TES_VAR2"]
        expected = "PRSNSENVeyJURVNfVkFSMSI6ICJ2YXJpYWJsZTEiLCAiVEVTX1ZBU" "jIiOiAidmFyaWFibGUyIn0="

        self.assertEqual(ct.encode_from_env(lst), expected)

    def test_encode_from_dict(self):
        dct = {"dict": "variable"}
        expected = "PRSNSENVeyJkaWN0IjogInZhcmlhYmxlIn0="

        self.assertEqual(ct.encode_from_dict(dct), expected)


if __name__ == "__main__":
    unittest.main()
