Rock the Vote
=============

`Rock the Vote <https://www.rockthevote.org/>`_ is an online registration tool.

The Parsons Connector makes use of Rock the Vote's Rocky API. In order to authenticate with the
API, users will need to specify the ID and the API key of the RTV partner organization for the
data.

**********
QuickStart
**********

To use the RockTheVote class you can either store the partner ID and API key as an
environmental variable (RTV_PARTNER_ID and RTV_PARTNER_API_KEY, respectively), or you can
pass them in as arguments to the class.

.. code-block:: python

   from parsons import RockTheVote

   rtv = RockTheVote()  # If specified as environment variables, no need to pass them in

   rtv = RockTheVote(partner_id='123', partner_api_key='supersecretkey') # Pass credentials directly

To fetch a list of registrations submitted for the partner ID, use the `run_registration_report`
method. It is possible to filter the results by providing a parameter to specify a start date
for the registrations.

.. code-block:: python

   from parsons import RockTheVote

   rtv = RockTheVote()

   registrants = rtv.run_registration_report(since='2020-01-01')

The `run_registration_report` will block as the report is being generated and downloaded from the
Rocky API. For larger reports, this can take a long time. If you have other things you want to do
while the report is running, you can break up the creation of the report from the fetching of the
data.

.. code-block:: python

   from parsons import RockTheVote

   rtv = RockTheVote()

   report_id = rtv.create_registration_report(since='2020-01-01')

   # Do some other stuff here

   registrants = rtv.get_registration_report(report_id)

.. autoclass :: parsons.rockthevote.rtv.RockTheVote
   :inherited-members:
