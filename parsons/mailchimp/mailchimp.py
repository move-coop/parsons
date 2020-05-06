import logging
import re
from parsons.etl import Table
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)


class Mailchimp():
    """
    Instantiate Mailchimp Class

    `Args:`
        api_key:
            The Mailchimp-provided application key. Not required if
            ``MAILCHIMP_API_KEY`` env variable set.
    `Returns:`
        Mailchimp Class
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.domain = re.findall("(?<=-).+$", self.api_key)[0]
        self.uri = f'https://{self.domain}.api.mailchimp.com/3.0/'
        self.client = APIConnector(self.uri, auth=('x', self.api_key))

    def get_request(self, endpoint, params=None, **kwargs):
        # Internal method to make a get request.

        r = self.client.request(self.uri + endpoint, 'GET', params=params)
        self.client.validate_response(r)
        data = r.json()

        return data

    def transform_table(self, tbl, fields_to_expand=None):
        # Internal method to transform a table prior to returning

        tbl.sort()
        if fields_to_expand:
            [tbl.unpack_dict(x, prepend=False) for x in fields_to_expand]

        return tbl

    def get_lists(self, fields=None, exclude_fields=None,
                  count=None, offset=None, before_date_created=None,
                  since_date_created=None, before_campaign_last_sent=None,
                  since_campaign_last_sent=None, email=None, sort_field=None,
                  sort_dir=None):

        params = {'fields': fields,
                  'exclude_fields': exclude_fields,
                  'count': count,
                  'offset': offset,
                  'before_date_created': before_date_created,
                  'since_date_created': since_date_created,
                  'before_campaign_last_sent': before_campaign_last_sent,
                  'since_campaign_last_sent': since_campaign_last_sent,
                  'email': email,
                  'sort_field': sort_field,
                  'sort_dir': sort_dir}

        response = self.get_request('lists', params=params)
        tbl = Table(response['lists'])
        logger.info(f'Found {tbl.num_rows} lists.')
        if tbl.num_rows > 0:
            return tbl
        else:
            return None

    def get_campaigns(self, fields=None, exclude_fields=None,
                      count=None, offset=None, type=None, status=None,
                      before_send_time=None, since_send_time=None,
                      before_create_time=None, since_create_time=None,
                      list_id=None, folder_id=None, member_id=None,
                      sort_field=None, sort_dir=None):

        params = {'fields': fields,
                  'exclude_fields': exclude_fields,
                  'count': count,
                  'offset': offset,
                  'type': type,
                  'status': status,
                  'before_send_time': before_send_time,
                  'since_send_time': since_send_time,
                  'before_create_time': before_create_time,
                  'since_create_time': since_create_time,
                  'list_id': list_id,
                  'folder_id': folder_id,
                  'member_id': member_id,
                  'sort_field': sort_field,
                  'sort_dir': sort_dir}

        response = self.get_request('campaigns', params=params)
        tbl = Table(response['campaigns'])
        logger.info(f'Found {tbl.num_rows} campaigns.')
        if tbl.num_rows > 0:
            return tbl
        else:
            return None

    def get_members(self, list_id, fields=None,
                    exclude_fields=None, count=None, offset=None,
                    email_type=None, status=None, since_timestamp_opt=None,
                    before_timestamp_opt=None, since_last_changed=None,
                    before_last_changed=None, unique_email_id=None,
                    vip_only=False, interest_category_id=None,
                    interest_ids=None, interest_match=None, sort_field=None,
                    sort_dir=None, since_last_campaign=None,
                    unsubscribed_since=None):

        params = {'fields': fields,
                  'exclude_fields': exclude_fields,
                  'count': count,
                  'offset': offset,
                  'email_type': email_type,
                  'status': status,
                  'since_timestamp_opt': since_timestamp_opt,
                  'before_timestamp_opt': before_timestamp_opt,
                  'since_last_changed': since_last_changed,
                  'before_last_changed': before_last_changed,
                  'unqiue_email_id': unique_email_id,
                  'vip_only': vip_only,
                  'interest_category_id': interest_category_id,
                  'interest_ids': interest_ids,
                  'interest_match': interest_match,
                  'sort_field': sort_field,
                  'sort_dir': sort_dir,
                  'since_last_campaign': since_last_campaign,
                  'unsubscribed_since': unsubscribed_since}

        response = self.get_request('lists/' + list_id + '/members',
                                    params=params)
        tbl = Table(response['members'])
        logger.info(f'Found {tbl.num_rows} members.')
        if tbl.num_rows > 0:
            return tbl
        else:
            return None

    def get_campaign_emails(self, campaign_id, fields=None,
                            exclude_fields=None, count=None, offset=None,
                            since=None):

        params = {'fields': fields,
                  'exclude_fields': exclude_fields,
                  'count': count,
                  'offset': offset,
                  'since': since}

        response = self.get_request('reports/' + campaign_id +
                                    '/email-activity',
                                    params=params)
        tbl = Table(response['emails'])
        if tbl.num_rows > 0:
            return tbl
        else:
            return None

    def get_unsubscribes(self, campaign_id, fields=None,
                         exclude_fields=None, count=None, offset=None):

        params = {'fields': fields,
                  'exclude_fields': exclude_fields,
                  'count': count,
                  'offset': offset}

        response = self.get_request('reports/' + campaign_id + '/unsubscribed',
                                    params=params)
        tbl = Table(response['unsubscribes'])
        logger.info(f'Found {tbl.num_rows} unsubscribes for {campaign_id}.')
        if tbl.num_rows > 0:
            return tbl
        else:
            return None