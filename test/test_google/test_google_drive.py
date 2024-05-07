import unittest
import os
from parsons import GoogleDrive

# Test Slides: https://docs.google.com/presentation/d/19I-kicyaJV53KoPNwt77KJL10fHzWFdZ_c2mW4XJaxc


@unittest.skipIf(
    not os.environ.get("LIVE_TEST"), "Skipping because not running live test"
)
class TestGoogleDrive(unittest.TestCase):
    def setUp(self):

        self.gd = GoogleDrive()

    def test_get_permissions(self):

        file_id = "19I-kicyaJV53KoPNwt77KJL10fHzWFdZ_c2mW4XJaxc"
        p = self.gd.get_permissions(file_id)
        self.assertTrue(True, "anyoneWithLink" in [x["id"] for x in p["permissions"]])

    def test_share_object(self):

        file_id = "19I-kicyaJV53KoPNwt77KJL10fHzWFdZ_c2mW4XJaxc"
        email_addresses = ["bob@bob.com"]

        shared = self.gd.share_object(file_id, email_addresses)
        self.assertTrue(True, list(set([x in p["permissions"] for x in shared]))[0])
