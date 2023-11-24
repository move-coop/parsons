import re


def format_phone_number(phone_number, country_code="1"):
    """
    Formats a phone number in E.164 format.

    Args:
        phone_number (str): The phone number to be formatted.
        country_code (str): The country code to be used as a prefix.
        Defaults to "1" (United States).

    Returns:
        str: The formatted phone number in E.164 format.
    """
    # Remove non-numeric characters and leading zeros
    digits = re.sub(r"[^\d]", "", phone_number.lstrip("0"))

    # Check if the phone number is valid
    if len(digits) < 10:
        raise ValueError("Invalid phone number.")

    # Handle country code prefix
    if not digits.startswith(country_code):
        digits = country_code + digits

    # Format the phone number in E.164 format
    formatted_number = "+" + digits

    # Check if the formatted number is valid
    # Implement validation logic here

    return formatted_number
