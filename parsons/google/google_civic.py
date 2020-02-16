from parsons.utilities import check_env
import requests
from parsons.etl import Table

URI = 'https://www.googleapis.com/civicinfo/v2/'


class GoogleCivic(object):
    """
    `Args:`
        api_key : str
            A valid Google api key. Not required if ``GOOGLE_CIVIC_API_KEY``
            env variable set.
    `Returns:`
        class
    """

    def __init__(self, api_key=None):

        self.api_key = check_env.check('GOOGLE_CIVIC_API_KEY', api_key)
        self.uri = URI

    def request(self, url, args=None):
        # Internal request method

        if not args:
            args = {}

        args['key'] = self.api_key

        r = requests.get(url, params=args)

        return r.json()

    def get_elections(self):
        """
        Get a collection of information about elections and voter information.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.uri + 'elections'

        return Table((self.request(url))['elections'])

    def _get_voter_info(self, election_id, address):
        # Internal method to call voter info end point. Portions of this are
        # parsed for other methods.

        url = self.uri + 'voterinfo'

        args = {'address': address, 'electionId': election_id}

        return self.request(url, args=args)

    def get_polling_location(self, election_id, address):
        """
        Get polling location information for a given address.

        `Args:`
            election_id: int
                A valid election id. Election ids can be found by running the
                :meth:`get_elections` method.
            address: str
                A valid US address in a single string.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        r = self._get_voter_info(election_id, address)

        return r['pollingLocations']

    def get_polling_locations(self, election_id, table, address_field='address'):
        """
        Get polling location information for a table of addresses.

        `Args:`
            election_id: int
                A valid election id. Election ids can be found by running the
                :meth:`get_elections` method.
            address: str
                A valid US address in a single string.
            address_field: str
                The name of the column where the address is stored.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        polling_locations = []

        # Iterate through the rows of the table
        for row in table:
            loc = self.get_polling_location(election_id, row[address_field])
            # Insert original passed address
            loc[0]['passed_address'] = row[address_field]

            # Add to list of lists
            polling_locations.append(loc[0])

        # Unpack values
        tbl = Table(polling_locations)
        tbl.unpack_dict('address', prepend_value='polling')
        tbl.unpack_list('sources', replace=True)
        tbl.unpack_dict('sources_0', prepend_value='source')
        tbl.rename_column('polling_line1', 'polling_address')

        # Resort columns
        tbl.move_column('pollingHours', len(tbl.columns))
        tbl.move_column('notes', len(tbl.columns))
        tbl.move_column('polling_locationName', 1)
        tbl.move_column('polling_address', 2)

        return tbl
