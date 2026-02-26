============================
Civis Job Status Slack Alert
============================

The Movement Cooperative uses Civis Platform to run the data syncs its members rely on.
Civis users are able to monitor the status of these pipelines within the Civis interface, but not all stakeholders are Civis users and if a problem occurs folks have to navigate to another system, such as Slack or TMC's support ticket system, to flag the issue, collaborate on troubleshooting, and get updates on the resolution.

To make this process more efficient, promote transparency, and facilitate collaboration, the TMC Engineering team wrote a script using Parsons to post Civis data sync statuses to an internal Slack channel. The statuses include a green check mark emoji if a sync has run successfully that day, a red X if a sync has failed, a running person if a sync was running at the time the script checked its status, and a person shrugging emoji if the script was unable to determine the status of the sync.

Data syncs in Civis can take a variety of forms. Some are single jobs, some are a specific type of job called an import, and others consist of multiple jobs chained together in a workflow. The Civis API treats these objects slightly differently, so the script accounts for that by parsing out each type from the API response and combining them into one Parsons Table with a column for object_type.

At the request of Indivisible, the TMC Data & Technology team templatized this script to allow for creating customized versions for member organizations with only the specific syncs they depend on. Indivisible now has their own daily alert on the status of their data syncs and other important scripts populating in a private Slack channel.

The code we used is available as a `sample script <https://github.com/move-coop/parsons/tree/master/useful_resources/sample_code/civis_job_status_slack_alert.py>`_ for you to view, re-use, and/or customize.
