========================
How to Build a Connector
========================

Connector classes are at the heart of the Parsons project.  When we want to add a new service for users to connect to with Parsons, we build a new Connector class for that service.

The documentation contains `a complete list <https://move-coop.github.io/parsons/html/index.html#integrations>`_ of existing connectors.  Requests for new connectors are made and discussed in `our issue tracker <https://github.com/move-coop/parsons/issues?q=is%3Aissue+is%3Aopen+label%3A%22new+connector%22>`_.  Before starting to build a new connector, check to see if there’s any discussion about it in the tracker.  Ideally, you’ll have a good sense of what you and/or other users want the connector to do before you start trying to build it.  Remember, you can always reach out to the community and ask for advice!

When you’re ready to get started, make sure you have Parsons installed and that the tests run successfully.

---------------
Getting Started
---------------

The first thing you’ll need to do is create a new folder for your connector.  This folder should have the same name as the module (file) within the folder, and the same name as the connector class.  For example, the airtable connector is in the “airtable” folder, and the hustle connector is in the “hustle” folder.

Inside the folder, create two files.  The first should be named __init__.py and should be empty.  The second will have the same name as your folder - this is the file which will have your connector’s code.  For example, in the airtable folder this file is called airtable.py and in the hustle folder it’s called hustle.py.

The directory should look like this:

.. code-block:: python
    yourconnectorname/
    __init__.py
        yourconnectorname.py
		
Next, add the reference to your connector to parsons/__init__.py.  Specifically, open parsons/__init__.py, scroll to the end of the other imports, and add the following:

.. code-block:: python
	from parsons.yourconnectorname.yourconnectorname import yourconnectorname
	
Also, in parsons/__init__.py add 'yourconnectorname' to the end of the list __all__.

Once this is done, open the yourconnectorname.py file.  At the top of the file, add the following code to enable logging for our connector:

.. code-block:: python

    import logging


    logger = logging.getLogger(__name__)

You’ll also want to create the Connector class itself:

.. code-block:: python

    class YourConnectorName(object):
        “””`Args:`”””

        def __init__(self, api_key=None):
            pass

The text enclosed in triple quotes “”” “”” is called a DocString, and is used to provide information about the class.  Typically, it includes the arguments accepted by the __init__ method of the class.

The __init__ method defines how the class is instantiated.  For instance, if you want to get an instance of the Connector class by writing `connector = YourConnectorName(table_name, api_key)` you’d have to add a table_name argument to go with the api_key argument.  Your connector’s init statement will probably require a different set of arguments than we’ve written here, but this makes for a good start.

In our Parsons connector classes, the __init__ method should handle authentication.  That is, when we initialize our Connector, we should give it credentials so that it can connect to the third-party service.  Then we won’t have to worry about authenticating in the other methods.  How exactly you authenticate to the service will depend on the service, but it typically involves getting an api_key or access_token, and it almost always involves creating an account on the service.

(Users of your connector class will need to know how to authenticate too!  Take notes of where you signed up for an account and how you got the api key, access token, etc so you can include it in the documentation for your connector.)

We like to give users two different options for getting api keys and other authentication to the connector - passing them as arguments to the __init__ method, and storing them as environmental variables.  Use the Parsons utility checkenv to allow for either possibility with code that looks like this:

.. code-block:: python

    import logging
    from parsons.utilities import check_env

    logger = logging.getLogger(__name__)


    class YourConnectorName(object):
        “””`Args:`”””

        def __init__(self, api_key=None):
            self.api_key = check_env.check('YOURCONNECTORNAME_API_KEY', api_key)

This code looks in the environmental variables for the api key and, if it doesn’t find it, uses the api_key passed in.

Most connectors make extensive use of existing client/providers.  Most likely, your next step will be to instantiate one of those existing clients using the authentication data, and add it to the class.  You can see an example of this in the `Airtable Connector <https://github.com/move-coop/parsons/blob/master/parsons/airtable/airtable.py#L22>`_.

--------
Patterns
--------

Parsons has a number of patterns that should be used when developing a connector to ensure that connectors look alike, which makes them easier to use and modify. Not all patterns apply to all connectors, but when reviewing pull requests, the maintainers will be looking to see if you adhere to the patterns described in this document.

In the sections below, we will attempt to enumerate the established patterns. We will use the `parsons.mailchimp.mailchimp.Mailchimp` connector as an example of how to implement the patterns.

^^^^^^^^^^^^^^^^^^^^
Class initialization
^^^^^^^^^^^^^^^^^^^^

**Allow configuration of a connector with environment variables as well as arguments passed to the class initializer.** Make use of `parsons.utilities.check_env.check` function to check that the value was provided either as an argument to the initializer, or in the environment.

**When calling into a web API, use the `parsons.utilities.APIConnector` class.** The `APIConnector` class has a number of methods for making web requests, and using the `APIConnector` helps enforce consistency across connectors. The `APIConnector` is a wrapper around the Python `requests` library.


Mailchimp example:

.. code-block:: python

    from parsons.utilities import check_env
    from parsons.utilities.api_connector import APIConnector


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

        def __init__(self, api_key=None):
            self.api_key = check_env.check('MAILCHIMP_API_KEY', api_key)
            self.domain = re.findall("(?<=-).+$", self.api_key)[0]
            self.uri = f'https://{self.domain}.api.mailchimp.com/3.0/'
            self.client = APIConnector(self.uri, auth=('x', self.api_key))

In the `__init__` method above, the Mailchimp class takes one argument: `api_key`. The argument has a default value of `None`, which allows for a user to initialize the connector without any arguments (ie `Mailchimp()`. If no value is passed for `api_key` as an argument to the `__init__` method, then the `check_env.check` function will attempt to retrieve the value from the `MAILCHIMP_API_KEY` environment variable. If the value is neither passed in as argument nor in the environment, the `check_env.check` method will raise a `KeyError` exception.

In the last line of the code snippet above, the `Mailchimp` class creates an `APIConnector` class, providing the root URL for the API (`self.uri`). The Mailchimp API accepts basic authentication as an authentication mechanism, so the `Mailchimp` connector is able to pass the `api_key` to the `APIConnector` via the `auth` keyword argument. If the API for your connector does not support basic authentication, you may need to implement your own authentication (e.g. via request headers).

^^^^^^^^^^^^^^^^^^^^^^^^
Your connector’s methods
^^^^^^^^^^^^^^^^^^^^^^^^

**The methods of your connector should generally mirror the endpoints of the API.** Every API is different, but the connector should generally look like the API it is connecting to. Methods of your connector should reference the resources the API is using (e.g. “people”, “members”, “events”).

The following lists rules for naming common endpoints:

* GET - single record - *get_<resource>* (e.g. get_event, get_person)
* GET - multiple records - *get_<resource>s* (e.g. get_members, get_people)
* POST - single record - *create_<resource>* (e.g. create_person, create_tag)
* PUT - single record - *update_<resource>* (e.g. update_person, update_event)
* DELETE - single record - *delete_<resource>* (e.g. delete_member)

**A method’s arguments should mirror the parameters of the API endpoint it is calling.** Optional parameters should be optional in your method signature (i.e. default to `None`).

**Use Python docstrings to document every public method of your class.** The docstrings for your public methods are used to automatically generate documentation for your connector. Having this documentation for every method makes it easier for users to pick up your connector.

**Methods returning multiple values should return a Parsons Table.** If the list of results is empty, return an empty Parsons `Table` (not `None`). Methods returning a single value should just return the value. If the API could not find the value (eg, the ID provided for a resource was not found), return a `None` value from the method.

Mailchimp example:

.. code-block:: python

    class Mailchimp():

        def get_lists(self, fields=None, exclude_fields=None,
                    count=None, offset=None, before_date_created=None,
                    since_date_created=None, before_campaign_last_sent=None,
                    since_campaign_last_sent=None, email=None, sort_field=None,
                    sort_dir=None):
            """
            Get a table of lists under the account based on query parameters. Note
            that argument descriptions here are sourced from Mailchimp's official
            API documentation.

            `Args:`
                fields: list of strings
                    A comma-separated list of fields to return. Reference
                    parameters of sub-objects with dot notation.
                exclude_fields: list of strings
                    A comma-separated list of fields to exclude. Reference
                    parameters of sub-objects with dot notation.
                count: int
                    The number of records to return. Default value is 10. Maximum
                    value is 1000.
                offset: int
                    The number of records from a collection to skip. Iterating over
                    large collections with this parameter can be slow. Default
                    value is 0.
                before_date_created: string
                    Restrict response to lists created before the set date. We
                    recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00.
                since_date_created: string
                    Restrict results to lists created after the set date. We
                    recommend ISO 8601 time format: 2015-10-21T15:41:36+00:00.
                before_campaign_last_sent: string
                    Restrict results to lists created before the last campaign send
                    date. We recommend ISO 8601 time format:
                    2015-10-21T15:41:36+00:00.
                since_campaign_last_sent: string
                    Restrict results to lists created after the last campaign send
                    date. We recommend ISO 8601 time format:
                    2015-10-21T15:41:36+00:00.
                email: string
                    Restrict results to lists that include a specific subscriber's
                    email address.
                sort_field: string, can only be 'date_created' or None
                    Returns files sorted by the specified field.
                sort_dir: string, can only be 'ASC', 'DESC', or None
                    Determines the order direction for sorted results.

            `Returns:`
                Table Class
            """
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
                return Table()


The `get_lists` method corresponds to the `GET /lists <https://mailchimp.com/developer/reference/lists/#get_/lists>`_ endpoint on the Mailchimp API. The method has a number of arguments (all optional), all of which are described in the docstring. The arguments are then mapped to the name of the endpoints’ parameters, and passed to the `APIConnector`’s `get_request` method.

The method can return more than one record, so the results of the call to the API are wrapped in a Parsons `Table`. If there are no results from the call, an empty table is returned.

------------
Finishing up
------------

^^^^^^^^^^^^^^^
Testing locally
^^^^^^^^^^^^^^^

In order to test locally, you will need to install the version of Parsons that you have been working on. To do that, you will need to install in "editable" mode, which allows you to import your local Parsons code instead of the released code.

To install Parsons in "editable" mode, run the following, where `<parsons-path>` is the path to the root of the Parsons repository on your local machine.

```bash
pip install -e <parsons-path>
```

^^^^^^^^^^^^^^^^^^^^^^
Adding automated tests
^^^^^^^^^^^^^^^^^^^^^^

 * Add a folder *test_yourconnectorname* in parsons/test for your connector
 * Add a file *test_yourconnectorname.py* to the *test_yourconnectorname* folder
 * Use the code below as a starting point for your tests
 * Add one `“Happy Path” <https://en.wikipedia.org/wiki/Happy_path>`_ test per public method of your connector
 * When possible mock out any external integrations, otherwise mark your test using the

```python
from parsons.yourconnector.yourconnector import YourConnector
import unittest
import requests_mock


class TestYourConnector(unittest.TestCase):

    def setUp(self):

        # add any setup code here to run before each test
        pass

    def tearDown(self):

        # add any teardown code here to run after each test
        pass

    @requests_mock.Mocker()
    def test_get_things(self, m):

    	# Test that campaigns are returned correctly.
        m.get(‘http://yourconnector.com/v1/things’, json=[])
        yc = YourConnector()
        tbl = yc.get_things()

        self.assertEqual(tbl.num_rows, 0)
```

^^^^^^^^^^^^^^^^^^^^
Adding documentation
^^^^^^^^^^^^^^^^^^^^

 * Add *yourconnectorname.rst* to the parsons/docs folder.
 * Use the parsons/docs/_template.rst file as a guide for the documentation for your connector.
 * Add a reference to your connector’s doc file to the parsons/docs/index.rst
 * You just need to add the filename without the .rst extension (ie *yourconnector*)
 * Be sure to add *yourconnector* in alphabetical order

^^^^^^^^^^^
Final steps
^^^^^^^^^^^

 * Add any new dependencies to the parsons/requirements.txt file
 * Run the entire suite of Parsons unit tests using the `pytest -rf test` command
 * Run the linter against Parsons using `flake8 --max-line-length=100 parsons`
 * Double-check that you have committed all of your code changes to your branch, and that you have pushed your branch to your fork
 * Open a pull request against the move-coop/parsons repository
