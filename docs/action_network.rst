Action Network
==============

********
Overview
********

`Action Network <https://actionnetwork.org/>`_ is an online tool for storing information
and organizing volunteers and donors. It is used primarily for digital organizing and event mangement. For more information, see `Action Network developer docs <https://actionnetwork.org/docs>`_, `SQL Mirror developer docs <https://actionnetwork.org/mirroring/docs>`_

.. note::

  Authentication
    Only ActionNetwork accounts of the partner tier are able to access their API. You can generate your key from the API & Sync page, located in the *Start Organizing* menu, under *Details*.

***********
Quick Start
***********

To instantiate a class, you can either pass in the API token as an argument or set the ``AN_API_TOKEN`` environmental variable.

.. code-block:: python

   from parsons import ActionNetwork

   # First approach: Use API credentials via environmental variables
   an = ActionNetwork()

   # Second approach: Pass API credentials as arguments
   an = ActionNetwork(api_token='MY_API_TOKEN')

You can then call various endpoints:

.. code-block:: python

    # List all people stored in Action Network
    all_contacts = an.get_people()

    # Add a person
    an.add_person('person.email@fakeemail.com')

    # Add a tag
    an.add_tag('fake_tag')

    # Update a person
    an.update_person('fake_id', given_name='new_given_name', tags=['tag_1', 'tag_2'])

    # Get all taggings associated with a specific tag
    all_taggings = an.get_taggings('tag_id')

    # Get a specific tagging
    specific_tagging = an.get_tagging('tag_id', 'tagging_id')

    # Create a tagging
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
      "item_type": "osdi:person"
    }

    # Delete a tagging
    an.delete_tagging('tag_id', 'tagging_id')

    # Get all wrappers
    all_wrappers = an.get_wrappers()

    # Get a specific wrapper
    specific_wrapper = an.get_wrapper('wrapper_id')

    # Get all surveys
    all_surveys = an.get_surveys()

    # Get a specific survey
    specific_survey = an.get_survey('survey_id')

    # Create a survey
    survey_payload = {
        "title": "My Free Survey",
        "origin_system": "FreeSurveys.com"
    }
    created_survey = an.create_survey(survey_payload)

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

    # Update a survey
    updated_survey = an.update_survey('survey_id', survey_payload)

***********
SQL Mirror
***********

.. code-block:: python

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

    # Use the function to query through SSH
    result = query_through_ssh(
        ssh_host, ssh_port, ssh_username, ssh_password,
        db_host, db_port, db_name, db_username, db_password, query
    )

    # Output the result
    print(result)

***
API
***
.. autoclass:: parsons.action_network.action_network.ActionNetwork
   :inherited-members:
   :members:
   