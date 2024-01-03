import logging
from parsons.utilities.api_connector import APIConnector
from parsons.utilities import check_env
from parsons import Table

logger = logging.getLogger(__name__)

class Census(object):

	"""
        Instantiate Census class.

           `Args:`
        """

	def __init__(self, api_key=None):
		self.api_key = check_env.check('CONNECTOR_API_KEY', api_key)
		self.host = 'https://api.census.gov/data'


	def get_census(self,year=None,dataset_acronym=None,variables=None,location=None):
		"""
				pull census data using parsons APIConnector
				to get key click on request a key here https://www.census.gov/data/developers.html
				some stuff cribbed from https://medium.com/@mcmanus_data_works/using-the-u-s-census-bureau-api-with-python-5c30ad34dbd7
				Args:
					year: string with slash and yearname= '/2019'
					dataset_acronym: string with dataset name, e.g. '/acs/acs1'
					variables: comma-separated string with variable names, e.g. 'NAME,B01001_001E'
					location: string with ampersand and desired locations, e.g. '&for=us:*'
				Return:
					petl table with data
				"""
		import requests

		g = '?get='
		usr_key = f"&key={self.api_key}"
		query_url = f"{self.host}{year}{dataset_acronym}{g}{variables}{location}{usr_key}"

		response = requests.get(query_url)

		return Table(response.json())



