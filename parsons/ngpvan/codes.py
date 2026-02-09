"""NGPVAN Code Endpoints"""

import logging

from parsons.etl.table import Table

logger = logging.getLogger(__name__)


class Codes:
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_codes(self, name=None, supported_entities=None, parent_code_id=None, code_type=None):
        """
        Get codes.

        Args:
            name (str, optional): Filter by name of code. Defaults to None.
            supported_entities (str, optional): Filter by supported entities. Defaults to None.
            parent_code_id (str, optional): Filter by parent code id. Defaults to None.
            code_type (str, optional): Filter by code type. Defaults to None.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        params = {
            "name": name,
            "supportedEntities": supported_entities,
            "parentCodeId": parent_code_id,
            "codeType": code_type,
            "$top": 200,
        }

        tbl = Table(self.connection.get_request("codes", params=params))
        logger.info(f"Found {tbl.num_rows} codes.")
        return tbl

    def get_code(self, code_id):
        """
        Get a code.

        Args:
            code_id (int): The code id.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        c = self.connection.get_request(f"codes/{code_id}")
        logger.debug(c)
        logger.info(f"Found code {code_id}.")
        return c

    def get_code_types(self):
        """
        Get code types.

        Returns:
            list: A list of code types.

        """
        lst = self.connection.get_request("codeTypes")
        logger.info(f"Found {len(lst)} code types.")
        return lst

    def create_code(
        self,
        name=None,
        parent_code_id=None,
        description=None,
        code_type="SourceCode",
        supported_entities=None,
    ):
        """
        Create a code.

        Args:
            name (str, optional): The name of the code. Defaults to None.
            parent_code_id (int, optional): A unique identifier for this code's parent. Defaults to None.
            description (str, optional): A description for this code, no longer than 200 characters.
                Defaults to None.
            code_type (str, optional): The code type. ``Tag`` and ``SourceCode`` are valid values.
                Defaults to "SourceCode".
            supported_entities (list, optional): A list of dicts that enumerate the searchability and applicability
                rules of the code. You can find supported entities with the
                :meth:`code_supported_entities`

                .. highlight:: python

                .. code-block:: python

                [
                {
                'name': 'Event',
                'is_searchable': True,
                'is_applicable': True
                }
                {
                'name': 'Locations',
                'start_time': '12-31-2018T13:00:00',
                'end_time': '12-31-2018T14:00:00'
                }
                ]. Defaults to None.

        """
        json = {
            "parentCodeId": parent_code_id,
            "name": name,
            "codeType": code_type,
            "description": description,
        }

        if supported_entities:
            se = [
                {
                    "name": s["name"],
                    "isSearchable": s["is_searchable"],
                    "isApplicable": s["is_applicable"],
                }
                for s in supported_entities
            ]

            json["supportedEntities"] = se

        r = self.connection.post_request("codes", json=json)
        logger.info(f"Code {r} created.")
        return r

    def update_code(
        self,
        code_id,
        name=None,
        parent_code_id=None,
        description=None,
        code_type="SourceCode",
        supported_entities=None,
    ):
        """
        Update a code.

        Args:
            code_id (int): The code id.
            name (str, optional): The name of the code. Defaults to None.
            parent_code_id (int, optional): A unique identifier for this code's parent. Defaults to None.
            description (str, optional): A description for this code, no longer than 200 characters.
                Defaults to None.
            code_type (str, optional): The code type. ``Tag`` and ``SourceCode`` are valid values.
                Defaults to "SourceCode".
            supported_entities (list, optional): A list of dicts that enumerate the searchability and applicability
                rules of the code. You can find supported entities with the
                :meth:`code_supported_entities`

                .. highlight:: python

                .. code-block:: python

                [
                {
                'name': 'Event',
                'is_searchable': True,
                'is_applicable': True
                }
                {
                'name': 'Locations',
                'start_time': '12-31-2018T13:00:00',
                'end_time': '12-31-2018T14:00:00'
                }
                ]. Defaults to None.

        """
        post_data = {}

        if name:
            post_data["name"] = name
        if parent_code_id:
            post_data["parentCodeId"] = parent_code_id
        if code_type:
            post_data["codeType"] = code_type
        if description:
            post_data["description"] = description

        if supported_entities:
            se = [
                {
                    "name": s["name"],
                    "isSearchable": s["is_searchable"],
                    "isApplicable": s["is_applicable"],
                }
                for s in supported_entities
            ]
            post_data["supportedEntities"] = se

        r = self.connection.put_request(f"codes/{code_id}", json=post_data)
        logger.info(f"Code {code_id} updated.")
        return r

    def delete_code(self, code_id):
        """
        Delete a code.

        Args:
            code_id (int): The code id.

        """
        r = self.connection.delete_request(f"codes/{code_id}")
        logger.info(f"Code {code_id} deleted.")
        return r

    def get_code_supported_entities(self):
        """
        Get code supported entities.

        Returns:
            list: A list of code supported entities.

        """
        lst = self.connection.get_request("codes/supportedEntities")
        logger.info(f"Found {len(lst)} code supported entities.")
        return lst
