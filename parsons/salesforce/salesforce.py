from simple_salesforce import Salesforce
from parsons.utilities import check_env
from parsons import Table
import logging

logger = logging.getLogger(__name__)

class Salesforce:
	"""
	Args:
		username: str
			The Salesforce username (usually an email address).
			Not required if ``SALESFORCE_USERNAME`` env variable is passed.
		password: str
			The Salesforce password.
			Not required if ``SALESFORCE_PASSWORD`` env variable is passed.
		security_token: str
			The Salesforce security token that can be acquired or reset in
			Settings > My Personal Information > Reset My Security Token.
			Not required if ``SALESFORCE_SECURITY_TOKEN`` env variable is passed.
		domain: str
			If the Saleforce instance is a sandbox, set to `'test'`. Otherwise, not required.
			Can also be passed through ``SALESFORCE_DOMAIN`` env variable.
	"""

	def __init__(self, username=None, password=None, security_token=None, domain=None):

		self.username = check_env.check('SALESFORCE_USERNAME', username)
		self.password = check_env.check('SALESFORCE_PASSWORD', password)
		self.security_token = check_env.check('SALESFORCE_SECURITY_TOKEN', security_token)
		self.domain = check_env.check('SALESFORCE_DOMAIN', domain)