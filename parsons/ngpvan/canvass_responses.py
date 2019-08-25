import logging

logger = logging.getLogger(__name__)


class CanvassResponses(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_canvass_responses_contact_types(self):
        """
        Get canvass response contact types available to the API user.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'canvassResponses/contactTypes'

        logger.info(f'Getting canvass response contact types...')
        crc = self.connection.request(url)
        logger.debug(crc)
        logger.info(f'Found {crc.num_rows} canvass response contact types.')

        return crc

    def get_canvass_responses_input_types(self):
        """
        Get canvass response input types available to the API user.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'canvassResponses/inputTypes'

        logger.info(f'Getting canvass response input types...')
        cri = self.connection.request(url)
        logger.debug(cri)
        logger.info(f'Found {cri.num_rows} canvass response input types.')

        return cri

    def get_canvass_responses_result_codes(self):
        """
        Get canvass response result code ids available to the API user.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'canvassResponses/resultCodes'

        logger.info(f'Getting canvass response result codes...')
        crr = self.connection.request(url)
        logger.debug(crr)
        logger.info(f'Found {crr.num_rows} canvass response result codes.')

        return crr
