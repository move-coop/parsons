from datetime import datetime, timedelta
import re
import requests

from parsons.etl.table import Table
from parsons.utilities import check_env

class Shopify(object):
    """
    Instantiate the Shopify class

    `Args:`
        subdomain: str
            The Shopify subdomain (e.g. ``myorg`` for myorg.myshopify.com) Not required if
            ``SHOPIFY_SUBDOMAIN`` env variable set.
        password: str
            The Shopify account password. Not required if ``SHOPIFY_PASSWORD`` env
            variable set.
        api_key: str
            The Shopify account API key. Not required if ``SHOPIFY_API_KEY`` env variable
            set.
        api_version: str
            The Shopify API version. Not required if ``SHOPIFY_API_VERSION`` env variable
            set.
    `Returns:`
        Shopify Class
    """
    def __init__(self, subdomain=None, password=None, api_key=None, api_version=None):
        self.subdomain = check_env.check('SHOPIFY_SUBDOMAIN', subdomain)
        self.password = check_env.check('SHOPIFY_PASSWORD', password)
        self.api_key = check_env.check('SHOPIFY_API_KEY', api_key)
        self.api_version = check_env.check('SHOPIFY_API_VERSION', api_version)

    def get_count(self, query_date=None, since_id=None, table_name=None):
        """
        Get the count of rows in a table.

        `Args:`
            query_date: str
                Filter query by a date that rows were created. This filter is ignored if value
                is None.
            since_id: str
                Filter query by a minimum ID. This filter is ignored if value is None.
            table_name: str
                The name of the Shopify table to query.
        `Returns:`
            int
        """
        return requests.get(self.get_query_url(query_date, since_id, table_name), auth=(self.api_key, self.password)).json().get("count", 0)

    def get_orders(self, query_date=None, since_id=None, completed=True, cols_to_fill={}):
        """
        Get Shopify orders.

        `Args:`
            query_date: str
                Filter query by a date that rows were created. Format: yyyy-mm-dd. This filter
                is ignored if value is None.
            since_id: str
                Filter query by a minimum ID. This filter is ignored if value is None.
            completed: bool
                True if only getting completed orders, False otherwise.
            cols_to_fill: dict
                A dictionary of custom columns to add or fill, with column name as key and row
                value as value
        `Returns:`
            Table Class
        """
        orders = []

        def _append_orders(url):
            nonlocal orders

            if completed:
                url += '&financial_status=paid'

            res = requests.get(url, auth=(self.api_key, self.password))

            cur_orders = res.json().get("orders", [])

            # Flatten orders to non-complex types
            for order in cur_orders:
                keys_to_add = {}
                keys_to_delete = []

                for key1 in order:
                    if isinstance(order[key1], dict):
                        for key2 in order[key1]:
                            keys_to_add[key1 + '_' + key2] = order[key1][key2]
                        keys_to_delete.append(key1)
                    elif key1 == 'note_attributes':
                        for note in order[key1]:
                            keys_to_add[key1 + '_' + note['name']] = note['value']

                order.update(keys_to_add)
                for key in keys_to_delete:
                    del order[key]

            orders += cur_orders

            return res

        res = _append_orders(self.get_query_url(query_date, since_id, "orders", False))

        # Get next page
        while res.headers.get("Link"):
            link = re.split('; |, ', res.headers.get("Link"))
            if len(link) and link[len(link) - 1] == 'rel="next"':
                res = _append_orders(link[len(link) - 2][1:-1])
            else:
                break

        tbl = Table(orders)

        # Table transformations
        cols = tbl.columns

        for col in cols_to_fill:
            if col not in cols:
                tbl.add_column(col, cols_to_fill[col])
            else:
                tbl.fill_column(col, cols_to_fill[col])
        
        for col in cols:
            tbl.fillna_column(col, '')
        
        return tbl

    def get_query_url(self, query_date=None, since_id=None, table_name=None, count=True):
        """
        Get the URL of a Shopify API request

        `Args:`
            query_date: str
                Filter query by a date that rows were created. Format: yyyy-mm-dd. This filter
                is ignored if value is None.
            since_id: str
                Filter query by a minimum ID. This filter is ignored if value is None.
            table_name: str
                The name of the Shopify table to query.
            count: bool
                True if refund should be included in Table, False otherwise.
        `Returns:`
            str
        """
        filters = 'limit=250&status=any'

        if count:
            table = table_name + '/count.json'
        else:
            table = table_name + '.json'

        if query_date:
            # Specific date if provided
            query_date = datetime.strptime(query_date, "%Y-%m-%d")
            max_date = query_date + timedelta(days=1)
            filters += '&created_at_min={}&created_at_max={}'.format(query_date.isoformat(), max_date.isoformat())
        elif since_id:
            # Since ID if provided
            filters += '&since_id=%s' % since_id

        return 'https://%s.myshopify.com/admin/api/%s/%s?%s' % (
            self.subdomain,
            self.api_version,
            table,
            filters
        )
    
    @classmethod
    def load_to_table(cls, **kwargs):
        """
        Fast classmethod so you can get the data all at once:
        tabledata = Redash.load_to_table(subdomain='myorg', password='abc123',
                                         api_key='abc123', api_version='2020-10',
                                         query_date='2020-10-20', since_id='8414',
                                         completed=True)
        This instantiates the class and makes the appropriate query type to Shopify's orders
        table based on which arguments are supplied.

        `Args:`
            subdomain: str
                The Shopify subdomain (e.g. ``myorg`` for myorg.myshopify.com).
            password: str
                The Shopify account password.
            api_key: str
                The Shopify account API key.
            api_version: str
                The Shopify API version.
            query_date: str
                Filter query by a date that rows were created. Format: yyyy-mm-dd. This filter
                is ignored if value is None.
            since_id: str
                Filter query by a minimum ID. This filter is ignored if value is None.
            completed: bool
                True if only getting completed orders, False otherwise.
            cols_to_fill: dict
                A dictionary of custom columns to add or fill, with column name as key and row
                value as value
        `Returns:`
            Table Class
        """
        initargs = {a: kwargs.get(a) for a in ('subdomain', 'password', 'api_key', 'api_version') if a in kwargs}
        obj = cls(**initargs)
        
        return obj.get_orders(kwargs.get('query_date'), kwargs.get('since_id'), kwargs.get('completed'), kwargs.get('cols_to_fill'))