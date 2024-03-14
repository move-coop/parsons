from requests import request
import math
import json
import time
from parsons.etl import Table
from parsons.utilities import check_env
import logging

logger = logging.getLogger(__name__)

COPPER_URI = "https://api.prosperworks.com/developer_api/v1"


class Copper(object):
    """
    Instantiate Copper Class

    `Args:`
        user_email:
            The email of the API user for Copper. Not required if ``COPPER_USER_EMAIL``
            env variable set.
        api_key:
            The Copper provided application key. Not required if ``COPPER_API_KEY``
            env. variable set.
    `Returns:`
        Copper Class
    """

    def __init__(self, user_email=None, api_key=None):

        self.api_key = check_env.check("COPPER_API_KEY", api_key)
        self.user_email = check_env.check("COPPER_USER_EMAIL", user_email)
        self.uri = COPPER_URI

    def base_request(self, endpoint, req_type, page=1, page_size=200, filters=None):
        # Internal Request Method

        url = self.uri + endpoint

        # Authentication must be done through headers, requests HTTPBasicAuth doesn't work
        headers = {
            "X-PW-AccessToken": self.api_key,
            "X-PW-Application": "developer_api",
            "X-PW-UserEmail": self.user_email,
            "Content-Type": "application/json",
        }

        payload = {}
        if filters is not None:
            if len(filters) > 0 and isinstance(filters, dict):
                payload.update(filters)

        # GET request with non-None data arg is malformed
        if req_type == "GET":
            return request(req_type, url, params=json.dumps(payload), headers=headers)
        else:
            payload["page_number"] = page
            payload["page_size"] = page_size

            return request(req_type, url, data=json.dumps(payload), headers=headers)

    def paginate_request(self, endpoint, req_type, page_size=200, filters=None):
        # Internal pagination method

        page = 1
        total_pages = 2
        blob = []
        only_page = False

        if isinstance(filters, dict):
            # Assume user wants just that page if page_number specified in filters
            if "page_number" in filters:
                page = filters["page_number"]
                # Ensure exactly one loop
                total_pages = page
                rows = f"{str(page_size)} or less"
                only_page = True
        else:
            filters = {}

        while page <= total_pages:

            r = self.base_request(
                endpoint, req_type, page_size=page_size, page=page, filters=filters
            )

            if page == 1:
                if "X-Pw-Total" in r.headers and not only_page:
                    rows = r.headers["X-Pw-Total"]
                    total_pages = int(math.ceil(int(rows) / float(page_size)))
                else:
                    rows = f"{str(page_size)} or less"
                    total_pages = 1
            logger.info(f"Retrieving page {page} of {total_pages}, total rows: {rows}")
            page += 1

            if r.text == "":
                return []
            # Avoid too many layers of nesting if possible
            if isinstance(json.loads(r.text), list):
                blob.extend(json.loads(r.text))
            else:
                blob.append(json.loads(r.text))
            # Wait for 1 second to avoid hitting rate limits
            time.sleep(1)

        return blob

    def get_people(self, filters=None, tidy=False):
        """
        Get people

        `Args:`
            `filters: dict`
                Optional; pass additional parameters to filter the records returned.
                See `Copper documentation <https://developer.copper.com/?version=latest#9c15869b-c894-4fa2-9346-d65a6602c129>`_ for choices
            `tidy: boolean or int`
                Optional; unpack list and dict columns as additional rows instead of columns
                If `True`: creates new table out of unpacked rows
                If 'int': adds rows to original table if max rows per key <= given number
                (so `tidy=0` guarantees new table)

        `Returns:`
            List of dicts of Parsons Tables:
                * people
                * people_emails
                * people_phone_numbers
                * people_custom_fields
                * people_socials
                * people_websites
        """  # noqa: E501,E261

        return self.get_standard_object("people", filters=filters, tidy=tidy)

    def get_companies(self, filters=None, tidy=False):
        """
        Get companies

        `Args:`
            `filters: dict`
                Optional; pass additional parameters to filter the records returned.
                See `Copper documentation <https://developer.copper.com/?version=latest#0b4f267f-3180-4041-861c-13f3cf17bcf9>`_ for choices
            `tidy: boolean or int`
                Optional; unpack list and dict columns as additional rows instead of columns
                If `True`: creates new table out of unpacked rows
                If 'int': adds rows to original table if max rows per key <= given number
                (so `tidy=0` guarantees new table)

        `Returns:`
            List of dicts of Parsons Tables:
                * companies
                * companies_phone_numbers
                * companies_custom_fields
                * companies_socials
                * companies_websites
        """  # noqa: E501,E261

        return self.get_standard_object("companies", filters=filters, tidy=tidy)

    def get_activities(self, filters=None, tidy=False):
        """
        Get activities

        `Args:`
            `filters: dict`
                Optional; pass additional parameters to filter the records returned.
                See `Copper documentation <https://developer.copper.com/?version=latest#d2e6ddd8-6699-4ff3-87e3-1febb0410dc9>`_ for choices
                Optional; unpack list and dict columns as additional rows instead of columns
                If `True`: creates new table out of unpacked rows
                If 'int': adds rows to original table if max rows per key <= given number
                (so `tidy=0` guarantees new table)

        `Returns:`
            List of dicts of Parsons Tables:
                * activities
        """  # noqa: E501,E261

        return self.get_standard_object("activities", filters=filters, tidy=tidy)

    def get_opportunities(self, filters=None, tidy=False):
        """
        Get opportunities (i.e. donations)

        `Args:`
            `filters: dict`
                Optional; pass additional parameters to filter the records returned.
                See `Copper documentation <https://developer.copper.com/?version=latest#5bb8adc1-137f-46bf-aa86-7df037840e57>`_ for choices
                Optional; unpack list and dict columns as additional rows instead of columns
                If `True`: creates new table out of unpacked rows
                If 'int': adds rows to original table if max rows per key <= given number
                (so `tidy=0` guarantees new table)

        `Returns:`
            List of dicts of Parsons Tables:
                * opportunities
                * opportunities_custom_fields
        """  # noqa: E501,E261

        return self.get_standard_object("opportunities", filters=filters, tidy=tidy)

    def get_standard_object(self, object_name, filters=None, tidy=False):
        # Retrieve and process a standard endpoint object (e.g. people, companies, etc.)

        logger.info(f"Retrieving {object_name} records.")
        blob = self.paginate_request(f"/{object_name}/search", req_type="POST", filters=filters)

        return self.process_json(blob, object_name, tidy=tidy)

    def get_custom_fields(self):
        """
        Get custom fields

        `Args:`
            `filters: dict`
            Optional; pass additional parameters to filter the records returned.
            See `Copper documentation <https://developer.copper.com/?version=latest#bf389290-0c19-46a7-85bf-f5e6884fa4e1>`_ for choices

        `Returns:`
            List of dicts of Parsons Tables:
                * custom_fields
                * custom_fields_available
                * custom_fields_options
        """  # noqa: E501,E261

        logger.info("Retrieving custom fields.")
        blob = self.paginate_request("/custom_field_definitions/", req_type="GET")
        return self.process_custom_fields(blob)

    def get_activity_types(self):
        """
        Get activity types

        `Args:`
            `filters: dict`
            Optional; pass additional parameters to filter the records returned.
            See `Copper documentation <https://developer.copper.com/?version=latest#6bd339f1-f0de-48b4-8c34-5a5e245e036f>`_ for choices

        `Returns:`
            List of dicts of Parsons Tables:
                * activitiy_types
        """  # noqa: E501,E261

        logger.info("Retrieving activity types.")

        response = self.paginate_request("/activity_types/", req_type="GET")
        orig_table = Table(response)
        at_user = orig_table.long_table([], "user", prepend=False)
        at_sys = orig_table.long_table([], "system", prepend=False)
        Table.concat(at_sys, at_user)

        return [{"name": "activity_types", "tbl": at_sys}]

    def get_contact_types(self):
        """
        Get contact types

        `Args:`
            `filters: dict`
            Optional; pass additional parameters to filter the records returned.
            See `Copper documentation <https://developer.copper.com/?version=latest#8b6e6ed8-c594-4eed-a2af-586aa2100f09>`_ for choices

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """  # noqa: E501,E261

        response = self.paginate_request("/contact_types/", req_type="GET")
        return Table(response)

    def process_json(self, json_blob, obj_type, tidy=False):
        # Internal method for converting most types of json responses into a list of Parsons tables

        # Output goes here
        table_list = []

        # Original table & columns
        obj_table = Table(json_blob)
        cols = obj_table.get_columns_type_stats()
        list_cols = [x["name"] for x in cols if "list" in x["type"]]
        dict_cols = [x["name"] for x in cols if "dict" in x["type"]]

        # Unpack all list columns
        if len(list_cols) > 0:
            for l in list_cols:  # noqa E741
                # Check for nested data
                list_rows = obj_table.select_rows(
                    lambda row: isinstance(row[l], list)
                    and any(isinstance(x, dict) for x in row[l])
                )
                # Add separate long table for each column with nested data
                if list_rows.num_rows > 0:
                    logger.debug(l, "is a nested column")
                    if len([x for x in cols if x["name"] == l]) == 1:
                        table_list.append(
                            {
                                "name": f"{obj_type}_{l}",
                                "tbl": obj_table.long_table(["id"], l),
                            }
                        )
                    else:
                        # Ignore if column doesn't exist (or has multiples)
                        continue
                else:
                    if tidy is False:
                        logger.debug(l, "is a normal list column")
                        obj_table.unpack_list(l)

        # Unpack all dict columns
        if len(dict_cols) > 0 and tidy is False:
            for d in dict_cols:
                logger.debug(d, "is a dict column")
                obj_table.unpack_dict(d)

        if tidy is not False:
            packed_cols = list_cols + dict_cols
            for p in packed_cols:
                if p in obj_table.columns:
                    logger.debug(p, "needs to be unpacked into rows")

                    # Determine whether or not to expand based on tidy
                    unpacked_tidy = obj_table.unpack_nested_columns_as_rows(p, expand_original=tidy)
                    # Check if column was removed as sign it was unpacked into separate table
                    if p not in obj_table.columns:
                        table_list.append({"name": f"{obj_type}_{p}", "tbl": unpacked_tidy})
                    else:
                        obj_table = unpacked_tidy

        # Original table will have had all nested columns removed
        if len(obj_table.columns) > 1:
            table_list.append({"name": obj_type, "tbl": obj_table})

        return table_list

    def process_custom_fields(self, json_blob):
        # Internal method to convert custom fields responses into a list of Parsons tables

        # Original table & columns
        custom_fields = Table(json_blob)

        # Available On
        available_on = custom_fields.long_table(["id"], "available_on")

        # Options
        options = custom_fields.long_table(["id", "name"], "options")

        return [
            {"name": "custom_fields", "tbl": custom_fields},
            {"name": "custom_fields_available", "tbl": available_on},
            {"name": "custom_fields_options", "tbl": options},
        ]
