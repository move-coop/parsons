import re
from datetime import datetime, timedelta

from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector


class Shopify:
    """
    Instantiate the Shopify class.

    Args:
        subdomain (str, optional): The Shopify subdomain (e.g. ``myorg`` for myorg.myshopify.com).
            Not required if ``SHOPIFY_SUBDOMAIN`` env variable set. Defaults to None.
        password (str, optional): The Shopify account password. Not required if ``SHOPIFY_PASSWORD`` env variable
            set. Defaults to None.
        api_key (str, optional): The Shopify account API key. Not required if ``SHOPIFY_API_KEY`` env variable set.
            Defaults to None.
        api_version (str, optional): The Shopify API version. Not required if ``SHOPIFY_API_VERSION`` env variable
            set. Defaults to None.
        access_token (str, optional): The Shopify access token. Not required if ``SHOPIFY_ACCESS_TOKEN`` env
            variable set. If argument or env variable is set, password and api_key are ignored.
            Defaults to None.

    Returns:
        Shopify Class

    """

    def __init__(
        self,
        subdomain=None,
        password=None,
        api_key=None,
        api_version=None,
        access_token=None,
    ):
        self.subdomain = check_env.check("SHOPIFY_SUBDOMAIN", subdomain)
        self.access_token = check_env.check("SHOPIFY_ACCESS_TOKEN", access_token, optional=True)
        self.password = check_env.check("SHOPIFY_PASSWORD", password, optional=True)
        self.api_key = check_env.check("SHOPIFY_API_KEY", api_key, optional=True)
        self.api_version = check_env.check("SHOPIFY_API_VERSION", api_version)
        self.base_url = f"https://{self.subdomain}.myshopify.com/admin/api/{self.api_version}/"
        if self.access_token is None and (self.password is None or self.api_key is None):
            raise KeyError("Must set either access_token or both api_key and password.")
        if self.access_token is not None:
            self.client = APIConnector(
                self.base_url, headers={"X-Shopify-Access-Token": access_token}
            )
        else:
            self.client = APIConnector(self.base_url, auth=(self.api_key, self.password))

    def get_count(self, query_date=None, since_id=None, table_name=None):
        """
        Get the count of rows in a table.

        Args:
            query_date (str, optional): Filter query by a date that rows were created. This filter is ignored if
                value is None. Defaults to None.
            since_id (str, optional): Filter query by a minimum ID. This filter is ignored if value is None.
                Defaults to None.
            table_name (str, optional): The name of the Shopify table to query. Defaults to None.

        Returns:
            int

        """
        return (
            self.client.request(self.get_query_url(query_date, since_id, table_name), "GET")
            .json()
            .get("count", 0)
        )

    def get_orders(self, query_date=None, since_id=None, completed=True):
        """
        Get Shopify orders.

        Args:
            query_date (str, optional): Filter query by a date that rows were created. Format: yyyy-mm-dd.
                This filter is ignored if value is None. Defaults to None.
            since_id (str, optional): Filter query by a minimum ID. This filter is ignored if value is None.
                Defaults to None.
            completed (bool, optional): True if only getting completed orders, False otherwise.
                Defaults to True.

        Returns:
            Table

        """
        orders = []

        def _append_orders(url):
            nonlocal orders

            if completed:
                url += "&financial_status=paid"

            res = self.client.request(url, "GET")

            cur_orders = res.json().get("orders", [])

            # Flatten orders to non-complex types
            for order in cur_orders:
                keys_to_add = {}
                keys_to_delete = []

                for key1 in order:
                    if isinstance(order[key1], dict):
                        for key2 in order[key1]:
                            keys_to_add[key1 + "_" + key2] = order[key1][key2]
                        keys_to_delete.append(key1)
                    elif key1 == "note_attributes":
                        for note in order[key1]:
                            keys_to_add[key1 + "_" + note["name"]] = note["value"]

                order.update(keys_to_add)
                for key in keys_to_delete:
                    del order[key]

            orders += cur_orders

            return res

        res = _append_orders(self.get_query_url(query_date, since_id, "orders", False))

        # Get next page
        while res.headers.get("Link"):
            link = re.split("; |, ", res.headers.get("Link"))
            if len(link) and link[len(link) - 1] == 'rel="next"':
                res = _append_orders(link[len(link) - 2][1:-1])
            else:
                break

        return Table(orders)

    def get_query_url(
        self,
        query_date: str = None,
        since_id: str = None,
        table_name: str = None,
        count: bool = True,
    ) -> str:
        """
        Get the URL of a Shopify API request.

        Args:
            query_date (str, optional): Filter query by a date that rows were created. Format: yyyy-mm-dd.
                This filter is ignored if value is None. Defaults to None.
            since_id (str, optional): Filter query by a minimum ID. This filter is ignored if value is None.
                Defaults to None.
            table_name (str, optional): The name of the Shopify table to query. Defaults to None.
            count (bool, optional): True if refund should be included in Table, False otherwise.
                Defaults to True.

        """
        filters = "limit=250&status=any"

        table = table_name + "/count.json" if count else table_name + ".json"

        if query_date:
            # Specific date if provided
            query_date = datetime.strptime(query_date, "%Y-%m-%d")
            max_date = query_date + timedelta(days=1)
            filters += (
                f"&created_at_min={query_date.isoformat()}&created_at_max={max_date.isoformat()}"
            )
        elif since_id:
            # Since ID if provided
            filters += f"&since_id={since_id}"

        return self.base_url + f"{table}?{filters}"

    def graphql(self, query: str) -> dict:
        """
        Make GraphQL request.

        Reference: https://shopify.dev/api/admin-graphql

        Args:
            query (str): GraphQL query.

        """
        return (
            self.client.request(self.base_url + "graphql.json", "POST", json={"query": query})
            .json()
            .get("data")
        )

    @classmethod
    def load_to_table(
        cls,
        subdomain=None,
        password=None,
        api_key=None,
        api_version=None,
        query_date=None,
        since_id=None,
        completed=True,
    ):
        """
        Fast classmethod so you can get the data all at once:
            tabledata = Shopify.load_to_table(subdomain='myorg', password='abc123',
                                            api_key='abc123', api_version='2020-10',
                                            query_date='2020-10-20', since_id='8414',
                                            completed=True) This instantiates the class and makes the appropriate query
        type to Shopify's orders table based on which arguments are supplied.

        Args:
            cls
            subdomain (str, optional): The Shopify subdomain (e.g. ``myorg`` for myorg.myshopify.com).
                Defaults to None.
            password (str, optional): The Shopify account password. Defaults to None.
            api_key (str, optional): The Shopify account API key. Defaults to None.
            api_version (str, optional): The Shopify API version. Defaults to None.
            query_date (str, optional): Filter query by a date that rows were created. Format: yyyy-mm-dd.
                This filter is ignored if value is None. Defaults to None.
            since_id (str, optional): Filter query by a minimum ID. This filter is ignored if value is None.
                Defaults to None.
            completed (bool, optional): True if only getting completed orders, False otherwise.
                value as value. Defaults to True.

        Returns:
            Table

        """
        return cls(subdomain, password, api_key, api_version).get_orders(
            query_date, since_id, completed
        )
