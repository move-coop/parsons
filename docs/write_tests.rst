=========================================
How to Write Tests for Parsons Connectors
=========================================

******************
How to Write Tests
******************

Most of our Parsons Connector classes fall into two categories:

 * Classes that call directly into HTTP API's using the Parsons ``APIConnector`` class
 * Classes that wrap around third party Python libraries, often using their own "client" class

The category that the class falls into generally determines how one will write unit tests for the class because the type of Connector determines how we simulate the external API.

No matter which type it is, we are looking to use mocks to simulate the class' interactions with the external API. Mocks are fake versions of the functions or classes that our Connectors use to access the external API. By using mocks in our tests, we make it easier to set up and run our tests without having to worry about having the proper credentials, etc. that we would need to call into an API.

^^^^^^^^^^^^^^^
Getting Started
^^^^^^^^^^^^^^^

 * Add a folder *test_yourconnectorname* in parsons/test for your connector
 * Add a file *test_yourconnectorname.py* to the *test_yourconnectorname* folder
 * Add at least one `“Happy Path” <https://en.wikipedia.org/wiki/Happy_path>`_ test per public method of your connector

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Tests for HTTP API Connectors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For classes built using the ``APIConnector`` class, we can leverage the ``requests-mock`` library, since the ``APIConnector`` uses the ``requests`` library.

The ``requests-mock`` library allows us to simulate the API we are calling into by pretending to be an HTTP server. We can create canned responses, and introspect on the endpoints that our Connector called to ensure that the method we are testing is acting the way we expect.

For an example of testing a class built on the ``APIConnector``, we can look at the ``MailChimp`` connector.

In the code below, we have our ``TestMailchimp`` that serves as our test case. We have one test method to test calls to our ``get_campaigns`` method in our ``Mailchimp`` Connector class.

We decorate ``test_get_campaigns`` with the ``requests_mock.Mocker`` class, which passes in our requests mocker as an argument ``m``. We can then use this mock to configure our mock server.

To configure our mock API, we can make use of the ``get``, ``post``, ``patch``, ``put``, and ``delete`` methods on the mock object ``m``. These methods mirror the calls we expect our Connector to make to the API. The methods on the mock object correspond to the HTTP method that we are expecting our Connector class to call with, and the first argument to the mock method is the URL that we expect our Connector to call. We can then provide a ``json`` argument to the mock method to provide a canned response that the mock HTTP server should return.

Below, we will use the ``get`` method to tell the mock HTTP server that we expect a call to the ``campaigns`` endpoint of our API, and that the mock HTTP server should return our ``test_campaigns`` canned response.

.. code-block:: python

    class TestMailchimp(unittest.TestCase):

        @requests_mock.Mocker()
        def test_get_campaigns(self, m):

            mc = MailChimp(api_key='12345')

            # Test that campaigns are returned correctly.
            m.get(self.mc.uri + 'campaigns', json=expected_json.test_campaigns)
            tbl = self.mc.get_campaigns()

            self.assertEqual(tbl.num_rows, 2)


After wiring up the mock HTTP API, we are ready to call the ``get_campaigns`` method on our ``Mailchimp`` connector. Since we are using the ``requests_mock.Mocker`` class, our Connector will not actually hit the Mailchimp API; our call will be intercepted and the configured canned response will be returned.

The Mailchimp tests store the canned responses in a separate Python module, which can help keep the test code separate from the test data, which helps makes tests more readable. The test data is imported from the ``expected_json.py`` Python file that sits alongside the ``test_mailchimp.py`` test file.

The data is imported at the top of the ``test_mailchimp.py`` file:

.. code-block:: python

    from test.test_mailchimp import expected_json


``expected_json`` can now be used to pull in our canned response variables, as we saw above:

.. code-block:: python

    m.get(self.mc.uri + 'campaigns', json=expected_json.test_campaigns)


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Tests for Connectors Built on Third Party Libraries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For classes that wrap third party libraries, we are looking to simulate whatever client object that serves as the Python API for the calls to the external service. To simulate the client object, we can use the ``unittest.mock.MagicMock`` class from the Python standard library.

The ``MagicMock`` class allows us to build a fake version of the client object by simulating functionality we expect our Connector class to use -- namely by returning canned responses to method calls on the client. As well, the ``MagicMock`` class is recording those calls as they happen, so that after we have run through our tests, we can check that things happened in the way we expected.

The following gives a simple example of initializing, setting up, and checking expectations on a ``MagicMock`` class. Please see the following, SalesforceTest example on integrating it with your Connector class.

.. code-block:: python

    from unittest.mock import MagicMock

    # Initialize a MagicMock object to serve as our fake client
    mock_client = MagicMock()
    # Tell the client to return a canned list of people from its list_people method
    mock_client.list_people.return_value = [
        {'id': 1, 'name': 'Nicole Jackson'},
    ]

    # Your Connector would call the client like normal
    people = mock_client.list_people()

    # Check that we got our expected data
    assert len(people) == 1
    assert people[0]['id'] == 1

    # Check that the list_people method was called
    mock_client.list_people.assert_called()

The ``Salesforce`` class is a good example for writing tests for Connector classes written against a third party library. The ``Salesforce`` Parsons Connector class wraps around the ``simple-salesforce`` library's Salesforce client. When testing the ``Salesforce`` Parsons class, we will need to swap out its reference to the ``simple-salesforce`` client with a mock client.

In the ``SalesforceTest`` class, this is done in the ``setUp`` method of the test class:

.. code-block:: python

    def setUp(self):
        self.sf = Salesforce()
        self.sf._client = mock.MagicMock()


The ``_client`` attribute on the Salesforce Connector class holds the class' reference to the underlying third party client object. By overriding it with our ``MagicMock`` object, the ``Salesforce`` Parsons class will be calling methods on our mock client instead of an actual simple-salesforce client.

We can then set up our mock client's ``query_all`` method:

.. code-block:: python

    self.sf._client.query_all.return_value = [{'Id': 1, 'value': 'FAKE'}]


Now, we can test our Salesforce Parsons Connector's query method:

.. code-block:: python

    # Call the query method with a fake value
    response = self.sf.query('FAKESOQL')
    # Check that our mock client's query_all method was also called with the fake value
    self.sf._client.query_all.assert_called_with('FAKESOQL')
    # Check that the response from our query method is what we expect
    self.assertEqual(response[0]['value'], 'FAKE')


In the first line, we call the method we are testing (query) with a fake value. In the next line, we check to make sure our mock client's ``query_all`` method was called with the same fake value. Finally, we test to make sure that our ``Salesforce`` Connector returned the expected response, which is based on the return value of the mock client's ``query_all`` method (which we set up in the previous block).

That's pretty much all there is to it. When writing tests for a Connector wrapping a third party library, we will almost always:

 * Create a mock client using the MagicMock class, and wire up the methods that our Connector will need
 * Replace the actual third party library's client on our Connector class with our mock
 * Call the method(s) on the Connector that we are looking to test
 * Verify the return value of the method calls is what we expect
 * Verify that the Connector called the expected methods on our mock client

^^^^^^^^^^^
Useful Tips
^^^^^^^^^^^

Parsons has a function ``assert_matching_tables`` in the ``parsons.test.conftest`` module that can be used to compare two Parsons tables:

.. code-block:: python

    from parsons import Table
    from test.conftest import assert_matching_tables

    a = Table()
    b = Table()

    # This fails because it actually tests whether a and b are the same instance
    assert(a == b)

    # But this works
    assert(list(a) == list(b))

    # And this works
    assert_matching_tables(a, b)
