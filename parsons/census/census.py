import logging
from parsons.utilities.api_connector import APIConnector
from parsons.utilities import check_env
from parsons import Table

logger = logging.getLogger(__name__)

class Census(object):
	"""
	Class that creates a connector to the Census Bureau API
	"""

	def __init__(self, api_key=None):
		"""
        Instantiate Census class.

           `Args:
           		api_key: string, key for Census API access (optional, can also be pulled from
           		environment variable CENSUS_API_KEY)
    	"""
		self.api_key = check_env.check("CENSUS_API_KEY", api_key)
		self.host = 'https://api.census.gov/data'


	def get_census(self,year=None,dataset_acronym=None,variables=None,location=None):
		"""
				Pull census data using parsons APIConnector
				Args:
					year: 4-digit string or integer e.g. '2019' or 2019
					dataset_acronym: string with dataset name, e.g. '/acs/acs1'
					variables: comma-separated string with variable names, e.g. 'NAME,B01001_001E'
					location: string with ampersand and desired locations, e.g. 'for=us:*'
				Return:
					Parsons table with data
		"""
		#set up the URL
		g = '?get='
		usr_key = f"&key={self.api_key}"
		year = str(year) # in case someone passes int
		location = "&for="+location
		query_url = f"{self.host}/{year}{dataset_acronym}{g}{variables}{location}{usr_key}"

		connector = APIConnector(uri=self.host)

		response = connector.get_request(url=query_url)

		return Table(response)



