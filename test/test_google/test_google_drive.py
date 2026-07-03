import random
import string

import pytest

from parsons import GoogleDrive

# Test Slides: https://docs.google.com/presentation/d/19I-kicyaJV53KoPNwt77KJL10fHzWFdZ_c2mW4XJaxc


@pytest.fixture
def gd():
    """Provide a live GoogleDrive connector."""
    return GoogleDrive()


@pytest.mark.live
def test_get_permissions(gd):
    file_id = "19I-kicyaJV53KoPNwt77KJL10fHzWFdZ_c2mW4XJaxc"
    p = gd.get_permissions(file_id)
    assert "anyoneWithLink" in [x["id"] for x in p["permissions"]]


@pytest.mark.live
def test_share_object(gd):
    file_id = "19I-kicyaJV53KoPNwt77KJL10fHzWFdZ_c2mW4XJaxc"
    email = "".join(random.choices(string.ascii_letters, k=10)) + "@gmail.com"
    email_addresses = [email]

    before = gd.get_permissions(file_id)["permissions"]
    gd.share_object(file_id, email_addresses)
    after = gd.get_permissions(file_id)["permissions"]
    assert len(after) > len(before)
