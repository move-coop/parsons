##############
Action Network
##############

Overview
========

`Action Network <https://actionnetwork.org/>`__ is an online tool for storing information
and organizing volunteers and donors. It is used primarily for digital organizing and event mangement.
For more information, see `Action Network developer docs <https://actionnetwork.org/docs>`__,
`SQL Mirror developer docs <https://actionnetwork.org/mirroring/docs>`__.

.. admonition:: Authentication

   Only ActionNetwork accounts of the partner tier are able to access their API.
   You can generate your key from the API & Sync page, located in the *Start Organizing* menu, under *Details*.

Quickstart
==========

To instantiate :class:`~parsons.action_network.action_network.ActionNetwork`,
you can either pass in the API token as an argument
or set the ``AN_API_TOKEN`` environmental variable.

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import ActionNetwork
   an = ActionNetwork()

.. code-block:: python
   :caption: Pass API credentials as arguments

   from parsons import ActionNetwork
   an = ActionNetwork(api_token='MY_API_TOKEN')

You can then call various endpoints:

.. code-block:: python
   :caption: List all people stored in Action Network

   all_contacts = an.get_people()

.. code-block:: python
   :caption: Add a person

   an.add_person('person.email@fakeemail.com')

.. code-block:: python
   :caption: Add a tag

   an.add_tag('fake_tag')

.. code-block:: python
   :caption: Update a person

   an.update_person('fake_id', given_name='new_given_name', tags=['tag_1', 'tag_2'])

.. code-block:: python
   :caption: Get all taggings associated with a specific tag

   all_taggings = an.get_taggings('tag_id')

.. code-block:: python
   :caption: Get a specific tagging

   specific_tagging = an.get_tagging('tag_id', 'tagging_id')

.. code-block:: python
   :caption: Create a tagging

   tagging_payload = {
      "_links" : {
      "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/123" }
      }
   }
   created_tagging = an.create_tagging('tag_id', tagging_payload)

   # Result
   created_tagging = {
      "_links": {
         "self": {
            "href": "https://actionnetwork.org/api/v2/tags/123/taggings/123"
         },
         "osdi:tag": {
            "href": "https://actionnetwork.org/api/v2/tags/123"
         },
         "osdi:person": {
            "href": "https://actionnetwork.org/api/v2/people/123"
         },
         "curies": [
            {
               "name": "osdi",
               "href": "https://actionnetwork.org/docs/v2/{rel}",
               "templated": true
            },
            {
               "name": "action_network",
               "href": "https://actionnetwork.org/docs/v2/{rel}",
               "templated": true
            }
         ]
      },
      "identifiers": [
         "action_network:123"
      ],
      "created_date": "2014-03-18T22:25:31Z",
      "modified_date": "2014-03-18T22:25:38Z",
      "item_type": "osdi:person",
   }

.. code-block:: python
   :caption: Delete a tagging

   an.delete_tagging('tag_id', 'tagging_id')

.. code-block:: python
   :caption: Get all wrappers

   all_wrappers = an.get_wrappers()

.. code-block:: python
   :caption: Get a specific wrapper

   specific_wrapper = an.get_wrapper('wrapper_id')

.. code-block:: python
   :caption: Get all surveys

   all_surveys = an.get_surveys()

.. code-block:: python
   :caption: Get a specific survey

   specific_survey = an.get_survey('survey_id')

.. code-block:: python
   :caption: Create a survey

   created_survey = {
      "identifiers": [
         "action_network:1234"
      ],
      "created_date": "2014-03-26T15:26:30Z",
      "modified_date": "2014-03-26T15:26:30Z",
      "title": "My Free Survey",
      "total_responses": 0,
      "origin_system": "FreeSurveys.com",
      "action_network:hidden": false,
      "_embedded": {
         "osdi:creator": {
         "given_name": "John",
         "family_name": "Doe",
         "created_date": "2014-03-20T21:04:31Z",
         "modified_date": "2014-03-20T21:04:31Z",
         "identifiers": [
            "action_network:1234"
         ],
         "email_addresses": [
            {
               "primary": true,
               "address": "jdoe@mail.com",
               "status": "subscribed"
            }
         ],
         "phone_numbers": [
            {
               "primary": true,
               "number": "12021234444",
               "number_type": "Mobile",
               "status": "subscribed"
            }
         ],
         "postal_addresses": [
            {
               "primary": true,
               "address_lines": [
                   "1600 Pennsylvania Ave"
               ],
               "locality": "Washington",
               "region": "DC",
               "postal_code": "20009",
               "country": "US",
               "language": "en",
               "location": {
                  "latitude": 32.249,
                  "longitude": -73.0339,
                  "accuracy": "Approximate"
               }
            }
         ],
         "languages_spoken": [
            "en"
         ],
         "_links": {
            "self": {
               "href": "https://actionnetwork.org/api/v2/people/1234"
            },
            "osdi:attendances": {
               "href": "https://actionnetwork.org/api/v2/people/1234/attendances"
            },
            "osdi:signatures": {
               "href": "https://actionnetwork.org/api/v2/people/1234/signatures"
            },
            "osdi:submissions": {
               "href": "https://actionnetwork.org/api/v2/people/1234/submissions"
            },
            "osdi:donations": {
               "href": "https://actionnetwork.org/api/v2/people/1234/donations"
            },
            "osdi:outreaches": {
               "href": "https://actionnetwork.org/api/v2/people/1234/outreaches"
            },
            "osdi:taggings": {
               "href": "https://actionnetwork.org/api/v2/people/1234/taggings"
            },
            "action_network:responses": {
               "href": "https://actionnetwork.org/api/v2/people/1234/responses"
            },
            "curies": [
               {
                  "name": "osdi",
                  "href": "https://actionnetwork.org/docs/v2/{rel}",
                  "templated": true
               },
               {
                  "name": "action_network",
                  "href": "https://actionnetwork.org/docs/v2/{rel}",
                  "templated": true
               }
            ]
         }
      },
      "_links": {
         "osdi:creator": {
            "href": "https://actionnetwork.org/api/v2/people/1234"
         },
         "self": {
            "href": "https://actionnetwork.org/api/v2/surveys/1234"
         },
         "action_network:responses": {
            "href": "https://actionnetwork.org/api/v2/surveys/1234/responses"
         },
         "action_network:record_response_helper": {
            "href": "https://actionnetwork.org/api/v2/surveys/1234/responses"
         },
         "action_network:embed": {
            "href": "https://actionnetwork.org/api/v2/surveys/1234/embed"
         },
         "curies": [
            {
               "name": "osdi",
               "href": "https://actionnetwork.org/docs/v2/{rel}",
               "templated": true
            },
            {
               "name": "action_network",
               "href": "https://actionnetwork.org/docs/v2/{rel}",
               "templated": true
            }
         ]
      }
   }

.. code-block:: python
   :caption: Update a survey

   updated_survey = an.update_survey('survey_id', survey_payload)

SQL Mirror
==========

.. code-block:: python
   :caption: Query through SSH

   from parsons.utilities.ssh_utilities import query_through_ssh

   # Define SSH and database parameters
   ssh_host = 'ssh.example.com'
   ssh_port = 22
   ssh_username = 'user'
   ssh_password = 'pass'
   db_host = 'db.example.com'
   db_port = 5432
   db_name = 'testdb'
   db_username = 'dbuser'
   db_password = 'dbpass'
   query = 'SELECT * FROM table'

   result = query_through_ssh(
       ssh_host, ssh_port, ssh_username, ssh_password,
       db_host, db_port, db_name, db_username, db_password, query
   )

   # Output the result
   print(result)

API
====

.. autoclass:: parsons.action_network.action_network.ActionNetwork
   :inherited-members:
   :members:

.. _ActionNetwork Advocacy campaigns Documentation: https://actionnetwork.org/docs/v2/advocacy_campaigns
.. _ActionNetwork Attendances Documentation: https://actionnetwork.org/docs/v2/attendances
.. _ActionNetwork Campaigns Documentation: https://actionnetwork.org/docs/v2/campaigns
.. _ActionNetwork Custom fields Documentation: https://actionnetwork.org/docs/v2/custom_fields
.. _ActionNetwork Donations Documentation: https://actionnetwork.org/docs/v2/donations
.. _ActionNetwork Embeds Documentation: https://actionnetwork.org/docs/v2/embed
.. _ActionNetwork Event Campaigns Documentation: https://actionnetwork.org/docs/v2/event_campaigns
.. _ActionNetwork Events Documentation: https://actionnetwork.org/docs/v2/events
.. _ActionNetwork Forms Documentation: https://actionnetwork.org/docs/v2/forms
.. _ActionNetwork Fundraising Pages Documentation: https://actionnetwork.org/docs/v2/fundraising_pages
.. _ActionNetwork Items Documentation: https://actionnetwork.org/docs/v2/items
.. _ActionNetwork Lists Documentation: https://actionnetwork.org/docs/v2/lists
.. _ActionNetwork Messages Documentation: https://actionnetwork.org/docs/v2/messages
.. _ActionNetwork Schedule helper Documentation: https://actionnetwork.org/docs/v2/schedule_helper
.. _ActionNetwork Send helper Documentation: https://actionnetwork.org/docs/v2/send_helper
.. _ActionNetwork Metadata Documentation: https://actionnetwork.org/docs/v2/metadata
.. _ActionNetwork Outreaches Documentation: https://actionnetwork.org/docs/v2/outreaches
.. _ActionNetwork People Documentation: https://actionnetwork.org/docs/v2/people
.. _ActionNetwork Person Signup Helper Documentation: https://actionnetwork.org/docs/v2/person_signup_helper
.. _ActionNetwork Background Processing Documentation: https://actionnetwork.org/docs/v2/#background-processing
.. _ActionNetwork Petitions Documentation: https://actionnetwork.org/docs/v2/petitions
.. _ActionNetwork Queries Documentation: https://actionnetwork.org/docs/v2/queries
.. _ActionNetwork Signatures Documentation: https://actionnetwork.org/docs/v2/signatures
.. _ActionNetwork Submissions Documentation: https://actionnetwork.org/docs/v2/submissions
.. _ActionNetwork Surveys Documentation: https://actionnetwork.org/docs/v2/surveys
.. _ActionNetwork Tags Documentation: https://actionnetwork.org/docs/v2/tags
.. _ActionNetwork Taggings Documentation: https://actionnetwork.org/docs/v2/taggings
.. _ActionNetwork Wrappers Documentation: https://actionnetwork.org/docs/v2/wrappers
.. _ActionNetwork Unique ID Lists Documentation: https://actionnetwork.org/docs/v2/unique_id_lists
