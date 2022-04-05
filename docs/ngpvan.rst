NGPVAN
======


********
Overview
********

The VAN module leverages the VAN API and generally follows the naming convention of their API endpoints. It
is recommended that you reference their `API documentation <https://docs.ngpvan.com/reference/overview>`_ for
additional details and information.

.. note::
   API Keys
      - API Keys are specific to each committee and state.
      - There is a Parsons type API Key that can be requested via the Integrations menu on the main page.
      	If you have an issue gaining access to this key, or an admin has questions, please email
	<parsons@movementcooperative.org>.


.. warning::
   VANIDs
      VANIDs are unique to each state and instance of the VAN. VANIDs used for the AV VAN **will not** match
      those of the SmartVAN or VoteBuilder.
      
   Maintenance & Support
      VAN/EveryAction is not responsible for support of Parsons. Their support team cannot answer questions
      about Parsons. Please direct any questions to the Parsons team via the issue tracker or Slack.

.. toctree::
	:maxdepth: 1

**********
QuickStart
**********

To call the VAN class you can either store the api key as an environmental variable VAN_API_KEY or pass it in as an argument.

.. code-block:: python

  from parsons import VAN

   van = VAN(db='MyVoters') # Specify the DB type and pass api key via environmental variable.

   van = VAN(api_key='asdfa-sdfadsf-adsfasdf',db='MyVoters') # Pass api key directly

You can then call various endpoints:

.. code-block:: python

  from parsons import VAN

   van = VAN(db='MyVoters')

   # List events with a date filter
   events = van.get_events(starting_before='2018-02-01')

   # List all folders shared with API Key User
   folders = van.get_folders()

   # Return to a Redshift database
   saved_lists = van.get_saved_lists().to_redshift('van.my_saved_lists')

This a is just a small sampling of all of the VAN endpoints that you can leverage. We recommend reviewing the
documentation for all functions.

****************
Common Workflows
****************

===========
Bulk Import
===========
For some methods, VAN allows you to bulk import multiple records to create or modify them.

The bulk upload endpoint requires access to files on the public internet as it runs the upload
asynchronously. Therefore, in order to bulk import, you must pass in cloud storage credentials
(either AWS S3 or Google Cloud Storage) so that the file can be posted.

**Bulk Apply Activist Codes**

In this example we are applying activist codes to a list of contacts. The csv file would
have the following columns:

  * ``vanid``
  * ``activistcodeid``

.. code-block:: python

   from parsons import VAN, Table

   van = VAN(db='EveryAction')

   # Load a table containing the VANID, activistcodeid and other options.
   tbl = Table.from_csv('new_volunteers.csv')

   # Table will be sent to S3 bucket and a POST request will be made to VAN creating
   # the bulk import job with all of the valid meta information. The method will
   # return the job id.
   job_id = van.bulk_apply_activist_codes(tbl, url_type="S3", bucket='my_bucket')

   # The bulk import job is run asynchronously, so you may poll the status of a job.
   job_status = van.get_bulk_import_job(job_id)


** Bulk Upsert Contacts**
In this example we are creating and updating emails and addresses. The csv file would
have the following columns:

* ``vanid``
* ``first_name``
* ``last_name``
* ``address``
* ``city``
* ``state``
* ``zip``
* ``email``

Note that ``vanid`` must be the first column in your table. For additional fields, see the
:func:`~parsons.ngpvan.van.BulkImport.bulk_upsert_contacts` documentation.

If a record contains a null value, it will not be updated.

If the VANID record is null, then a new record will be created.

.. code-block:: python

    from parsons import VAN, Table

    van = VAN(db=EveryAction)

    # Load a table containing VANID and PII columns
    tbl = Table.from_csv('hot_leads.csv')

    # Table will be sent to S3 bucket and a POST request will be made to VAN creating
    # the bulk import job with all of the valid meta information. The method will
    # return the job id.
    job_id = van.bulk_upsert_contacts(tbl, url_type="S3", bucket='my_bucket')

    # The bulk import job is run asynchronously, so you may poll the status of a job.
    job_status = van.get_bulk_import_job(job_id)

    # When the job is complete, get the results of the job. This file will include newly
    # created vanids.
    job_results = van.get_bulk_import_job_results(job_id)

**Upload Saved List**

.. code-block:: python

   from parsons import VAN, Table

   van = VAN(db='MyVoters')

   # Load a table containing VANIDs
   tbl = Table.from_csv('gcs_test.csv')

   # The destination folder id. You can get a list of folder ids by running the
   # VAN.get_folders() method. Remember to share the folder with your API user
   # or you will not be able to access it.
   folder_id = 1171

   # The destination list name
   list_name = 'My Winning List v1.0'

   # The cloud storage service and kwargs specific to GCS.
   url_type = 'GCS'
   bucket_name = 'my_bucket'
   app_creds = 'my_creds.json' # Not required if stored as env variable.

   van.upload_saved_list(tbl, list_name, folder_id, url_type, replace=true,
                         bucket_name=bucket_name, app_creds=app_creds)

============================
Scores: Loading and Updating
============================

Loading a score is a multi-step process. Once a score is set to approved, loading takes place overnight.

**Standard Auto Approve Load**

.. code-block:: python

   from parsons import VAN, Table

   van = VAN(db='MyVoters') # API key stored as an environmental variable

   # If you don't know the id, you can run van.get_scores() to list the
   # slots that are available and their associated score ids.
   score_id = 9999

   # Load the Parsons table with the scores. The first column of the table
   # must be the person id (e.g. VANID). You could create this from Redshift or
   # another source.
   tbl = Table.from_csv('winning_scores.csv')

   # Specify the score id slot and the column name for each score.
   config = [{'score_id': score_id, 'score_column': 'winning_model'}]

   # If you have multiple models in the same file, you can load them all at the same time.
   # In fact, VAN recommends that you do so to reduce their server loads.
   config = [{'score_id': 5555, 'score_column': 'score1'}, {'score_id': 5556, 'score_column': 'score2'}]

   # The score file must posted to the internet. This configuration uses S3 to do so. In this
   # example, your S3 keys are stored as environmental variables. If not, you can pass them
   # as arguments.
   job_id = van.upload_scores(tbl, config, url_type='S3', email='info@tmc.org', bucket='tmc-fake')

**Standard Load Requiring Approval**

.. code-block:: python

   from parsons import VAN

   van = VAN(db='MyVoters') # API key stored as an environmental variable
   config = [{'score_id': 3421, 'score_column': 'winning_model'}]

   # Note that auto_approve is set to False. This means that you need to manually approve
   # the job once it is loaded.
   job_id = van.upload_scores(tbl, config, url_type='S3', email='info@tmc.org',
                              bucket='tmc-fake', auto_approve=False)

   # Approve the job
   van.update_score_status(job_id,'approved')

===========================
People: Add Survey Response
===========================
The following workflow can be used to apply survey questions, activist codes
and canvass responses.

.. code-block:: python

   from parsons import VAN

   # Instantiate Class
   van = VAN(db="MyVoters")

   van_id = 13242
   sq = 311838 # Valid survey question id
   sr = 1288926 # Valid survey response id
   ct = 36 # Valid contact type id
   it = 4 # Valid input type id

   # Create a valid survey question response
   van.apply_survey_response(vanid, sq, sr, contact_type_id=ct, input_type_id=it)

=============================
Event: Creating and Modifying
=============================

Events are made up of sub objects that need to exist to create an event

* Event Object - The event itself
* Event Type - The type of event, such as a `Canvass` or `Phone Bank`. These are created
  in the VAN UI and can be reused for multiple events.
* Locations - An event can have multiple locations. While not required to initially create an
  event, these are required to add signups to an event.
* Roles - The various roles that a person can have at an event, such as ``Lead`` or
  ``Canvasser``. These are set as part of the event type.
* Shifts - Each event can have multiple shits in which a person can be assigned. These are
  specified in the event creation.

.. code-block:: python

  from parsons import VAN

  # Instantiate class
  van = VAN(db="EveryAction")

  # Create A Location
  loc_id = van.location(name='Big `Ol Canvass', address='100 W Washington', city='Chicago', state='IL')

  # Create Event
  name = 'GOTV Canvass' # Name of event
  short_name = 'GOTVCan' # Short name of event, 12 chars or less
  start_time = '2018-11-01T15:00:00' # ISO formatted date
  end_time = '2018-11-01T18:00:00' # ISO formatted date after start time
  event_type_id = 296199 # A valid event type id
  roles = [259236] # A list of valid role ids
  location_ids = [loc_id] # An optional list of locations ids for the event
  description = 'CPD Super Volunteers Canvass' # Optional description of 200 chars or less
  shifts = [{'name': 'Shift 1',
             'start_time': '2018-11-01T15:00:00',
             'end_time': '2018-11-11T17:00:00'}] # Shifts must fall within event start/end time.

  new_event = van.event_create(name, short_name, start_time, end_time, event_type_id, roles,
                               location_ids=location_ids, shifts=shifts, description=description)


============================
Signup: Adding and Modifying
============================

.. code-block:: python

  from parsons import VAN

  # Instantiate class
  van = VAN(db="EveryAction")

  # Create a new signup

  vanid = 100349920
  event_id = 750001004
  shift_id = 19076
  role_id = 263920
  location_id = 3
  role_id = 263920
  status_id = 11

  # Create the signup. Will return a signup id
  signup_id  = van.signup_create(vanid, event_id, shift_id, role_id, status_id, location_id

  # Modify a status of the signup
  new_status_id = 6
  van.signup_update(signup_id, status_id=new_status_id)

***
API
***

======
People
======
.. autoclass:: parsons.ngpvan.van.People
   :inherited-members:

==============
Activist Codes
==============
.. autoclass:: parsons.ngpvan.van.ActivistCodes
   :inherited-members:

===========
Bulk Import
===========
.. autoclass:: parsons.ngpvan.van.BulkImport
   :inherited-members:

=================
Canvass Responses
=================
.. autoclass:: parsons.ngpvan.van.CanvassResponses
   :inherited-members:

================
Changed Entities
================
.. autoclass:: parsons.ngpvan.van.ChangedEntities
   :inherited-members:

=====
Codes
=====
.. autoclass:: parsons.ngpvan.van.Codes
   :inherited-members:

=============
Custom Fields
=============
.. autoclass:: parsons.ngpvan.van.CustomFields
   :inherited-members:

======
Events
======
.. autoclass:: parsons.ngpvan.van.Events
   :inherited-members:

===========
Export Jobs
===========
.. autoclass:: parsons.ngpvan.van.ExportJobs
   :inherited-members:

=================
File Loading Jobs
=================
.. autoclass:: parsons.ngpvan.van.FileLoadingJobs
   :inherited-members:

=======
Folders
=======
.. note::
   A folder must be shared with the user associated with your API key to
   be listed.

.. autoclass:: parsons.ngpvan.van.Folders
   :inherited-members:

=========
Locations
=========
.. autoclass:: parsons.ngpvan.van.Locations
   :inherited-members:

===========
Saved Lists
===========
.. note::
   A saved list must be shared with the user associated with your API key to
   be listed.

.. autoclass:: parsons.ngpvan.van.SavedLists
   :inherited-members:

======
Scores
======
Prior to loading a score for the first time, you must contact VAN support to request
a score slot.

.. note::
  Score Auto Approval
    Scores can be automatically set to ``approved`` through the :meth:`VAN.upload_scores`
    method allowing you to skip calling :meth:`VAN.update_score_status`, if the average of
    the scores is within the fault tolerance specified by the user. It is only available
    to API keys with permission to automatically approve scores.


.. autoclass:: parsons.ngpvan.van.Scores
   :inherited-members:

=======
Signups
=======
.. autoclass:: parsons.ngpvan.van.Signups
   :inherited-members:

================
Supporter Groups
================
.. autoclass:: parsons.ngpvan.van.SupporterGroups
   :inherited-members:

================
Survey Questions
================
.. autoclass:: parsons.ngpvan.van.SurveyQuestions
   :inherited-members:

=======
Targets
=======
.. autoclass:: parsons.ngpvan.van.Targets
   :inherited-members:
