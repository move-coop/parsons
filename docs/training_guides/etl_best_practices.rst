===============================================
Introduction to ETL Best Practices With Parsons
===============================================

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

****************************
Getting Relevant Credentials
****************************

Each Parsons connector has a page in the documentation, and at the top of each page is a description of what credentials you need and how to get them. Sometimes this is straightforward, and sometimes it's more complicated.

**Mobilize**

To access Mobilize, you'll need to get an API key by contacting a support representative. If you don't have an account but would like to follow along anyway, we've provided some fake Mobilize data which we'll walk you through accessing below.

If you were able to get an API key, you can now save it as an environmental variable `MOBILIZE_AMERICA_API_KEY` by running this command on the command line::

    set MOBILIZE_AMERICA_API_KEY=$API_KEY       # Windows
    export MOBILIZE_AMERICA_API_KEY=$API_KEY    # Linux/Mac

(Not comfortable with the command line? Check out our <Getting Set Up Guide>.)

And that's it, you're done! When you instantiate the Mobilize connector, it will look in the environment for `MOBILIZE_AMERICA_API_KEY`. If it finds the key, it can use it to handle all the authentication for you.

..note::

    What do we mean, "when you instantiate the Mobilize connector"? We've created the Mobilize connector class, which has general features anyone can use to work with Mobilize. But in order to actually work with that class, you need to create a "instance" of it. That instance will have data specific to you, such as your API key.

    "Instantiation" is just a fancy way to say "create an instance of".

    In Python, you almost always create an instance of something by calling it parentheses, ie: `mobilize_instance = Mobilize()`.

**Google Sheets**

Setting up the Google Sheets connector takes several steps.

First, you'll need to go to the `Google Developers Console <https://console.cloud.google.com/apis/api/drive.googleapis.com/overview?project=actlocal-smartmaps>`_ and select the project you want to work with, or create a new one (recommended). Following `these instructions from Google <https://developers.google.com/drive/api/guides/enable-drive-api>`_, click **APIs & Auth** and then **APIs**. Select the Drive API from among the API options, and click **enable**.

Once you've created a project and enabled the API, you'll need to get the credentials that will allow you to access the API. Click on the **credentials** option in the left sidebar. Click **create credentials** and select the **Service Account** option. Once you have filled out the form and clicked submit, it will give you a set of credentials as a json string which you can save to a file.

Now we need to tell Parsons where it can find the credentials. We'll set an environmental variable `GOOGLE_DRIVE_CREDENTIALS` which is the path to where your credentials are stored (replace the paths below with your correct paths)::

    set GOOGLE_DRIVE_CREDENTIALS="C:\Home\Projects\"      # Windows
    export GOOGLE_DRIVE_CREDENTIALS="/home/projects/"     # Linux/Mac


Learn more about paths :ref:`here <path-explainer>`.

Finally, you'll want to look inside the credentials file and find an email address in the field `client_email`. It will look something like `service-account@projectname-123456.iam.gserviceaccount.com`. Go to the Google Drive UI for the folder you want to work with and share the folder with this email address.

*

And that's it! We're done with authorizing our accounts (at least, until we add Action Network, but that's not for a while).

^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Extracting Data from Moblize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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