import json
import logging
import requests

from parsons.etl.table import Table
from parsons.utilities import check_env

logger = logging.getLogger(__name__)


class ActionKit(object):
    """
    Instatiate the ActionKit class

    `Args:`
        domain: str
            The ActionKit domain (e.g. ``myorg.actionkit.com``) Not required if
            ``ACTION_KIT_DOMAIN`` env variable set.
        username: str
            The authorized ActionKit username. Not required if ``ACTION_KIT_USERNAME`` env
            variable set.
        password: str
            The authorized ActionKit user password. Not required if ``ACTION_KIT_USERNAME``
            env variable set.
    """

    _default_headers = {'content-type': 'application/json',
                        'accepts': 'application/json'}

    def __init__(self, domain=None, username=None, password=None):

        self.domain = check_env.check('ACTION_KIT_DOMAIN', domain)
        self.username = check_env.check('ACTION_KIT_USERNAME', username)
        self.password = check_env.check('ACTION_KIT_PASSWORD', password)
        self.conn = self._conn()

    def _conn(self, default_headers=_default_headers):

        client = requests.Session()
        client.auth = (self.username, self.password)
        client.headers.update(default_headers)
        return client

    def _base_endpoint(self, endpoint, entity_id=None):
        # Create the base endpoint URL

        url = f'https://{self.domain}/rest/v1/{endpoint}/'

        if entity_id:
            return url + f'{entity_id}/'
        return url

    def _base_get(self, endpoint, entity_id=None, exception_message=None):
        # Make a general get request to ActionKit

        resp = self.conn.get(self._base_endpoint(endpoint, entity_id))

        if exception_message and resp.status_code == 404:
            raise Exception(self.parse_error(resp, exception_message))

        return resp.json()

    def _base_post(self, endpoint, exception_message, return_full_json=False, **kwargs):
        # Make a general post request to ActionKit

        resp = self.conn.post(self._base_endpoint(endpoint), data=json.dumps(kwargs))

        if resp.status_code != 201:
            raise Exception(self.parse_error(resp, exception_message))

        # Some of the methods should just return pointer to location of created
        # object.
        if 'headers' in resp.__dict__ and not return_full_json:
            return resp.__dict__['headers']['Location']

        # Not all responses return a json
        try:
            return resp.json()

        except ValueError:
            return None

    def parse_error(self, resp, exception_message):
        # AK provides some pretty robust/helpful error reporting. We should surface them with
        # our exceptions.

        if 'errors' in resp.json().keys():
            if isinstance(resp.json()['errors'], list):
                exception_message += '\n' + ','.join(resp.json()['errors'])
            else:
                for k, v in resp.json()['errors'].items():
                    exception_message += str('\n' + k + ': ' + ','.join(v))

        return exception_message

    def get_user(self, user_id):
        """
        Get a user.

        `Args:`
            user_id: int
                The user id of the record to get.
        `Returns`:
            User json object
        """

        return self._base_get(endpoint='user', entity_id=user_id,
                              exception_message='User not found')

    def get_user_fields(self):
        """
        Get list of valid user fields that can be passed with the
        :meth:`ActionKit.create_user` method.

        `Returns`:
            List of user fields
        """

        resp = self._base_get(endpoint='user/schema')

        return list(resp['fields'].keys())

    def create_user(self, email, **kwargs):
        """
        Create a user.

        `Args:`
            email: str
                Email for the user
            user_dict: dict
                Optional; Additional user fields
        `Returns:`
            User json object
        """

        return self._base_post(endpoint='user', exception_message='Could not create user',
                               email=email, **kwargs)

    def update_user(self, user_id, **kwargs):
        """
        Update a user.

        `Args:`
            user_id: int
                The user id of the person to update
            user_dict: dict
                A dictionary of fields to update for the user.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint('user', user_id), data=json.dumps(kwargs))
        logger.info(f'{resp.status_code}: {user_id}')

    def delete_user(self, user_id):
        """
        Delete a user.

        `Args:`
            user_id: int
                The user id of the person to delete
        `Returns:`
            ``None``
        """

        resp = self.conn.delete(self._base_endpoint('user', user_id))
        logger.info(f'{resp.status_code}: {user_id}')

    def get_campaign(self, campaign_id):
        """
        Get a campaign.

        `Args:`
            campaign_id: int
                The campaign id of the record.
        `Returns`:
            Campaign json object
        """

        return self._base_get(endpoint='campaign', entity_id=campaign_id,
                              exception_message='Campaign not found')

    def get_campaign_fields(self):
        """
        Get list of valid campaign fields that can be passed with the
        :meth:`ActionKit.create_campaign` and :meth:`ActionKit.update_campaign` methods.

        `Returns`:
            List of campaign fields
        """

        resp = self._base_get(endpoint='campaign/schema')
        return list(resp['fields'].keys())

    def create_campaign(self, name, **kwargs):
        """
        Create a campaign.

        `Args:`
            name: str
                The name of the campaign to create
        `Returns`:
            API location of new resource
        """

        return self._base_post(endpoint='campaign', exception_message='Could not create campaign',
                               name=name, **kwargs)

    def get_event_create_page(self, event_create_page_id):
        """
        Get a event create page.

        `Args:`
            event_create_page_id: int
                The event create page id of the record to get.
        `Returns`:
            Event create page json object
        """

        return self._base_get(endpoint='eventcreatepage', entity_id=event_create_page_id,
                              exception_message='Event create page not found')

    def get_event_create_page_fields(self):
        """
        Get list of event create page fields that can be passed with the
        :meth:`ActionKit.create_event_create_page`.

        `Returns`:
            List of event create page fields
        """

        resp = self._base_get(endpoint='eventcreatepage/schema')
        return list(resp['fields'].keys())

    def create_event_create_page(self, name, campaign_id, title, **kwargs):
        """
        Add an event page to a campaign.

        `Args:`
            campaign_id: int
                The campaign to assoicate page with
            name: str
                The name of the page to create
            title: str
                The title of the page to create
        `Returns`:
            API location of new resource
        """

        return self._base_post(endpoint='eventcreatepage',
                               exception_message='Could not create event create page',
                               campaign=f'/rest/v1/campaign/{campaign_id}/',
                               name=name,
                               title=title,
                               **kwargs)

    def get_event_create_form(self, event_create_form_id):
        """
        Get a event create form.

        `Args:`
            event_create_form_id: int
                The event create form id of the record to get.
        `Returns`:
            Event create form json object
        """

        return self._base_get(endpoint='eventcreateform', entity_id=event_create_form_id,
                              exception_message='Event create page not found')

    def get_event_create_form_fields(self):
        """
        Get list of valid event create form fields that can be passed with the
        :meth:`ActionKit.create_event_create_form` method.

        `Returns`:
            List of event create form fields
        """

        resp = self._base_get(endpoint='eventcreateform/schema')
        return list(resp['fields'].keys())

    def create_event_create_form(self, page_id, thank_you_text, **kwargs):
        """
        Create a event create form.

        `Args:`
            page_id: int
                The page to associate the form with
            thank_you_text: str
                Free form thank you text
        `Returns:`
            API location of new resource
        """

        return self._base_post(endpoint='eventcreateform',
                               exception_message='Could not event create form',
                               page=f'/rest/v1/eventcreatepage/{page_id}/',
                               thank_you_text=thank_you_text,
                               **kwargs)

    def get_event_signup_page(self, event_signup_page_id):
        """
        Get event signup page.

        `Args:`
            event_signup_page_id: int
                The event signup page id of the record to get.
        `Returns`:
            Event signup page json object
        """

        return self._base_get(endpoint='eventsignuppage', entity_id=event_signup_page_id,
                              exception_message='User page signup page not found')

    def get_event_signup_page_fields(self):
        """
        Get list of valid event signup page fields that can be passed with the
        :meth:`ActionKit.create_event_signup_page` method.

        `Returns`:
            List of event signup page fields
        """

        resp = self._base_get(endpoint='eventsignuppage/schema')
        return list(resp['fields'].keys())

    def create_event_signup_page(self, name, campaign_id, title, **kwargs):
        """
        Add an event signup page to a campaign.

        `Args:`
            campaign_id: int
                The campaign to assoicate page with
            name: str
                The name of the page to create
            title: str
                The title of the page to create
        `Returns`:
            API location of new resource
        """

        return self._base_post(endpoint='eventsignuppage',
                               exception_message='Could not create signup page',
                               campaign=f'/rest/v1/campaign/{campaign_id}/',
                               name=name,
                               title=title,
                               **kwargs)

    def get_event_signup_form(self, event_signup_form_id):
        """
        Get a user.

        `Args:`
            event_signup_form_id: str
                The event signup form id of the record to get.
        `Returns`:
            Event signup form json object
        """

        return self._base_get(endpoint='eventsignupform', entity_id=event_signup_form_id,
                              exception_message='User page signup form not found')

    def get_event_signup_form_fields(self):
        """
        Get list of valid event signup form fields that can be passed with the
        :meth:`ActionKit.create_event_signup_form` method.

        `Returns`:
            List of event signup form fields
        """

        resp = self._base_get(endpoint='eventsignupform/schema')
        return list(resp['fields'].keys())

    def create_event_signup_form(self, page_id, thank_you_text, **kwargs):
        """
        Create a event signup form.

        `Args:`
            page_id: int
                The page to associate the form with
            thank_you_text: str
                Free form thank you text
        `Returns:`
            API location of new resource
        """

        return self._base_post(endpoint='eventsignupform',
                               exception_message='Could not event create signup form',
                               page=f'/rest/v1/page/{page_id}/',
                               thank_you_text=thank_you_text,
                               **kwargs)

    def get_page_followup(self, page_followup_id):
        """
        Get a page followup.

        `Args:`
            page_followup_id: int
                The user id of the record to get.
        `Returns`:
            Page followup json object
        """

        return self._base_get(endpoint='pagefollowup', entity_id=page_followup_id,
                              exception_message='Page followup not found')

    def get_page_followup_fields(self):
        """
        Get list of valid page followup fields that can be passed with the
        :meth:`ActionKit.create_page_followup` method.

        `Returns`:
            List of page followup fields
        """

        resp = self._base_get(endpoint='pagefollowup/schema')
        return list(resp['fields'].keys())

    def create_page_followup(self, signup_page_id, url, **kwargs):
        """
        Add a page followup.

        `Args:`
            signup_page_id: int
                The signup page to associate the followup page with
            url: str
                URL of the folloup page
        `Returns`:
            API location of new resource
        """

        return self._base_post(endpoint='pagefollowup',
                               exception_message='Could not create page followup',
                               page=f'/rest/v1/eventsignuppage/{signup_page_id}/',
                               url=url,
                               **kwargs)

    def create_generic_action(self, page, email=None, ak_id=None, **kwargs):
        """
        Post a generic action. One of ``ak_id`` or ``email`` is a required argument.

        `Args:`
            page:
                The page to post the action. The page short name.
            email:
                The email address of the user to post the action.
            ak_id:
                The action kit id of the record.
            **kwargs:
                Optional arguments and fields that can sent. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/manual/api/rest/actionprocessing.html>`_.
        `Returns`:
            dict
                The response json
        """ # noqa: E501,E261

        if not email or ak_id:
            raise ValueError('One of email or ak_id is required.')

        return self._base_post(endpoint='action',
                               exception_message='Could not create action.',
                               email=email,
                               page=page,
                               return_full_json=True,
                               **kwargs)

    def bulk_upload_csv(self, csv_file, import_page,
                        autocreate_user_fields=False, user_fields_only=False):
        """
        Bulk upload a csv file of new users or user updates.
        If you are uploading a table object, use bulk_upload_table instead.
        See `ActionKit User Upload Documentation <https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html>`_
        Be careful that blank values in columns will overwrite existing data.

        If you get a 500 error, try sending a much smaller file (say, one row),
        which is more likely to return the proper 400 with a useful error message

        `Args:`
            import_page: str
                The page to post the action. The page short name.
            csv_file: str or buffer
                The csv (optionally zip'd) file path or a file buffer object
                A user_id or email column is required.
                ActionKit rejects files that are larger than 128M
            autocreate_user_fields: bool
              When True columns starting with "user_" will be uploaded as user fields.
              See the `autocreate_user_fields documentation
              <https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html#create-a-multipart-post-request>`_.
            user_fields_only: bool
              When uploading only an email/user_id column and user_ user fields,
              ActionKit has a fast processing path.
              This doesn't work, if you upload a zipped csv though.
        `Returns`:
            dict
                success: whether upload was successful
                progress_url: an API URL to get progress on upload processing
                res: requests http response object
        """ # noqa: E501,E261

        # self.conn defaults to JSON, but this has to be form/multi-part....
        upload_client = self._conn({'accepts': 'application/json'})
        if isinstance(csv_file, str):
            csv_file = open(csv_file, 'rb')

        res = upload_client.post(
            self._base_endpoint('upload'),
            files={'upload': csv_file},
            data={'page': import_page,
                  'autocreate_user_fields': int(autocreate_user_fields),
                  'user_fields_only': int(user_fields_only)})
        rv = {'res': res,
              'success': res.status_code == 201,
              'progress_url': res.headers.get('Location')}
        return rv

    def bulk_upload_table(self, table, import_page, autocreate_user_fields=0,
                          no_overwrite_on_empty=False):
        """
        Bulk upload a table of new users or user updates.
        See `ActionKit User Upload Documentation <https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html>`_
        Be careful that blank values in columns will overwrite existing data.

        Tables with only an identifying column (user_id/email) and user_ user fields
        will be fast-processed -- this is useful for setting/updating user fields.

        .. note::
            If you get a 500 error, try sending a much smaller file (say, one row),
            which is more likely to return the proper 400 with a useful error message

        `Args:`
            import_page: str
                The page to post the action. The page short name.
            table: Table Class
                A Table of user data to bulk upload
                A user_id or email column is required.
            autocreate_user_fields: bool
                When True columns starting with "user_" will be uploaded as user fields.
                `ActionKit <https://actionkit.com/>`_.
                See the autocreate_user_fields `documentation <https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html#create-a-multipart-post-request>`_.
            no_overwrite_on_empty: bool
                When uploading user data, ActionKit will, by default, take a blank value
                and overwrite existing data for that user.
                This can be undesirable, if the goal is to only send updates.
                Setting this to True will divide up the table into multiple upload
                batches, changing the columns uploaded based on permutations of
                empty columns.
        `Returns`:
            dict
                success: bool -- whether upload was successful (individual rows may not have been)
                results: [dict] -- This is a list of the full results.
                         progress_url and res for any results
        """ # noqa: E501,E261

        import_page = check_env.check('ACTION_KIT_IMPORTPAGE', import_page)
        upload_tables = [table]
        if no_overwrite_on_empty:
            upload_tables = self._split_tables_no_empties(table)
        results = []
        for tbl in upload_tables:
            user_fields_only = int(not any([
                h for h in tbl.columns
                if h != 'email' and not h.startswith('user_')]))
            results.append(self.bulk_upload_csv(tbl.to_csv(),
                                                import_page,
                                                autocreate_user_fields=autocreate_user_fields,
                                                user_fields_only=user_fields_only))
        return {
            'success': all([r['success'] for r in results]),
            'results': results
        }

    def _split_tables_no_empties(self, table):
        table_groups = {}
        for row in table:
            blanks = tuple(k for k in table.columns
                           if row.get(k) in (None, ''))
            grp = table_groups.setdefault(blanks, [])
            grp.append(row)
        results = []
        for blanks, subset in table_groups.items():
            subset_table = Table(subset)
            if blanks:
                subset_table.table = subset_table.table.cutout(*blanks)
            results.append(subset_table)
        return results
