"""Utility for running and logging output from dbt commands

Enable this utility by installing parsons with a dbt extra:

.. code-block:: bash

    pip install parsons[dbt-redshift]
    pip install parsons[dbt-postgres]
    pip install parsons[dbt-snowflake]
    pip install parsons[dbt-bigquery]

To run dbt commands, you will need to have a dbt project directory
somewhere on the local filesystem.

The dbt command will inherit environment variables from the python
process shell, so if your dbt profiles.yml file uses environment
variables, ensure those are set in python or the parent shell before
running this dbt utility.

Logging is handled separately from the dbt run itself. The
dbtRunner.run method returns a dbtCommandResult object which can be
passed to a child class of dbtLogger for logging to stdout, slack,
etc.

Parsons provides a few example dbtLogger child classes, but for
best results, design your own!

Example usage:

.. code-block:: python

    from parsons.utilities.dbt import (
        run_dbt_commands,
        dbtLoggerSlack,
        dbtLoggerPython
    )

    run_dbt_commands(
        commands=['run', 'test'],
        dbt_project_directory='/home/ubuntu/code/dbt_project/',
        loggers=[
            dbtLoggerPython,
            dbtLoggerSlack(slack_webhook=os.environ['SLACK_WEBHOOK'])
        ]
    )

"""

from parsons.utilities.dbt.dbt import run_dbt_commands
from parsons.utilities.dbt.logging import (
    dbtLoggerMarkdown,
    dbtLoggerPython,
    dbtLoggerSlack,
    dbtLoggerStdout,
)

__all__ = [
    "run_dbt_commands",
    "dbtLoggerMarkdown",
    "dbtLoggerSlack",
    "dbtLoggerStdout",
    "dbtLoggerPython",
]
