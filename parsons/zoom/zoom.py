from parsons.utilities import check_env

ZOOM_URI = 'https://api.zoom.us/v2/'


class Zoom():

    def __init__(self, token=None):

        self.token = check_env.check('ZOOM_TOKEN', token)

        self.headers = {'authorization': f"Bearer {self.zoom_token}",
                        'content-type': "application/json"}

        self.client = APIConnector(ZOOM_URI, header=self.headers)

    def get_webinars(self):
        """
        Get webinars.

        `Args:`
            arg1: str
        `Returns`:
            A parsons table
        """

        # To Do:
        # Add in the arguments to pass as params.
        # Figure out pagination, if it exists
        # Figure out the endpoint url for 'webinars'

        return Table(self.client.get('webinars', params=params))
