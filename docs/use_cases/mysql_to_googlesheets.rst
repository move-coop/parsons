=============================
MySQL to Google Sheets Export
=============================

ActionKit, a commonly used tool in the progressive ecosystem, provides its clients with access to their data in a MySQL database, which is very useful for data practitioners who write SQL but less so for users who do not write code. 350.org needed a way to track their progress to their annual key performance indicators (KPIs) that relied on ActionKit data but was accessible by many staff across the organization. Together with the Movement Cooperative (TMC) they were able to create a solution using the Parsons MySQL Database and Google Sheets classes.

350.org and TMC developed a script to query the MySQL database where 350’s ActionKit data lives and export the query results to a Google Sheet. One important function within the script is the try_overwrite function, which sets a maximum number of times the script will attempt to write data to a Google Sheet before erroring. This function is designed to help navigate Google’s limits on the number of calls per minute.

The original script contained four different queries and saved each query’s results in a different tab in the newly created Google Sheets workbook. A simplified version of the code we used is available as a `sample script <https://github.com/move-coop/parsons/tree/master/useful_resources/sample_code/mysql_to_googlesheets.py>`_ for you to view, re-use, or customize to fit your needs.
