# Sample Scripts

The scripts in this folder perform data operations, typically moving data between one connector and another. To perform the same operation, all you should need to do is change the configuration variables in the `Configuration Variables` section of each script. You can also use these scripts as a jumping off point to create new scripts doing similar opeations.

If you can't find the script you want here, you can create an issue in the tracker with the label [script request](https://github.com/move-coop/parsons/labels/script%20request). Please put in as much detail as possible what you would like the script to do.

If you have a script you'd like to add, you have two options. You can create an issue in the tracker with the contents of your script, and add the label [sample script to add](https://github.com/move-coop/parsons/labels/script%20to%20add). Or you can add the script yourself.

If you wish to add the script yourself, please use the `template_script.py` file so that your contribution's structure is consistent with all the other scripts. Please keep most comments as these are directed at the eventual user of your script, but delete any comments labeled "//To Script Writer//" once you understand their advice.

Please also add your new script to the table below.

# Existing Scripts

| File Name                       | Brief Description                                                              | Connectors Used       | Written For Parsons Version |
| ------------------------------- | ------------------------------------------------------------------------------ | --------------------- | --------------------------- |
| actblue_to_google_sheets.py     | Get information about contributions from ActBlue and put in a new Google Sheet | ActBlue, GoogleSheets | 0.18.0                      |
| apply_activist_code.py          | Gets activist codes stored in Redshift and applies to users in Van             | Redshift, VAN         | unknown                     |
| civis_job_status_slack_alert.py | Posts Civis job and workflow status alerts in Slack                            | Slack                 | unknown                     |
| mysql_to_googlesheets.py        | Queries a MySQL database and saves the results to a Google Sheet               | GoogleSheets, MySQL   | unknown                     |
| ngpvan_sample_list.py           | Creates a new saved list from a random sample of an existing saved list in VAN | VAN                   | unknown                     |
| opt_outs_everyaction.py         | Opts out phone numbers in EveryAction from a Redshift table                    | Redshift, VAN         | 0.21.0                      |
| s3_to_redshift.py               | Moves files from S3 to Redshift                                                | Redshift, S3          | unknown                     |
| s3_to_s3.py                     | Get files from vendor s3 bucket and moves to own S3 bucket                     | S3                    | unknown                     |
| update_user_in_actionkit.py     | Adds a voterbase_id (the Targetsmart ID) to users in ActionKit                 | Redshift, ActionKit   | unknown                     |
| zoom_to_van.py                  | Adds Zoom attendees to VAN and applies an activist code                        | Zoom, VAN             | 0.15.0                      |
