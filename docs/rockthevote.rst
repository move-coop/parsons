#############
Rock the Vote
#############

Overview
========

`Rock the Vote <https://www.rockthevote.org/>`__ is an online registration tool. This Parsons connector makes use of
Rock the Vote's `Rocky API <https://rock-the-vote.github.io/Voter-Registration-Tool-API-Docs/>`__.

.. admonition:: Authentication

   In order to authenticate with the API, users must specify the ID and API key of the RTV partner organization for the data.

Quickstart
==========

To use the :class:`~parsons.rockthevote.rtv.RockTheVote` class you can either store the partner ID and API key as an
environmental variable (``RTV_PARTNER_ID`` and ``RTV_PARTNER_API_KEY``, respectively), or you can
pass them in as arguments to the class.

.. code-block:: python
   :caption: If credentials are specified as environment variables, no need to pass them in

   from parsons import RockTheVote
   rtv = RockTheVote()

.. code-block:: python
   :caption: Pass credentials directly

   from parsons import RockTheVote
   rtv = RockTheVote(partner_id='123', partner_api_key='supersecretkey')

To fetch a list of registrations submitted for the partner ID, use the
:meth:`~parsons.rockthevote.rtv.RockTheVote.run_registration_report`
method. It is possible to filter the results by providing a parameter to specify a start date
for the registrations.

.. code-block:: python
   :caption: Get list of registrations since a specific date

   registrants = rtv.run_registration_report(since='2020-01-01')

The :meth:`~parsons.rockthevote.rtv.RockTheVote.run_registration_report` will block as the report
is being generated and downloaded from the Rocky API. For larger reports, this can take a long time.
If you have other things you want to do while the report is running,
you can break up the creation of the report from the fetching of the data.

.. code-block:: python
   :caption: Create report of registrations since a specific date -- get report ID

   report_id = rtv.create_registration_report(since='2020-01-01')

.. code-block:: python
   :caption: Get the registration report

   registrants = rtv.get_registration_report(report_id)

API
====

.. autoclass:: parsons.rockthevote.rtv.RockTheVote
   :inherited-members:
   :members:

.. autoexception:: parsons.rockthevote.rtv.RTVFailure
   :inherited-members:
   :members:
