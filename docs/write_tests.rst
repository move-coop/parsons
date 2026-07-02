=========================================
How to Write Tests for Parsons Connectors
=========================================

This is the single, canonical guide for writing tests in Parsons. It defines
**one** way to structure a connector's tests, **one** decision rule for how to
mock the outside world, and **one** convention for where test data lives.

If you are updating an older test that does not follow these conventions, please
migrate it to this standard as you go.

.. contents:: On this page
   :local:
   :depth: 2


*******************
Guiding principle
*******************

**Mock the outermost boundary you do not own. Never mock the connector's own
methods.**

A test exists to prove that *our* code behaves correctly. If a test replaces one
of the connector's own methods with a mock, it is testing the mock, not the
connector, and it will keep passing even when the real method is broken. Instead,
replace the *external* thing the connector talks to — the HTTP server, the
third-party SDK client, or the network protocol — and let the real connector code
run against it.

Which boundary you mock depends on how the connector reaches the outside world.
Almost every connector falls into one of three categories:

.. list-table::
   :header-rows: 1
   :widths: 22 33 45

   * - Connector type
     - How it calls out
     - How to test it
   * - **HTTP / REST**
     - ``APIConnector`` or ``requests`` directly
     - ``requests_mock`` fixture (mock at the HTTP layer)
   * - **Third-party SDK**
     - Wraps a vendor client object (e.g. ``simple-salesforce``, ``slack_sdk``, ``boto3``)
     - ``mocker`` to replace the client (mock at the SDK boundary)
   * - **Protocol / database**
     - A stateful connection (SMTP, SFTP, DB-API)
     - A fake class implementing the interface

The rest of this guide walks through each one.


*******************
Getting started
*******************

Every connector's tests live in a single directory with a fixed layout:

.. code-block:: text

    test/test_<connector>/
    ├── __init__.py
    ├── conftest.py              # shared fixtures for this connector
    ├── data/                    # canned response payloads (.json, .csv, ...)
    │   └── get_records.json
    └── test_<connector>.py      # the tests

Rules for the layout:

* One directory per connector, named ``test_<connector>``.
* One test module, ``test_<connector>.py``. Split into
  ``test_<connector>_<area>.py`` files only when a single module grows unwieldy.
* Put reusable fixtures in ``conftest.py`` (see `Fixtures and shared setup`_).
* Put large canned payloads in ``data/`` as real ``.json`` / ``.csv`` files (see
  `Test data`_).

Write tests as **plain pytest functions**, not ``unittest.TestCase`` classes. Use
fixtures for setup instead of ``setUp``/``tearDown``. At minimum, add one
`"happy path" <https://en.wikipedia.org/wiki/Happy_path>`_ test per public method,
plus tests for the error handling and edge cases that matter for that method.


***************************
HTTP / REST API connectors
***************************

This is the most common category — any connector built on ``APIConnector`` or
that uses ``requests`` directly. Because those calls go through the ``requests``
library, we mock at the HTTP layer with `requests-mock
<https://requests-mock.readthedocs.io/>`_. This exercises the connector's real
code path *and* the ``APIConnector`` stack — URL building, headers, pagination,
error handling — while intercepting the actual network call.

Use the ``requests_mock`` **pytest fixture** (provided automatically by the
``requests-mock`` package — just add it as a test argument). Do not use the
``@requests_mock.Mocker()`` decorator or the context-manager form in new tests;
the fixture is the pytest-native standard.

A minimal example:

.. code-block:: python

    import json

    import pytest

    from parsons import Mailchimp
    from test.conftest import assert_matching_tables


    @pytest.fixture
    def mailchimp(requests_mock):
        # Mock any auth/handshake the constructor performs, then build the client.
        return Mailchimp(api_key="fake-key-us1")


    def test_get_campaigns(mailchimp, requests_mock, shared_datadir):
        expected = json.loads((shared_datadir / "campaigns.json").read_text())
        requests_mock.get(mailchimp.uri + "campaigns", json=expected)

        tbl = mailchimp.get_campaigns()

        assert tbl.num_rows == 2

What is happening here:

* The ``requests_mock`` fixture stands in as a fake HTTP server for the duration of
  the test. Any request the connector makes that is *not* registered raises
  ``NoMockAddress``, so unexpected calls fail loudly.
* ``requests_mock.get(url, json=...)`` registers a canned response. The mirror
  methods ``post``, ``patch``, ``put``, and ``delete`` register the other verbs.
* Because the fake server is in place, ``mailchimp.get_campaigns()`` runs the real
  connector code but never touches the network.

Assert on **both** sides of the boundary where it matters:

* **Return value** — that the connector parsed the response into the expected
  ``Table`` / dict (use ``assert_matching_tables``).
* **Request** — that the connector called the right URL with the right params or
  body. ``requests_mock`` records this:

  .. code-block:: python

      def test_insert_record(mailchimp, requests_mock):
          requests_mock.post(mailchimp.uri + "lists/abc/members", json={"id": "1"})

          mailchimp.add_member("abc", "a@example.com")

          assert requests_mock.last_request.json() == {
              "email_address": "a@example.com",
              "status": "subscribed",
          }

To simulate API errors, set ``status_code`` (and optionally a JSON error body) and
assert the connector raises or handles it:

.. code-block:: python

    def test_get_campaigns_not_found(mailchimp, requests_mock):
        requests_mock.get(mailchimp.uri + "campaigns", status_code=404)

        with pytest.raises(requests.exceptions.HTTPError):
            mailchimp.get_campaigns()


************************************
Third-party SDK / library connectors
************************************

Some connectors wrap a vendor's Python client (``simple-salesforce``,
``slack_sdk``, ``boto3``, the Google API clients, etc.) rather than calling HTTP
themselves. For these, the boundary we do not own is the **client object**, so we
replace it with a mock using the ``mocker`` fixture from
`pytest-mock <https://pytest-mock.readthedocs.io/>`_.

Build the connector, then swap its client attribute for a ``MagicMock`` and
program the specific methods the code under test will call:

.. code-block:: python

    import pytest

    from parsons import Salesforce


    @pytest.fixture
    def salesforce(mocker):
        sf = Salesforce()
        sf._client = mocker.MagicMock()
        return sf


    def test_query(salesforce):
        salesforce._client.query_all.return_value = {
            "records": [{"Id": "003abc", "value": "FAKE"}],
        }

        response = salesforce.query("FAKE SOQL")

        # 1. The connector returned what we expect...
        assert response["records"][0]["value"] == "FAKE"
        # 2. ...and it called the client the way we expect.
        salesforce._client.query_all.assert_called_with("FAKE SOQL")

The pattern is always:

#. Replace the connector's real client with a ``MagicMock``.
#. Program the return values of the client methods the test will trigger.
#. Call the connector method under test.
#. Assert on the return value **and** on how the client was called.

If the connector constructs its client lazily or from credentials, patch the
constructor at its import site instead:
``mocker.patch("parsons.salesforce.salesforce.SalesforceClient", ...)``.


*******************************
Protocol / database connectors
*******************************

Connectors that speak a stateful protocol — SMTP, SFTP, a DB-API database — are
awkward to mock method-by-method. Prefer a small **fake class** that implements
the same interface and records what it was asked to do. Keep it in a
``fakes.py`` module inside the connector's test directory.

``test/test_databases/fakes.py`` is the reference example:

.. code-block:: python

    from parsons import Table
    from parsons.databases.database_connector import DatabaseConnector


    class FakeDatabase(DatabaseConnector):
        def __init__(self):
            self.copy_call_args = []

        def query(self, sql, parameters=None) -> Table:
            return Table()

        def copy(self, data, table_name, **kwargs):
            # Record the call so the test can assert on it later.
            self.copy_call_args.append({"table_name": table_name, "kwargs": kwargs})

A fake is worth the extra code when the connector drives a multi-step
conversation (connect → act → quit) or when the same fake is reused across many
tests. For a one-off, a ``mocker.MagicMock`` is fine.


***********
Test data
***********

Keep canned data out of the test body so tests stay readable.

* **Large or reused payloads** (a realistic API response, a sample CSV) go in the
  connector's ``data/`` directory as real ``.json`` / ``.csv`` / ``.xml`` files.
  Load them with the ``shared_datadir`` fixture from
  `pytest-datadir <https://github.com/gabrielcnr/pytest-datadir>`_, which copies
  the directory into a temp location per test:

  .. code-block:: python

      def test_get_records(airtable, requests_mock, shared_datadir):
          payload = json.loads((shared_datadir / "records.json").read_text())
          requests_mock.get(airtable.base_uri, json=payload)
          ...

* **Small, single-use values** (a handful of keys) may stay inline in the test as
  a literal dict — roughly 15 lines or fewer. If it is bigger than that, or used
  by more than one test, move it to ``data/``.

Do **not** create large ``*_responses.py`` / ``expected_json.py`` Python modules
of canned data for new connectors — use ``data/`` files instead. Storing payloads
as ``.json`` keeps them language-neutral, diffable, and easy to regenerate from a
real API response.


*************************
Fixtures and shared setup
*************************

Use pytest fixtures, defined in the connector's ``conftest.py``, in place of
``setUp``/``tearDown``:

* A fixture that builds the connector (mocking any auth the constructor performs).
* ``autouse=True`` fixtures for cross-cutting mocks that every test needs — for
  example, replacing an SFTP client or intercepting all requests. See
  ``test/test_catalist/conftest.py`` for an example that mocks ``requests`` for a
  whole connector.

The **root** ``test/conftest.py`` provides helpers available everywhere:

.. code-block:: python

    from parsons import Table
    from test.conftest import assert_matching_tables

    assert_matching_tables(result_table, expected_table)

* ``assert_matching_tables(table1, table2, ignore_headers=False)`` — compare two
  Parsons ``Table`` objects (or dicts) row by row. Use this instead of ``==``,
  which only checks identity.
* ``validate_list(expected_keys, table)`` — assert a ``Table`` has exactly the
  expected columns.
* ``sample_data`` / ``tbl`` — ready-made sample data fixtures.


***********
Live tests
***********

A **live test** hits a real external service with real credentials. These cannot
run in CI (no secrets, no network guarantees), so they are **skipped by default**.
Mark them with ``@pytest.mark.live``:

.. code-block:: python

    @pytest.mark.live
    def test_get_permissions_against_real_api():
        gd = GoogleDrive()  # reads real credentials from the environment
        ...

Run them explicitly with the ``--live`` flag (or ``LIVE_TEST=1``):

.. code-block:: bash

    pytest --live                 # run all live tests
    pytest --live=box             # run only test/test_box live tests
    LIVE_TEST=1 pytest            # equivalent via env var

Live tests **supplement** mocked unit tests; they never replace them. Every public
method still needs a mocked test that runs in CI.


***********
Checklist
***********

Before opening a PR, confirm your connector's tests:

* Live in ``test/test_<connector>/`` with ``__init__.py``, ``conftest.py``, and
  ``test_<connector>.py``.
* Are plain pytest functions using fixtures (no new ``unittest.TestCase``).
* Mock the correct boundary — HTTP (``requests_mock``), SDK client (``mocker``),
  or protocol (a fake) — and never the connector's own methods.
* Cover at least the happy path of every public method, plus key errors.
* Assert on both the return value and how the boundary was called.
* Keep large canned data in ``data/`` (loaded via ``shared_datadir``); only small,
  single-use literals stay inline.
* Mark any credentialed/network tests with ``@pytest.mark.live``.
