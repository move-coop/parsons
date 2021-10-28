import json
import logging
import requests
import time

from parsons.etl.table import Table
from parsons.utilities import check_env

logger = logging.getLogger(__name__)


class ActionKit(object):
    """
    Instantiate the ActionKit class

    `Args:`
        domain: str
            The ActionKit domain (e.g. ``myorg.actionkit.com``) Not required if
            ``ACTION_KIT_DOMAIN`` env variable set.
        username: str
            The authorized ActionKit username. Not required if ``ACTION_KIT_USERNAME`` env
            variable set.
        password: str
            The authorized ActionKit user password. Not required if ``ACTION_KIT_PASSWORD``
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

    def _base_get(self, endpoint, entity_id=None, exception_message=None, params=None):
        # Make a general get request to ActionKit

        resp = self.conn.get(self._base_endpoint(endpoint, entity_id), params=params)
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
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
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
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint('user', user_id), data=json.dumps(kwargs))
        logger.info(f'{resp.status_code}: {user_id}')

    def get_event(self, event_id):
        """Get an event.

        `Args:`
            event_id: int
                The id for the event.
        `Returns:`
            dict
                Event json object.

        """
        return self._base_get(f"event/{event_id}")

    def get_events(self, limit=None, **kwargs):
        """Get multiple events.

        `Args:`
            limit: int
                The number of events to return. If omitted, all events are returned.
            **kwargs:
                Optional arguments to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.

                Additionally, expressions to filter the data can also be provided. For addition
                info, visit `Django's docs on field lookups <https://docs.djangoproject.com/\
                en/3.1/topics/db/queries/#field-lookups>`_.

                .. code-block:: python

                    ak.get_events(fields__name__contains="FirstName")
        `Returns:`
            Parsons.Table
                The events data.
        """
        # "The maximum number of objects returned per request is 100. Use paging
        # to get more objects."
        # (https://roboticdogs.actionkit.com/docs//manual/api/rest/overview.html#ordering)
        # get `limit` events if it's provided, otherwise get 100
        kwargs["_limit"] = min(100, limit or 1_000_000_000)
        json_data = self._base_get("event", params=kwargs)
        data = json_data["objects"]

        next_url = json_data.get("meta", {}).get("next")
        while next_url:
            resp = self.conn.get(f'https://{self.domain}{next_url}')
            data += resp.json().get("objects", [])
            next_url = resp.json().get("meta", {}).get("next")
            if limit and len(data) >= limit:
                break

        return Table(data[:limit])

    def update_event(self, event_id, **kwargs):
        """
        Update an event.

        `Args:`
            event_id: int
                The event id of the event to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint('event', event_id), data=json.dumps(kwargs))
        logger.info(f'{resp.status_code}: {event_id}')

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
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
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
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
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
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
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
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
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
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            API location of new resource
        """

        return self._base_post(endpoint='eventsignupform',
                               exception_message='Could not event create signup form',
                               page=f'/rest/v1/page/{page_id}/',
                               thank_you_text=thank_you_text,
                               **kwargs)

    def update_event_signup(self, event_signup_id, **kwargs):
        """
        Update an event signup.

        `Args:`
            event_signup_id: int
                The id of the event signup to update
            event_signup_dict: dict
                A dictionary of fields to update for the event signup.
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint('eventsignup', event_signup_id),
                               data=json.dumps(kwargs))
        logger.info(f'{resp.status_code}: {event_signup_id}')

    def get_mailer(self, entity_id):
        """
        Get a mailer.

        `Args:`
            entity_id: int
                The entity id of the record to get.
        `Returns`:
            Mailer json object
        """

        return self._base_get(endpoint='mailer', entity_id=entity_id)

    def create_mailer(self, **kwargs):
        """
        Create a mailer.

        `Args:`
            **kwargs:
                Arguments and fields to pass to the client. A full list can be found in the
                `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/manual/api/\
                rest/mailer.html>`_.
        `Returns:`
            URI of new mailer
        """

        return self._base_post(endpoint='mailer', exception_message='Could not create mailer',
                               **kwargs)

    def copy_mailer(self, mailer_id):
        """
        copy a mailer
        returns new copy of mailer which should be updatable.
        """
        resp = self.conn.post(self._base_endpoint('mailer', entity_id=mailer_id) + '/copy')
        return(resp)

    def update_mailing(self, mailer_id, **kwargs):
        """
        Update a mailing.

        `Args:`
            mailing_id: int
                The id of the mailing to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint('mailer', mailer_id), data=json.dumps(kwargs))
        logger.info(f'{resp.status_code}: {mailer_id}')

    def rebuild_mailer(self, mailing_id):
        """
        Rebuild a mailer.

        `Args:`
            mailing_id: int
                Id of the mailer.
        `Returns:`
            URI to poll for progress
        """

        return self._base_post(endpoint='mailer/' + str(mailing_id) + '/rebuild',
                               exception_message='Could not rebuild mailer')

    def queue_mailer(self, mailing_id):
        """
        Queue a mailer.

        `Args:`
            mailing_id: int
                Id of the mailer.
        `Returns:`
            URI to poll for progress
        """

        return self._base_post(endpoint='mailer/' + str(mailing_id) + '/queue',
                               exception_message='Could not queue mailer')

    def update_order(self, order_id, **kwargs):
        """
        Update an order.

        `Args:`
            order_id: int
                The id of the order to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint('order', order_id),
                               data=json.dumps(kwargs))
        logger.info(f'{resp.status_code}: {order_id}')

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
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns`:
            API location of new resource
        """

        return self._base_post(endpoint='pagefollowup',
                               exception_message='Could not create page followup',
                               page=f'/rest/v1/eventsignuppage/{signup_page_id}/',
                               url=url,
                               **kwargs)

    def get_survey_question(self, survey_question_id):
        """
        Get a survey question.

        `Args:`
            survey_question_id: int
                The survey question id of the record to get.
        `Returns`:
            Survey question json object
        """

        return self._base_get(endpoint='surveyquestion', entity_id=survey_question_id,
                              exception_message='Survey question not found')

    def update_survey_question(self, survey_question_id, **kwargs):
        """
        Update a survey question.

        `Args:`
            survey_question_id: int
                The id of the survey question to update
            survey_question_dict: dict
                A dictionary of fields to update for the survey question.
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint('surveyquestion', survey_question_id),
                               data=json.dumps(kwargs))
        logger.info(f'{resp.status_code}: {survey_question_id}')

    def update_transaction(self, transaction_id, **kwargs):
        """
        Update a transaction.

        `Args:`
            transaction_id: int
                The id of the transaction to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint('transaction', transaction_id),
                               data=json.dumps(kwargs))
        logger.info(f'{resp.status_code}: {transaction_id}')

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
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
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

        url = self._base_endpoint('upload')
        files = {'upload': csv_file}
        data = {
            'page': import_page,
            'autocreate_user_fields': int(autocreate_user_fields),
            'user_fields_only': int(user_fields_only),
        }
        with upload_client.post(url, files=files, data=data) as res:
            progress_url = res.headers.get('Location')
            rv = {
                'res': res,
                'success': res.status_code == 201,
                'id': progress_url.split('/')[-2] if progress_url else None,
                'progress_url': progress_url
            }
            return rv

    def bulk_upload_table(self, table, import_page, autocreate_user_fields=0,
                          no_overwrite_on_empty=False, set_only_columns=None):
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
            set_only_columns: list
                This is similar to no_overwrite_on_empty but restricts to a specific set of columns
                which, if blank, should not be overwritten.
        `Returns`:
            dict
                success: bool -- whether upload was successful (individual rows may not have been)
                results: [dict] -- This is a list of the full results.
                         progress_url and res for any results
        """ # noqa: E501,E261

        import_page = check_env.check('ACTION_KIT_IMPORTPAGE', import_page)
        upload_tables = self._split_tables_no_empties(
            table, no_overwrite_on_empty, set_only_columns)
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

    def _split_tables_no_empties(self, table, no_overwrite_on_empty, set_only_columns):
        table_groups = {}
        # uploading combo of user_id and email column should be mutually exclusive
        blank_columns_test = table.columns
        if not no_overwrite_on_empty:
            blank_columns_test = (set(['user_id', 'email'] + (set_only_columns or []))
                                  .intersection(table.columns))
        for row in table:
            blanks = tuple(k for k in blank_columns_test
                           if row.get(k) in (None, ''))
            grp = table_groups.setdefault(blanks, [])
            grp.append(row)
        results = []
        for blanks, subset in table_groups.items():
            subset_table = Table(subset)
            if blanks:
                subset_table.table = subset_table.table.cutout(*blanks)
            logger.debug(f'Column Upload Blanks: {blanks}')
            logger.debug(f'Column Upload Columns: {subset_table.columns}')
            if not set(['user_id', 'email']).intersection(subset_table.columns):
                logger.warning(
                    f'Upload will fail without user_id or email. '
                    f'Rows: {subset_table.num_rows}, Columns: {subset_table.columns}'
                )
            results.append(subset_table)
        return results

    def collect_upload_errors(self, result_array):
        """
        Collect any upload errors as a list of objects from bulk_upload_table 'results' key value.
        This waits for uploads to complete, so it may take some time if you uploaded a large file.
        `Args:`
            result_array: list
                After receiving a dict back from bulk_upload_table you may want to see if there
                were any errors in the uploads.  If you call collect_upload_errors(result_array)
                it will iterate across each of the uploads fetching the final result of e.g.
                /rest/v1/uploaderror?upload=123
        `Returns`:
            [dict]
                message: str -- error message
                upload: str -- upload progress API path e.g. "/rest/v1/upload/123456/"
                id: int -- upload error record id (different than upload id)
        """
        errors = []
        for res in result_array:
            upload_id = res.get('id')
            if upload_id:
                while True:
                    upload = self._base_get(endpoint='upload', entity_id=upload_id)
                    if not upload or upload.get('status') != 'new':
                        break
                    else:
                        time.sleep(1)
                error_data = self._base_get(endpoint='uploaderror', params={'upload': upload_id})
                logger.debug(f'error collect result: {error_data}')
                errors.extend(error_data.get('objects') or [])
        return errors
