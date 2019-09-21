"""NGPVAN Activist Code Endpoints"""

import logging
logger = logging.getLogger(__name__)


class ActivistCodes(object):
    """
        .. note::
            To apply or remove activist codes, use the :meth:`toggle_activist_code` method.
    """

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_activist_codes(self):
        """
        Get activist code objects

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'activistCodes'

        logger.info(f'Getting activist codes...')
        acs = self.connection.request_paginate(url)
        logger.debug(acs)
        logger.info(f'Found {acs.num_rows} activist codes.')

        return acs

    def get_activist_code(self, activist_code_id):
        """Get an activist code

        `Args:`
            activist_code_id : int
                The activist code id associated with the activist code.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'activistCodes/{}'.format(activist_code_id)

        logger.info(f'Getting activist code {activist_code_id}...')
        ac = self.connection.request(url)
        logger.debug(ac)
        logger.info(f'Found activist code {activist_code_id}.')
        return ac
