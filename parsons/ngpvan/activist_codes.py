"""NGPVAN Activist Code Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class ActivistCodes(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_activist_codes(self):
        """
        Get activist codes.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request('activistCodes'))
        logger.info(f'Found {tbl.num_rows} activist codes.')
        return tbl

    def get_activist_code(self, activist_code_id):
        """
        Get an activist code.

        `Args:`
            activist_code_id : int
                The activist code id.
        `Returns:`
            dict
                The activist code
        """

        r = self.connection.get_request(f'activistCodes/{activist_code_id}')
        logger.info(f'Found activist code {activist_code_id}.')
        return r

    def toggle_activist_code(self, id, activist_code_id, action, id_type='vanid',
                             result_code_id=None, contact_type_id=None, input_type_id=None,
                             date_canvassed=None):
        """
        Apply or remove an activist code to or from a person.

        `Args:`
            id: str
                A valid person id
            activist_code_id: int
                A valid activist code id
            action: str
                Either 'apply' or 'remove'
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
            result_code_id : int
                `Optional`; Specifies the result code of the response. If
                not included,responses must be specified. Conversely, if
                responses are specified, result_code_id must be null. Valid ids
                can be found by using the :meth:`get_canvass_responses_result_codes`
            contact_type_id : int
                `Optional`; A valid contact type id
            input_type_id : int
                `Optional`; Defaults to 11 (API Input)
            date_canvassed : str
                `Optional`; ISO 8601 formatted date. Defaults to todays date
        Returns:
            Status code 204
        """

        response = {"activistCodeId": activist_code_id,
                    "action": self._action_parse(action),
                    "type": "activistCode"}

        r = self.apply_response(id, response, id_type, result_code_id=result_code_id,
                                contact_type_id=contact_type_id, input_type_id=input_type_id,
                                date_canvassed=date_canvassed)

        logger.info(f'{id_type.upper()} {id} {action.capitalize()} ' +
                    f'activist code {activist_code_id}')

        return r
