from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Any, Literal

import simple_salesforce

from parsons.utilities import check_env

if TYPE_CHECKING:
    from collections import OrderedDict

    from parsons import Table


logger = logging.getLogger(__name__)


class Salesforce:
    """
    Instantiate the Salesforce class

    Supports the password and
    `client_credentials <https://help.salesforce.com/s/articleView?language=en_US&id=xcloud.connected_app_client_credentials_setup.htm&type=5>`__
    authentication methods.

    Args:
        username:
            The Salesforce username (usually an email address).
            Not required if ``SALESFORCE_USERNAME`` env variable is passed.
            Used in the 'password' auth method.
        password:
            The Salesforce password.
            Not required if ``SALESFORCE_PASSWORD`` env variable is passed.
            Used in the 'password' auth method.
        security_token:
            The Salesforce security token that can be acquired or reset in
            Settings > My Personal Information > Reset My Security Token.
            Not required if ``SALESFORCE_SECURITY_TOKEN`` env variable is passed.
            Used in the 'password' auth method.
        test_environment:
            If ``True`` the client will connect to a Salesforce sandbox instance.
            Not required if ``SALESFORCE_DOMAIN`` env variable is passed.
        consumer_key:
            consumer key for a connected app.
            Used in the 'client_credentials' auth method.
        consumer_secret:
            consumer secret for a connected app.
            Used in the 'client_credentials' auth method.
        domain:
            url for the salesforce instance.
            Used in the 'client_credentials' auth method.
        authentication_method:
            The method to use for authentication.
            Defaults to ``password``.
            Not required if ``SALESFORCE_AUTHENTICATION_METHOD`` env variable is passed.

    """

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        security_token: str | None = None,
        test_environment: bool = False,
        consumer_key: str | None = None,
        consumer_secret: str | None = None,
        domain: str | None = None,
        authentication_method: Literal["password", "client_credentials"] | None = None,
    ):
        if authentication_method:
            self.authentication_method = authentication_method
        elif env_authentication_method := os.environ.get("SALESFORCE_AUTHENTICATION_METHOD"):
            self.authentication_method: str = env_authentication_method
        else:
            self.authentication_method = "password"

        if self.authentication_method == "password":
            self.username: str = check_env.check("SALESFORCE_USERNAME", username)
            self.password: str = check_env.check("SALESFORCE_PASSWORD", password)
            self.security_token: str = check_env.check("SALESFORCE_SECURITY_TOKEN", security_token)
            if test_environment:
                self.domain = check_env.check("SALESFORCE_DOMAIN", "test")
            else:
                self.domain = None

        elif self.authentication_method == "client_credentials":
            self.consumer_key: str = check_env.check("SALESFORCE_CONSUMER_KEY", consumer_key)
            self.consumer_secret: str = check_env.check(
                "SALESFORCE_CONSUMER_SECRET", consumer_secret
            )
            self.domain = check_env.check("SALESFORCE_DOMAIN", domain)

        else:
            raise NotImplementedError(
                f"{self.authentication_method} is not a supported method. Parsons currently supports 'password' and 'client_credentials'"
            )

        self._client = None

    def describe_object(self, object: str) -> OrderedDict:
        """
        Args:
            object:
                The API name of the type of record to describe.
                Note that custom object names end in ``__c``.

        Returns:
            All the object's metadata in Salesforce

        """
        return getattr(self.client, object).describe()

    def describe_fields(self, object: str) -> dict[str, Any]:
        """
        Args:
            object:
                The API name of the type of record on whose fields you want data.
                Note that custom object names end in ``__c``.

        Returns:
            Dict of all the object's field meta data in Salesforce

        """
        return json.loads(json.dumps(getattr(self.client, object).describe()["fields"]))

    def query(self, soql: str) -> list[dict[str, Any]]:
        """
        Args:
            soql: str
                The desired query in Salesforce SOQL language (SQL with additional limitations).
                For reference, see the `Salesforce SOQL Documentation`_.

        Returns:
            Salesforce data

        """
        q = self.client.query_all(soql)
        q = json.loads(json.dumps(q))
        logger.info(f"Found {q['totalSize']} results")
        return q

    def insert_record(
        self, object: str, data_table: Table
    ) -> list[dict[str, bool | str | list[dict]]]:
        """
        Insert new records of the desired object into Salesforce

        Args:
            object:
                The API name of the type of record to insert.
                Note that custom object names end in ``__c``.
            data_table:
                A Parsons Table with data for inserting records.
                Column names must match object field API names,
                though case and order need not match.
                Note that custom field names end in ``__c``.

        Returns:
            * success: bool
            * created: bool (if new record is created)
            * id: str (id of record created, if successful)
            * errors: list of dicts (with error details)

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
        Update existing records of the desired object in Salesforce

        Args:
            object:
                The API name of the type of record to update.
                Note that custom object names end in ``__c``.
            data_table:
                A Parsons Table with data for updating records.
                Must contain one column named `id`.
                Column names must match object field API names,
                though case and order need not match.
                Note that custom field names end in ``__c``.

        Returns:
            * success: bool
            * created: bool (if new record is created)
            * id: str (id of record altered, if successful)
            * errors: list of dicts (with error details)

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
        Insert new records and update existing ones of the desired object in Salesforce

        Args:
            object:
                The API name of the type of record to upsert.
                Note that custom object names end in ``__c``.
            data_table:
                A Parsons Table with data for upserting records.
                Column names must match object field API names,
                though case and order need not match.
                Note that custom field names end in ``__c``.
            id_col:
                The column name in `data_table` that stores the record ID.
                Required even if all records are new/inserted.

        Returns:
            * success: bool
            * created: bool (if new record is created)
            * id: str (id of record created or altered, if successful)
            * errors: list of dicts (with error details)

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
        Delete existing records of the desired object in Salesforce

        Args:
            object:
                The API name of the type of record to delete.
                Note that custom object names end in ``__c``.
            id_table:
                Parsons Table of record IDs to delete.
                Note that ``Id`` is the default Salesforce record ID field name.
            hard_delete:
                If ``True``, will permanently delete record instead of moving it to trash.

        Returns:
            Each list has the following data.
            * success: bool
            * created: bool (if new record is created)
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
    def client(self) -> simple_salesforce.api.Salesforce:
        """
        Get the Salesforce client to use for making all calls.

        For more information, check the
        `Simple Salesforce Documentation <https://simple-salesforce.readthedocs.io/en/latest/>`__

        """
        if not self._client:
            # Create a Salesforce client to use to make bulk calls
            if self.authentication_method == "password":
                self._client = simple_salesforce.api.Salesforce(
                    username=self.username,
                    password=self.password,
                    security_token=self.security_token,
                    domain=self.domain,
                )
            elif self.authentication_method == "client_credentials":
                self._client = simple_salesforce.api.Salesforce(
                    consumer_key=self.consumer_key,
                    consumer_secret=self.consumer_secret,
                    domain=self.domain,
                )
            else:
                raise Exception("Should not be possible to reach this code")

        return self._client
