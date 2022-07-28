"""
This module contains functions that can be passed to the Parsons Table convert_column
method. They take in an original value and return a new value. They can, of course, also be used
on their own.
"""

from dateutil.parser import parse
import datetime
import re


# Datetime conversion functions


def date_to_timestamp(value, tzinfo=datetime.timezone.utc):
    """Convert any date value into a Unix timestamp.

    `Args:`
        value: int or str or datetime
            Value to parse
        tzinfo: datetime.timezone
            `Optional`: Timezone for the datetime; defaults to UTC.
    `Returns:`
        Unix timestamp (int)
    """

    parsed_date = parse_date(value)

    if not parsed_date:
        return None

    if not parsed_date.tzinfo:
        parsed_date = parsed_date.replace(tzinfo=tzinfo)

    return int(parsed_date.timestamp())


def parse_date(value, tzinfo=datetime.timezone.utc):
    """Parse an arbitrary date value into a Python datetime.

    If no value is provided (i.e., the value is None or empty), then the return value will be
    None.

    `Args:`
        value: int or str or datetime
            Value to parse
        tzinfo: datetime.timezone
            `Optional`: Timezone for the datetime; defaults to UTC.
    `Returns:`
        datetime.datetime or None
    """

    if not value:
        return None

    # If it's a number, we (probably) have a unix timestamp
    if isinstance(value, int):
        parsed = datetime.datetime.fromtimestamp(value, tzinfo)
    elif isinstance(value, datetime.datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = parse(value)
    else:
        raise TypeError(
            'Unable to parse value; must be one of string or int or datetime, but got type '
            f'{type(value)}')

    if not parsed.tzinfo:
        parsed = parsed.replace(tzinfo=tzinfo)

    return parsed


def timestamp_to_readable(value, tzinfo=datetime.timezone.utc, format_as='%Y-%m-%d %H:%M:%S'):
    """Converts a Unix timestamp into a common human-readable format.

    `Args:`
        value: int or str or datetime
            Must correspond to a unix timestamp
        tzinfo: datetime.timezone
            `Optional`: Timezone for the datetime; defaults to UTC.
        format_as: str
            Should use strftime syntax; defaults to '%Y-%m-%d %H:%M:%S'
    `Returns:`
        str
    """
    datetime_obj = parse_date(value, tzinfo)
    return datetime_obj.strftime(format_as)


# Flatten contacts

def get_primary_contact_from_nested(contact_list, get_first=True, selector=None):
    """Extracts single contact value from list of dictionaries.

    Multiple connectors, including Mobilize and Action Network, have a format for
    contact info that looks like:

    [{"primary": True, "number": "111-111-1111"}]

    This helper method helps "flatten" the dictionary by returning the primary number (or,
    if no primary number is found and get_first is True, the first number found).

    If no selector is passed in, the function tries common options and, finally, tries to get the
    selector from the dictionary.

    `Args:`
        contact_list: list
            List containing dictionaries with format {"primary": True, $selector: $value}
        get_first: boolean
            `Optional`: If primary contact is not found, return first contact if it exists rather
            than None; defaults to True
        selector: str
            `Optional`:
    `Returns:`
        str
    """

    if not contact_list:
        return

    # get selector if not supplied

    if not selector:

        for option in ["number", "postal_code", "address"]:  # try common options
            if option in contact_list[0]:
                selector = option
                break

        if not selector:  # if selector still not found, look in dict
            dict_keys = list(contact_list[0].keys())
            dict_keys.pop("primary")
            selector = dict_keys[0]  # NOTE: this will break on dicts that have additional keys

    # extract contact using selector

    extracted_contacts = []

    for contact in contact_list:

        if contact["primary"]:
            return contact[selector]
        else:
            extracted_contacts.append(contact[selector])

    if get_first and extracted_contacts:
        return extracted_contacts[0]

    return None


def clean_US_phones(value, simple=True):
    """Provides simple validation and standardization for US phone numbers.

    Given a phone number, standardizes to either a simple format or a fancy format.

    Simple: 10 digit format with no country code, spaces or extra characters, ie: 3334445555
    Fancy: 16 digit format with parens and country code, ie: 1-(333)-444-5555

    Assumes North American phone number and will incorrectly reject most international numbers.

    `Args:`
        value: str
            Value containing phone number to parse
        simple: boolean
            `Optional`: Indicates format phone number should be standardized to; defaults to True
    `Returns:`
        str
    """

    # Parse string and standardize to 10 digit format

    value = value.split("x")[0]  # if there's an x in the old_number, use only numbers before the x

    parsed_value = re.compile(r'\d+(?:\.\d+)?').findall(value)  # extracts digits only
    value = "".join(parsed_value)

    if len(value) == 11 and value[0] == 1:
        value = value[1:]   # remove first digit if it's 1

    if len(value) != 10:  # all valid numbers should have 10 digits
        return None

    if simple:
        return value

    return f"1-({value[:3]})-{value[3:6]}-{value[6:10]}"  # fancy version
