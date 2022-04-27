==================================
Introduction to ETL Best Practices
==================================

This training guide will walk you through some basic ETL workflows using Parsons. It is based off of a two-part training designed by Cormac Martinez del Rio of The Movement Cooperative.

It introduces the basic concepts behind the Extract, Transform and Load (ETL) process by working through two examples. First, we focus on how to write a basic Parsons script that moves data between one platform (Mobilize) and another (Google Sheets). Then, we introduce some more advanced concepts such as data warehouses, platforms like Civis, and the use of log tables and schedulers to make your workflow easier to run and debug.

You can suggest improvements to this guide or request additional guides by filing an issue in our issue tracker or telling us in Slack. To get added to our Slack, and/or to request access to the recordings of this training, email us at *engineering@movementcooperative.org*.

^^^^^^^^^^^^
Introduction
^^^^^^^^^^^^

- What is ETL?
- Our example use case.
- Link to scripts we're using on Github.

^^^^^^^^^^^^^^
Authentication
^^^^^^^^^^^^^^

In order to access our data from Mobilize and add it to Google Sheets, we need to authenticate ourselves to these two services. We do this by getting the relevant credentials from the platform and then saving them to specific environmental variables.

Each Parsons connector has a page in the documentation, and at the top of each page is a description of what credentials you need and how to get them. Sometimes this is straightforward, and sometimes it's more complicated.

########
Mobilize
########

To access Mobilize, you'll need to get an API key by contacting a support representative. If you don't have an account but would like to follow along anyway, we've provided some fake Mobilize data which we'll walk you through accessing below.

If you were able to get an API key, you can now save it as the environmental variable ``MOBILIZE_AMERICA_API_KEY`` by running this command on the command line::

    set MOBILIZE_AMERICA_API_KEY=$API_KEY       # Windows
    export MOBILIZE_AMERICA_API_KEY=$API_KEY    # Linux/Mac

(Not comfortable with the command line? Check out our `training guide <getting_set_up.html>`_.)

And that's it, you're done! When you instantiate the Mobilize connector, it will look in the environment for ``MOBILIZE_AMERICA_API_KEY``. If it finds the key, it can use it to handle all the authentication for you.

.. note::

    What do we mean, "when you instantiate the Mobilize connector"? We've created the Mobilize connector class, which has general features anyone can use to work with Mobilize. But in order to actually work with that class, you need to create a "instance" of it. That instance will have data specific to you, such as your API key.

    "Instantiation" is just a fancy way to say "create an instance of". In Python, you instantiate something by calling it with parentheses, ie: ``mobilize_instance = Mobilize()``.

#############
Google Sheets
#############

Setting up the Google Sheets connector takes several steps.

First, you'll need to go to the `Google Developers Console <https://console.cloud.google.com/>`_ and select the project you want to work with, or create a new one (recommended). Following `these instructions from Google <https://developers.google.com/drive/api/guides/enable-drive-api>`_, click **APIs & Auth** and then **APIs**. Select the Drive API from among the API options, and click **enable**.

Once you've created a project and enabled the API, you'll need to get the credentials that will allow you to access the API. Click on the **credentials** option in the left sidebar. Click **create credentials** and select the **Service Account** option. Once you have filled out the form and clicked submit, it will give you a set of credentials as a json string which you can save to a file.

Now we need to tell Parsons where it can find the credentials. We'll set an environmental variable ``GOOGLE_DRIVE_CREDENTIALS`` which is the path to where your credentials are stored (replace the paths below with your correct paths)::

    set GOOGLE_DRIVE_CREDENTIALS="C:\Home\Projects\"      # Windows
    export GOOGLE_DRIVE_CREDENTIALS="/home/projects/"     # Linux/Mac


Learn more about paths :ref:`here <path-explainer>`.

Finally, look inside the credentials file for an email address in the field ``client_email``. It will look something like ``service-account@projectname-123456.iam.gserviceaccount.com``. Go to the Google Drive UI for the folder you want to work with and share the folder with this email address.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Extracting Data from Moblize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#################################
Setting up: Imports and Instances
#################################

Before we jump into moving data around, lets import all the things we need and instantiate our connectors.

Your imports should look like this::

    import json
    from datetime import datetime
    from parsons import Table, MobilizeAmerica, GoogleSheets

"json" is a Python module that helps us convert between data in a JSON format (which is a popular way to store and share data) and Python data structures.

"datetime" is a Python module that helps us work more easily with dates and times.

Finally, from Parsons, we're importing the two connectors we're using, plus the Parsons Table object. The Parsons Table is the core data structure in Parsons. It's a standardized way to hold data, which makes it very easy to move data between vendors even if the vendors have different structures.

We instantiate our connectors with this code::

    mobilize = MobilizeAmerica()
    google_sheets = GoogleSheets()

And we're ready to start extracting!

##########
Extracting
##########

We're going to extract some data on attendance from Mobilize. We can do that with this code::

    attendance_records = mobilize.get_attendances()

If you weren't able to get an authenticated Mobilize account, you can use the fake Mobilize data in `this google sheet <https://docs.google.com/spreadsheets/d/1YZr6gXmptxfzqb_t58frwNHhVu_KMTQzvMpnNUZd47I/>`_::

    spreadsheet_id = "1YZr6gXmptxfzqb_t58frwNHhVu_KMTQzvMpnNUZd47I"
    attendance_records = google_sheets.get_worksheet(spreadsheet_id)

And...that's it! We've got our data. Let's take a look at what we've extracted::

    print(attendance_records)

The result should look like this::

    {'id': '46273', 'event_id': '454545', 'event_title': 'January Canvass', 'timeslot_id': '738375', 'timeslot_start_date': '1642865400', 'timeslot_end_date': '1642872600', 'status': 'REGISTERED', 'attended': 'true', 'person': '{"id": 1, "given_name": "Lou", "family_name": "Slainey", "email_address": "lslainey0@unicef.org", "phone_number": "3271326753", "postal_code": "78737"}'}
    {'id': '46274', 'event_id': '454546', 'event_title': 'January Textbank', 'timeslot_id': '239573', 'timeslot_start_date': '1643563800', 'timeslot_end_date': '1643527800', 'status': 'REGISTERED', 'attended': 'true', 'person': '{"id": 2, "given_name": "Arleyne", "family_name": "Ransfield", "email_address": "aransfield1@qq.com", "phone_number": "2174386332", "postal_code": "78737"}'}
    {'id': '46275', 'event_id': '454547', 'event_title': 'February Canvass', 'timeslot_id': '183743', 'timeslot_start_date': '1644939000', 'timeslot_end_date': '1644946200', 'status': 'REGISTERED', 'attended': 'true', 'person': '{"id": 3, "given_name": "Alameda", "family_name": "Blackmuir", "email_address": "ablackmuir2@wisc.edu", "phone_number": "3844977654", "postal_code": "78737"}'}
    {'id': '46276', 'event_id': '454548', 'event_title': 'February Phonebank', 'timeslot_id': '283666', 'timeslot_start_date': '1645378200', 'timeslot_end_date': '1645342200', 'status': 'REGISTERED', 'attended': 'true', 'person': '{"id": 4, "given_name": "Bondie", "family_name": "Berrow", "email_address": "bberrow3@discuz.net", "phone_number": "2275080414", "postal_code": "78737"}'}
    {'id': '46277', 'event_id': '454549', 'event_title': 'March Relational Organizing Hour', 'timeslot_id': '477483', 'timeslot_start_date': '1648218600', 'timeslot_end_date': '1648225800', 'status': 'REGISTERED', 'attended': 'true', 'person': '{"id": 5, "given_name": "Korrie", "family_name": "Spight", "email_address": "kspight4@sakura.ne.jp", "phone_number": "9818241063", "postal_code": "78737"}'}
     ...

There are more than four rows in this table, but ``print`` only displays the first five rows by default, for readability's sake.

As you can see, this data corresponds to what's in the Google sheet. We display the data in what looks like a nested Parsons dictionary, with the column names as keys and the actual contents of each cell as the values. You can ask for any row of a Parsons Table as a dictionary::

    print(attendance_records[0])
    >> {'id': '46273', 'event_id': '454545', 'event_title': 'January Canvass', 'timeslot_id': '738375', 'timeslot_start_date': '1642865400', 'timeslot_end_date': '1642872600', 'status': 'REGISTERED', 'attended': 'true', 'person': '{"id": 1, "given_name": "Lou", "family_name": "Slainey", "email_address": "lslainey0@unicef.org", "phone_number": "3271326753", "postal_code": "78737"}'}

You can also get any column of a Parsons Table as a list of values::

    print(attendance_records["event_title"])
    >> ['January Canvass', 'January Textbank', 'February Canvass', 'February Phonebank', 'March Relational Organizing Hour' ...

Because individual rows are treated as dictionaries, and individual columns as list, that makes it easy to iterate over them with a for loop::

    for index, attendance in enumerate(attendance_records):
        print(attendance['person'])

There are also a couple of convenience methods for getting the total number of rows and the list of column names::

    attendance_records.num_rows
    attendance_records.columns


<see actual sample script on Github to see what should go here>

Digression: what is a Parsons table?
- you can access petl functions on parsons table
- those functions will return a *petl* table, so use table() to convert from petl to table
- Mention why petl instead of pandas

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Transforming Data with Parsons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- convert columns
- select rows
<again, see actual sample script for details>

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Loading Data to Google Sheets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

<again, see actual sample script for details>

^^^^^^^^^^^^^^^^^^^^^^
Using a Data Warehouse
^^^^^^^^^^^^^^^^^^^^^^

- limitations of just running a script from your laptop
- introduce data warehouse, introduce civis, etc
- see agenda doc + slides for details

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
New Example: Mobilize --> Civis/Redshift --> Action Network
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Extracting Data from Moblize Into Warehouse
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Transforming Mobilize Data in Warehouse with SQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Load Data from Warehouse to Action Network
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**********
Log Tables
**********

^^^^^^^^^^^^^^^
Scheduling Jobs
^^^^^^^^^^^^^^^