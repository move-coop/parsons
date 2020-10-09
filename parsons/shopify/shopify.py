from datetime import date, datetime, timedelta
from enum import Enum
from io import StringIO
import requests

from parsons.etl.table import Table
from parsons.utilities import check_env

class QueryTypes(Enum):
    COUNT = "count"
    ORDERS = "orders"

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
            The authorized ActionKit user password. Not required if ``SHOPIFY_API_KEY``
            env variable set.
    """

    def __init__(self, subdomain=None, password=None, api_key=None):
        self.COUNT = QueryTypes.COUNT
        self.ORDERS = QueryTypes.ORDERS
        self.subdomain = check_env.check('SHOPIFY_SUBDOMAIN', subdomain)
        self.password = check_env.check('SHOPIFY_PASSWORD', password)
        self.api_key = check_env.check('SHOPIFY_API_KEY', api_key)

    def get_csv(self, tbl=None):
        """
        Generate StringIO from a Table
        """
        csv_path = tbl.to_csv()
        csv_contents = ''
        with open(csv_path, newline='') as csv_file:
            csv_contents = csv_file.read()
        
        return StringIO(csv_contents).getvalue()

    def get_orders_tbl(self, url=None):
        """
        Generate Table from a URL
        """
        if url is None:
            url = self.get_query(None, None, 1, self.ORDERS)
        # Get orders
        orders = requests.get(url).json().get(self.ORDERS.value, [])
        # Filter out refunds
        orders = [order for order in orders if order.get('financial_status', '') != 'refunded']
        
        return Table(orders)

    def get_query(self, min_date=None, since_id=None, page=1, query_type=QueryTypes.COUNT, limit=250):
        if query_type == QueryTypes.ORDERS:
            filters = 'page=%s&limit=%d&status=any' % (
                page,
                limit
            )
            table = 'orders.json'
        else:
            filters = 'status=any'
            table = 'orders/count.json'

        if min_date:
            # Specific date if provided
            min_date = datetime.strptime(min_date, "%Y-%m-%d")
            max_date = min_date + timedelta(days=1)
            filters += '&created_at_min=%sT00:00:00-05:00&created_at_max=%sT00:00:00-05:00' % (datetime.strftime(min_date, "%Y-%m-%d"), datetime.strftime(max_date, "%Y-%m-%d"))
        elif since_id:
            # Since ID if provided
            filters += '&since_id=%s' % since_id
        else:
            # Default to yesterday
            max_date = date.today()
            min_date = max_date + timedelta(days=-1)
            filters += '&created_at_min=%sT00:00:00-05:00&created_at_max=%sT00:00:00-05:00' % (datetime.strftime(min_date, "%Y-%m-%d"), datetime.strftime(max_date, "%Y-%m-%d"))

        url = 'https://%s:%s@%s.myshopify.com/admin/%s?%s' % (
            self.api_key,
            self.password,
            self.subdomain,
            table,
            filters
        )

        if query_type == QueryTypes.ORDERS:
            return url
        else:
            return requests.get(url).json().get(self.COUNT.value, 0)