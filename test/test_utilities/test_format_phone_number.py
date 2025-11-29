import unittest

from parsons.utilities.format_phone_number import format_phone_number


class TestFormatPhoneNumber(unittest.TestCase):
    def test_format_phone_number_local_us_number(self):
        phone_number = "555-123-4567"
        expected_result = "+15551234567"
        assert format_phone_number(phone_number) == expected_result

    def test_format_phone_number_us_number_with_leading_1(self):
        phone_number = "15551234567"
        expected_result = "+15551234567"
        assert format_phone_number(phone_number) == expected_result

    def test_format_phone_number_international_number(self):
        phone_number = "+441234567890"
        expected_result = "+441234567890"
        assert format_phone_number(phone_number, country_code="44") == expected_result

    def test_format_phone_number_invalid_length(self):
        phone_number = "12345"
        assert format_phone_number(phone_number) is None


if __name__ == "__main__":
    unittest.main()
