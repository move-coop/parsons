from simple_salesforce import Salesforce as _Salesforce
from parsons.utilities import check_env
import logging
import json

logger = logging.getLogger(__name__)


class Salesforce:
    """
    Instantiate the Salesforce class

    `Args:`
        username: str
            The Salesforce username (usually an email address). Not required if
            ``SALESFORCE_USERNAME`` env variable is passed.
        password: str
            The Salesforce password. Not required if ``SALESFORCE_PASSWORD`` env variable is
            passed.
        security_token: str
            The Salesforce security token that can be acquired or reset in
            Settings > My Personal Information > Reset My Security Token.
            Not required if ``SALESFORCE_SECURITY_TOKEN`` env variable is passed.
        test_environment: bool
            If ``True`` the client will connect to a Salesforce sandbox instance. Not required if
            ``SALESFORCE_DOMAIN`` env variable is passed.
    `Returns:`
        Salesforce class
    """

    def __init__(self, username=None, password=None, security_token=None, test_environment=False):

        self.username = check_env.check("SALESFORCE_USERNAME", username)
        self.password = check_env.check("SALESFORCE_PASSWORD", password)
        self.security_token = check_env.check("SALESFORCE_SECURITY_TOKEN", security_token)

        if test_environment:
            self.domain = check_env.check("SALESFORCE_DOMAIN", "test")
        else:
            self.domain = None

        self._client = None

    def describe_object(self, object):
        """
        `Args:`
            object: str
                The API name of the type of record to describe. Note that custom object names end
                in `__c`
        `Returns:`
            Ordered Dict of all the object's meta data in Salesforce
        """

        return getattr(self.client, object).describe()

    def describe_fields(self, object):
        """
        `Args:`
            object: str
                The API name of the type of record on whose fields you want data. Note that custom
                object names end in `__c`
        `Returns:`
            Dict of all the object's field meta data in Salesforce
        """

        return json.loads(json.dumps(getattr(self.client, object).describe()["fields"]))

    def query(self, soql):
        """
        `Args:`
            soql: str
                The desired query in Salesforce SOQL language (SQL with additional limitations).
                For reference, see the `Salesforce SOQL documentation <https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm>`_.
        `Returns:`
            list of dicts with Salesforce data
        """  # noqa: E501,E261

        q = self.client.query_all(soql)
        q = json.loads(json.dumps(q))
        logger.info(f"Found {q['totalSize']} results")
        return q

    def insert_record(self, object, data_table):
        """
        Insert new records of the desired object into Salesforce

        `Args:`
            object: str
                The API name of the type of record to insert. Note that custom object names end
                in `__c`
            data_table: obj
                A Parsons Table with data for inserting records. Column names must match object
                field API names, though case and order need not match. Note that custom field
                names end in `__c`.
        `Returns:`
            list of dicts that have the following data:
            * success: boolean
            * created: boolean (if new record is created)
            * id: str (id of record created, if successful)
            * errors: list of dicts (with error details)
        """

        r = getattr(self.client.bulk, object).insert(data_table.to_dicts())
        s = [x for x in r if x.get("success") is True]
        logger.info(
            f"Successfully inserted {len(s)} out of {data_table.num_rows} records to {object}"
        )
        return r

    def update_record(self, object, data_table):
        """
        Update existing records of the desired object in Salesforce

        `Args:`
            object: str
                The API name of the type of record to update. Note that custom object names end
                in `__c`
            data_table: obj
                A Parsons Table with data for updating records. Must contain one column named
                `id`. Column names must match object field API names, though case and order need
                not match. Note that custom field names end in `__c`.
            `Returns:`
                list of dicts that have the following data:
                * success: boolean
                * created: boolean (if new record is created)
                * id: str (id of record altered, if successful)
                * errors: list of dicts (with error details)
        """

        r = getattr(self.client.bulk, object).update(data_table.to_dicts())
        s = [x for x in r if x.get("success") is True]
        logger.info(
            f"Successfully updated {len(s)} out of {data_table.num_rows} records in {object}"
        )
        return r

    def upsert_record(self, object, data_table, id_col):
        """
        Insert new records and update existing ones of the desired object in Salesforce

        `Args:`
            object: str
                The API name of the type of record to upsert. Note that custom object names end
                in `__c`
            data_table: obj
                A Parsons Table with data for upserting records. Column names must match object
                field API names, though case and order need not match. Note that custom field
                names end in `__c`.
            id_col: str
                The column name in `data_table` that stores the record ID. Required even if all
                records are new/inserted.
            `Returns:`
                list of dicts that have the following data:
                * success: boolean
                * created: boolean (if new record is created)
                * id: str (id of record created or altered, if successful)
                * errors: list of dicts (with error details)
        """

        r = getattr(self.client.bulk, object).upsert(data_table.to_dicts(), id_col)
        s = [x for x in r if x.get("success") is True]
        logger.info(
            f"Successfully upserted {len(s)} out of {data_table.num_rows} records to {object}"
        )
        return r

    def delete_record(self, object, id_table, hard_delete=False):
        """
        Delete existing records of the desired object in Salesforce

        `Args:`
            object: str
                The API name of the type of record to delete. Note that custom object names end
                in `__c`
            id_table: obj
                A Parsons Table of record IDs to delete. Note that 'Id' is the default Salesforce
                record ID field name.
            hard_delete: boolean
                If true, will permanently delete record instead of moving it to trash
            `Returns:`
                list of dicts that have the following data:
                * success: boolean
                * created: boolean (if new record is created)
                * id: str (id of record deleted, if successful)
                * errors: list of dicts (with error details)
        """

        if hard_delete:
            r = getattr(self.client.bulk, object).hard_delete(id_table.to_dicts())
        else:
            r = getattr(self.client.bulk, object).delete(id_table.to_dicts())

        s = [x for x in r if x.get("success") is True]
        logger.info(
            f"Successfully deleted {len(s)} out of {id_table.num_rows} records from {object}"
        )
        return r

    @property
    def client(self):
        """
        Get the Salesforce client to use for making all calls. For more information, check the
        `Simple Salesforce Documentation <https://simple-salesforce.readthedocs.io/en/latest/>`_

        `Returns:`
            `simple-salesforce Salesforce object`
        """
        if not self._client:
            # Create a Salesforce client to use to make bulk calls
            self._client = _Salesforce(
                username=self.username,
                password=self.password,
                security_token=self.security_token,
                domain=self.domain,
            )

        return self._client
