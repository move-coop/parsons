"""NGPVAN Code Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class Codes(object):
    def __init__(self, van_connection):

        self.connection = van_connection

    def get_codes(self, name=None, supported_entities=None, parent_code_id=None, code_type=None):
        """
        Get codes.

        `Args:`
            name : str
                Filter by name of code.
            supported_entities: str
                Filter by supported entities.
            parent_code_id: str
                Filter by parent code id.
            code_type: str
                Filter by code type.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
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

        `Args:`
            code_id : int
                The code id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        c = self.connection.get_request(f"codes/{code_id}")
        logger.debug(c)
        logger.info(f"Found code {code_id}.")
        return c

    def get_code_types(self):
        """
        Get code types.

        `Returns:`
            list
                A list of code types.
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

        `Args:`
            name: str
                The name of the code.
            parent_code_id: int
                A unique identifier for this code’s parent.
            description: str
                A description for this code, no longer than 200 characters.
            code_type: str
                The code type. ``Tag`` and ``SourceCode`` are valid values.
            supported_entities: list
                A list of dicts that enumerate the searchability and applicability rules of the
                code. You can find supported entities with the :meth:`code_supported_entities`

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
                    ]
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

        `Args:`
            code_id: int
                The code id.
            name: str
                The name of the code.
            parent_code_id: int
                A unique identifier for this code’s parent.
            description: str
                A description for this code, no longer than 200 characters.
            code_type: str
                The code type. ``Tag`` and ``SourceCode`` are valid values.
            supported_entities: list
                A list of dicts that enumerate the searchability and applicability rules of the
                code. You can find supported entities with the :meth:`code_supported_entities`

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
                    ]
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

        `Args:`
            code_id: int
                The code id.
        `Returns:`
            ``None``
        """

        r = self.connection.delete_request(f"codes/{code_id}")
        logger.info(f"Code {code_id} deleted.")
        return r

    def get_code_supported_entities(self):
        """
        Get code supported entities.

        `Returns:`
            list
                A list of code supported entities.
        """

        lst = self.connection.get_request("codes/supportedEntities")
        logger.info(f"Found {len(lst)} code supported entities.")
        return lst
