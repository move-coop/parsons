"""
Routines for interacting with TargetSmart's developer API.

https://docs.targetsmart.com/developers/tsapis/v2/index.html
"""

import logging

import petl
import requests

from parsons.etl.table import Table
from parsons.utilities import check_env

from .targetsmart_smartmatch import SmartMatch

URI = "https://api.targetsmart.com/"

logger = logging.getLogger(__name__)


class TargetSmartConnector:
    def __init__(self, api_key):
        self.uri = URI
        self.api_key = check_env.check("TS_API_KEY", api_key)
        self.headers = {"x-api-key": self.api_key}

    def request(self, url, args=None, raw=False):
        r = requests.get(url, headers=self.headers, params=args)

        # This allows me to deal with data that needs to be munged.
        if raw:
            return r.json()

        return Table(r.json()["output"])


class Person:
    def __init__(self):
        return None

    def data_enhance(self, search_id, search_id_type="voterbase", state=None):
        """
        Searches for a record based on an id or phone or email address.

        Args:
            search_id (str): The primary key or email address or phone number.
            search_id_type (str, optional): One of ``voterbase``, ``exacttrack``, ``phone``,
                ``email``, ``smartvan``, ``votebuilder``, ``voter``, ``household``. Defaults to "voterbase".
            state (str, optional): Two character state code. Required if ``search_id_type`` of ``smartvan``,
                ``votebuilder`` or ``voter``. Defaults to None.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        if search_id_type in ["smartvan", "votebuilder", "voter"] and state is None:
            raise KeyError(f"Search ID type '{search_id_type}' requires state kwarg")

        if search_id_type not in (
            "voterbase",
            "exacttrack",
            "phone",
            "email",
            "smartvan",
            "votebuilder",
            "voter",
            "household",
        ):
            raise ValueError("Search_id_type is not valid")

        url = self.connection.uri + "person/data-enhance"

        args = {
            "search_id": search_id,
            "search_id_type": search_id_type,
            "state": state,
        }

        return self.connection.request(url, args=args)

    def radius_search(
        self,
        first_name,
        last_name,
        middle_name=None,
        name_suffix=None,
        latitude=None,
        longitude=None,
        address=None,
        radius_size=10,
        radius_unit="miles",
        max_results=10,
        gender="a",
        age_min=None,
        age_max=None,
        composite_score_min=1,
        composite_score_max=100,
        last_name_exact=True,
        last_name_is_prefix=False,
        last_name_prefix_length=10,
        address_type="reg",
    ):
        """
        Search for a person based on a specified radius.

        Args:
            first_name (str): One or more alpha characters. Required.
            last_name (str): One or more alpha characters. Required.
            middle_name (str, optional): One or more alpha characters. Defaults to None.
            name_suffix (str, optional): One or more alpha characters. Defaults to None.
            latitude: Float Floating point number (e.g. 33.738987255507). Defaults to None.
            longitude: Float Floating point number (e.g. -116.40833849559). Defaults to None.
            address (str, optional): Any geocode-able address. Defaults to None.
            address_type: Str
                ``reg`` for registration (default) or ``tsmart`` for TargetSmart. Defaults to "reg".
            radius_size (int, optional): A positive integer where combined with ``radius_unit`` does not exceed 120
                miles. Defaults to 10.
            radius_unit (str, optional): One of ``meters``, ``feet``, ``miles`` (default), or
                ``kilometers``. Defaults to "miles".
            max_results (int, optional): Default of ``10``. An integer in range [0 - 100].
                Defaults to 10.
            gender (str, optional): Default of ``a``. One of ``m``, ``f``, ``u``, ``a``. Defaults to "a".
            age_min (int, optional): A positive integer. Defaults to None.
            age_max (int, optional): A positive integer. Defaults to None.
            composite_score_min (int, optional): An integer in range [1 - 100]. Filter out results with composite
                score less than this value. Defaults to 1.
            composite_score_max (int, optional): An integer in range [1 - 100]. Filter out results with composite
                score greater than this value. Defaults to 100.
            last_name_exact: Bool

                last name is not longer than 10 characters. As an example, “anders” is less likely to match to
                “anderson” with this enabled. Disable this option if you are using either ``last_name_is_prefix`` or
                ``last_name_prefix_length``. Defaults to True.
            last_name_is_prefix (bool, optional): Enable this parameter if your search last name is truncated.
                This can be common for some client applications that for various reasons do not have full last names.
                Use this parameter along with
                ``last_name_prefix_length`` to configure the length of the last name prefix. This parameter is ignored
                if ``last_name_exact`` is enabled. Defaults to False.
            last_name_prefix_length: Int

                finding relative matches. This value must be between 3 and 10. This parameter is ignored if
                last_name_exact is enabled. Defaults to 10.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        if (latitude is None or longitude is None) and address is None:
            raise ValueError("Lat/Long or Address required")

        if not first_name:
            raise ValueError("First name is required")

        if not last_name:
            raise ValueError("Last name is required")

        # Convert booleans
        for a in [last_name_exact, last_name_is_prefix]:
            a = str(a)

        url = self.connection.uri + "person/radius-search"

        args = {
            "first_name": first_name,
            "last_name": last_name,
            "middle_name": middle_name,
            "name_suffix": name_suffix,
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "address_type": address_type,
            "radius_size": radius_size,
            "radius_unit": radius_unit,
            "max_results": max_results,
            "gender": gender,
            "age_min": age_min,
            "age_max": age_max,
            "composite_score_min": composite_score_min,
            "composite_score_max": composite_score_max,
            "last_name_exact": last_name_exact,
            "last_name_is_prefix": last_name_is_prefix,
            "last_name_prefix_length": last_name_prefix_length,
        }

        r = self.connection.request(url, args=args, raw=True)
        return Table(list(r["output"])).unpack_dict("data_fields", prepend=False)

    def phone(self, table):
        """
        Match based on a list of 500 phones numbers.

        Table can contain up to 500 phone numbers to match

        Args:
            table: Table See :ref:`parsons-table`. One row per phone number, up to 500 phone numbers.

        Returns:
            See :ref:`parsons-table` for output options.

        """
        url = self.connection.uri + "person/phone-search"

        args = {"phones": list(petl.values(table.table, 0))}

        return Table(self.connection.request(url, args=args, raw=True)["result"])


class Service:
    def __init__(self):
        return None

    def district(
        self,
        search_type="zip",
        address=None,
        zip5=None,
        zip4=None,
        state=None,
        latitude=None,
        longitude=None,
    ):
        """
        Return district information based on a geographic point.

        The method allows you to search based on the following:

        .. list-table::
            :widths: 30 30 30
            :header-rows: 1

            * - Search Type
              - ``search_type``
              - Required kwarg(s)
            * - Zip Code
              - ``zip``
              - ``zip5``, ``zip4``
            * - Address
              - ``address``
              - ``address``
            * - Point
              - ``point``
              - ``latitude``, ``longitude``

        Args:
            search_type (str, optional): The type of district search to perform. One of ``zip``, ``address`` or
                ``point``. Defaults to "zip".
            address (str, optional): An uparsed full address. Defaults to None.
            zip5 (str, optional): The USPS Zip5 code. Defaults to None.
            zip4 (str, optional): The USPS Zip4 code. Defaults to None.
            state (str, optional): The two character state code. Defaults to None.
            latitude: Float or str Valid latitude floating point. Defaults to None.
            longitude: Float or str Valid longitude floating point. Defaults to None.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        if search_type == "zip" and None in [zip5, zip4]:
            raise ValueError("Search type 'zip' requires 'zip5' and 'zip4' arguments")

        elif search_type == "point" and None in [latitude, longitude]:
            raise ValueError("Search type 'point' requires 'latitude' and 'longitude' arguments")

        elif search_type == "address" and None in [address]:
            raise ValueError("Search type 'address' requires 'address' argument")

        elif search_type not in ["zip", "point", "address"]:
            raise KeyError("Invalid 'search_type' provided.")

        else:
            pass

        url = self.connection.uri + "service/district"

        args = {
            "search_type": search_type,
            "address": address,
            "zip5": zip5,
            "zip4": zip4,
            "state": state,
            "latitude": latitude,
            "longitude": longitude,
        }

        return Table([self.connection.request(url, args=args, raw=True)["match_data"]])


class Voter:
    def __init__(self, connection):
        self.connection = connection

    def voter_registration_check(
        self,
        first_name=None,
        last_name=None,
        state=None,
        street_number=None,
        street_name=None,
        city=None,
        zip_code=None,
        age=None,
        dob=None,
        phone=None,
        email=None,
        unparsed_full_address=None,
    ):
        """
        Searches for a registered individual, returns matches.

        A search must include the at minimum first name, last name and state.

        Args:
            first_name (str, optional): Required; One or more alpha characters. Trailing wildcard allowed.
                Defaults to None.
            last_name (str, optional): Required; One or more alpha characters. Trailing wildcard allowed.
                Defaults to None.
            state (str, optional): Required; Two character state code (e.g. ``NY``). Defaults to None.
            street_number (str, optional): Optional; One or more alpha characters. Trailing wildcard allowed.
                Defaults to None.
            street_name (str, optional): Optional; One or more alpha characters. Trailing wildcard allowed.
                Defaults to None.
            city (str, optional): Optional; The person's home city. Defaults to None.
            zip_code (str, optional): Optional; Numeric characters. Trailing wildcard allowed.
                Defaults to None.
            age (int, optional): Optional; One or more integers. Trailing wildcard allowed.
                Defaults to None.
            dob (str, optional): Optional; Numeric characters in YYYYMMDD format. Trailing wildcard allowed.
                Defaults to None.
            phone (str, optional): Optional; Integer followed by 0 or more * or integers. Defaults to None.
            email (str, optional): Optional; Alphanumeric character followed by 0 or more * or legal characters
                (alphanumeric, @, -, .). Defaults to None.
            unparsed_full_address (str, optional): Optional; One or more alphanumeric characters.
                No wildcards. Defaults to None.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        url = self.connection.uri + "voter/voter-registration-check"

        if None in [first_name, last_name, state]:
            raise ValueError(
                """Function must include at least first_name,
                             last_name, and state."""
            )

        args = {
            "first_name": first_name,
            "last_name": last_name,
            "state": state,
            "street_number": street_number,
            "street_name": street_name,
            "city": city,
            "zip_code": zip_code,
            "age": age,
            "dob": dob,
            "phone": phone,
            "email": email,
            "unparsed_full_address": unparsed_full_address,
        }

        return self.connection.request(url, args=args, raw=True)


class TargetSmartAPI(Voter, Person, Service, SmartMatch):
    def __init__(self, api_key=None):
        self.connection = TargetSmartConnector(api_key=api_key)
