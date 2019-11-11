from simple_salesforce import Salesforce
from parsons.utilities import check_env
from parsons import Table
import logging

logger = logging.getLogger(__name__)

class Salesforce:
	"""
	`Args:`
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
	`Returns:`
		Salesforce class
	"""

	def __init__(self, username=None, password=None, security_token=None, domain=None):

		self.username = check_env.check('SALESFORCE_USERNAME', username)
		self.password = check_env.check('SALESFORCE_PASSWORD', password)
		self.security_token = check_env.check('SALESFORCE_SECURITY_TOKEN', security_token)
		self.domain = check_env.check('SALESFORCE_DOMAIN', domain)

		self.client = Salesforce(
		    username=self.username,
		    password=self.password,
		    security_token=self.security_token,
		    domain=self.domain
		)

	def query(self, soql):
		"""
		`Args:`
			soql: str
				The desired query in Salesforce SOQL language (SQL with additional limitations).
				For reference, see `Salesforce SOQL documentation<https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm>`_.
		`Returns:`
			list of dicts with Salesforce data
		"""

		return self.client.query_all(soql)

	def insert(self, object, data_table):
		"""
		Insert new records of the desired object into Salesforce

		`Args:`
			object: str
				The API name of the type of records to insert.
				Note that custom object names end in `__c`
			data_table: Parsons Table
				Data for records inserted. Column names must match object field API names, though
				case need not match. Note that custom field names end in `__c`.
		`Returns:`
			list of dicts that have the following data:
			* success: boolean
			* created: boolean (if new record is created)
			* id: str (id of record created, if successful)
			* errors: list of dicts (with error details)
		"""

		dicts = [row for row in data_table]
		return getattr(self.client.bulk, object).insert(dicts, id_col)

	def update(self, object, data_table, id_col):
		"""
		Update existing records of the desired object in Salesforce

		`Args:`
			object: str
				The API name of the type of records to update.
				Note that custom object names end in `__c`
			data_table: Parsons Table
				Data for updating records. Column names must match object field API names, though
				case need not match. Note that custom field names end in `__c`.
			id_col: str
				The column name in `data_table` that stores the record ID.
			`Returns:`
				list of dicts that have the following data:
				* success: boolean
				* created: boolean (if new record is created)
				* id: str (id of record altered, if successful)
				* errors: list of dicts (with error details)
		"""

		dicts = [row for row in data_table]
		return getattr(self.client.bulk, object).update(dicts, id_col)

	def upsert(self, object, data_table, id_col):
		"""
		Insert new records and update existing ones of the desired object in Salesforce

		`Args:`
			object: str
				The API name of the type of records to upsert.
				Note that custom object names end in `__c`
			data_table: Parsons Table
				Data for upserting records. Column names must match object field API names, though
				case need not match. Note that custom field names end in `__c`.
			id_col: str
				The column name in `data_table` that stores the record ID.
				Required even if all records are new/inserted.
			`Returns:`
				list of dicts that have the following data:
				* success: boolean
				* created: boolean (if new record is created)
				* id: str (id of record created or altered, if successful)
				* errors: list of dicts (with error details)
		"""

		dicts = [row for row in data_table]
		return getattr(self.client.bulk, object).upsert(dicts, id_col)

	def delete(self, object, id_table, hard_delete=False):
		"""
		Delete existing records of the desired object in Salesforce

		`Args:`
			object: str
				The API name of the type of records to delete.
				Note that custom object names end in `__c`
			id_table: Parsons Table
				The table of record IDs to delete.
				Note that 'Id' is the default Salesforce record ID field name.
			hard_delete: boolean
				If true, will permanently delete record instead of moving it to trash
			`Returns:`
				list of dicts that have the following data:
				* success: boolean
				* created: boolean (if new record is created)
				* id: str (id of record deleted, if successful)
				* errors: list of dicts (with error details)
		"""

		dicts = [row for row in data_table]
		if hard_delete is True:
			return getattr(self.client.bulk, object).hard_delete(dicts, id_col)
		else:
			return getattr(self.client.bulk, object).delete(dicts, id_col)
