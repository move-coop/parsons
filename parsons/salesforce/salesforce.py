import json
import logging
import os

import simple_salesforce
from simple_salesforce import Salesforce as _Salesforce

from parsons import Table
from parsons.utilities import check_env

logger = logging.getLogger(__name__)


class Salesforce:
    """
    Instantiate the Salesforce class

    Supports the password and `client_credentials
    <https://help.salesforce.com/s/articleView?id=xcloud.connected_app_client_credentials_setup.htm&type=5>`_
    authentication methods........

    Args:
        username (str, optional): The Salesforce username (usually an email address). Not required if
            ``SALESFORCE_USERNAME`` env variable is passed. Used in the 'password' auth method.
            Defaults to None.
        password (str, optional): The Salesforce password. Not required if
            ``SALESFORCE_PASSWORD`` env variable is passed. Used in the 'password' auth method.
            Defaults to None.
        security_token (str, optional): The Salesforce security token that can be acquired or reset in Settings > My
            Personal Information > Reset My Security Token. Not required if ``SALESFORCE_SECURITY_TOKEN`` env variable
            is passed. Used in the 'password' auth method. Defaults to None.
        test_environment (bool, optional): If ``True`` the client will connect to a Salesforce sandbox instance.
            Not required if
            ``SALESFORCE_DOMAIN`` env variable is passed. Defaults to False.
        consumer_key (str, optional): Consumer key for a connected app. Used in the 'client_credentials' auth
            method. Defaults to None.
        consumer_secret (str, optional): Consumer secret for a connected app. Used in the 'client_credentials' auth
            method. Defaults to None.
        domain (str, optional): Url for the salesforce instance. Used in the
            'client_credentials' auth method. Defaults to None.
        authentication_method (str, optional): The method to use for authentication. Not required if
            ``SALESFORCE_AUTHENTICATION_METHOD`` env variable is passed. Defaults to None.

    Returns:
        Salesforce

    """

    def __init__(
        self,
        username: str = None,
        password: str = None,
        security_token: str = None,
        test_environment: bool = False,
        consumer_key: str = None,
        consumer_secret: str = None,
        domain: str = None,
        authentication_method: str = None,
    ):
        if authentication_method:
            self.authentication_method = authentication_method
        elif env_authentication_method := os.environ.get("SALESFORCE_AUTHENTICATION_METHOD"):
            self.authentication_method = env_authentication_method
        else:
            self.authentication_method = "password"

        if self.authentication_method == "password":
            self.username = check_env.check("SALESFORCE_USERNAME", username)
            self.password = check_env.check("SALESFORCE_PASSWORD", password)
            self.security_token = check_env.check("SALESFORCE_SECURITY_TOKEN", security_token)
            if test_environment:
                self.domain = check_env.check("SALESFORCE_DOMAIN", "test")
            else:
                self.domain = None

        elif self.authentication_method == "client_credentials":
            self.consumer_key = check_env.check("SALESFORCE_CONSUMER_KEY", consumer_key)
            self.consumer_secret = check_env.check("SALESFORCE_CONSUMER_SECRET", consumer_key)
            self.domain = check_env.check("SALESFORCE_DOMAIN", domain)

        else:
            raise NotImplementedError(
                f"{self.authentication_method} is not a supported method. Parsons currently supports 'password' and 'client_credentials'"
            )

        self._client = None

    def describe_object(self, object: str):
        """
        Describe object.

        Args:
            object (str): The API name of the type of record to describe. Note that custom object names end in
                `__c`.

        Returns:
            Ordered Dict of all the object's meta data in Salesforce

        """
        return getattr(self.client, object).describe()

    def describe_fields(self, object: str) -> dict:
        """
        Describe fields.

        Args:
            object (str): The API name of the type of record on whose fields you want data.
                Note that custom object names end in `__c`.

        Returns:
            dict: Object's field meta data in Salesforce.

        """
        return json.loads(json.dumps(getattr(self.client, object).describe()["fields"]))

    def query(self, soql: str) -> list[dict]:
        """
        Query function.

        Args:
            soql (str): The desired query in Salesforce SOQL language (SQL with additional limitations).
                For reference, see the `Salesforce SOQL documentation
                <https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm>`_.

        Returns:
            list[dict]: Salesforce data.

        """
        q = self.client.query_all(soql)
        q = json.loads(json.dumps(q))
        logger.info(f"Found {q['totalSize']} results")
        return q

    def insert_record(
        self, object: str, data_table: Table
    ) -> list[dict[str, bool | str | list[dict]]]:
        """
        Insert new records of the desired object into Salesforce.

        Args:
            object (str): The API name of the type of record to insert. Note that custom object names end in `__c`.
            data_table (Table): A Parsons Table with data for inserting records. Column names must match object
                field API names, though case and order need not match. Note that custom field names end in `__c`.

        Returns:
            list[dict[str, bool | str | list[dict]]]: Contains the following data:
                * success: bool
                * created: bool (if new record is created)
                * id: str (id of record created, if successful)
                * errors: list of dicts (with error details).

        """
        r = getattr(self.client.bulk, object).insert(data_table.to_dicts())
        s = [x for x in r if x.get("success") is True]
        logger.info(
            f"Successfully inserted {len(s)} out of {data_table.num_rows} records to {object}"
        )
        return r

    def update_record(
        self, object: str, data_table: Table
    ) -> list[dict[str, bool | str | list[dict]]]:
        """
        Update existing records of the desired object in Salesforce.

        Args:
            object (str): The API name of the type of record to update. Note that custom object names end in `__c`.
            data_table (Table): A Parsons Table with data for updating records. Must contain one column named
                `id`. Column names must match object field API names, though case and order need not match.
                Note that custom field names end in `__c`.

        Returns:
            list[dict[str, bool | str | list[dict]]]: Contains the following data:
                * success: bool
                * created: bool (if new record is created)
                * id: str (id of record altered, if successful)
                * errors: list of dicts (with error details).

        """
        r = getattr(self.client.bulk, object).update(data_table.to_dicts())
        s = [x for x in r if x.get("success") is True]
        logger.info(
            f"Successfully updated {len(s)} out of {data_table.num_rows} records in {object}"
        )
        return r

    def upsert_record(
        self, object: str, data_table: Table, id_col: str
    ) -> list[dict[str, bool | str | list[dict]]]:
        """
        Insert new records and update existing ones of the desired object in Salesforce.

        Args:
            object (str): The API name of the type of record to upsert. Note that custom object names end in `__c`.
            data_table (Table): A Parsons Table with data for upserting records. Column names must match object
                field API names, though case and order need not match. Note that custom field names end in `__c`.
            id_col (str): The column name in `data_table` that stores the record ID. Required even if all records
                are new/inserted.

        Returns:
            list[dict[str, bool | str | list[dict]]]: Contains the following data:
                * success: bool
                * created: bool (if new record is created)
                * id: str (id of record created or altered, if successful)
                * errors: list of dicts (with error details).

        """
        r = getattr(self.client.bulk, object).upsert(data_table.to_dicts(), id_col)
        s = [x for x in r if x.get("success") is True]
        logger.info(
            f"Successfully upserted {len(s)} out of {data_table.num_rows} records to {object}"
        )
        return r

    def delete_record(
        self, object: str, id_table: Table, hard_delete: bool = False
    ) -> list[dict[str, bool | str | list[dict]]]:
        """
        Delete existing records of the desired object in Salesforce.

        Args:
            object (str): The API name of the type of record to delete. Note that custom object names end in `__c`.
            id_table (Table): Obj A Parsons Table of record IDs to delete. Note that 'Id' is the default Salesforce
                record ID field name.
            hard_delete (bool, optional): If true, will permanently delete record instead of moving it to trash.
                Defaults to False.

        Returns:
            list[dict[str, bool | str | list[dict]]]: Contains the following data:
                * success: bool
                * created: bool (if new record is created)
                * id: str (id of record deleted, if successful)
                * errors: list of dicts (with error details).

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
    def client(self) -> simple_salesforce.Salesforce:
        """
        Get the Salesforce client to use for making all calls.

        Returns:
            Documentation Reference:
                `Simple Salesforce Documentation
                <https://simple-salesforce.readthedocs.io/en/latest/>`_.

        """
        if not self._client:
            # Create a Salesforce client to use to make bulk calls
            if self.authentication_method == "password":
                self._client = _Salesforce(
                    username=self.username,
                    password=self.password,
                    security_token=self.security_token,
                    domain=self.domain,
                )
            elif self.authentication_method == "client_credentials":
                self._client = _Salesforce(
                    consumer_key=self.consumer_key,
                    consumer_secret=self.consumer_secret,
                    domain=self.domain,
                )
            else:
                raise Exception("Should not be possible to reach this code")

        return self._client
