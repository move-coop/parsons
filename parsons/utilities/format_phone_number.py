import re


def format_phone_number(phone_number, country_code="1"):
    """
    Formats a phone number in E.164 format, which is the international standard for phone numbers.
    Example: Converts "555-555-5555" -> "+15555555555"

    `Args:`
        phone_number (str):
            The phone number to be formatted.
        country_code (str):
            The country code to be used as a prefix.
        Defaults to "1" (United States).

    `Returns:`
        str:
            The formatted phone number in E.164 format.
    """
    # Remove non-numeric characters and leading zeros
    digits = re.sub(r"[^\d]", "", phone_number.lstrip("0"))

    # Check if the phone number is valid
    if len(digits) < 10:
        return None

    # Handle country code prefix
    if not digits.startswith(country_code):
        digits = country_code + digits

    # Format the phone number in E.164 format
    formatted_number = "+" + digits

    return formatted_number
