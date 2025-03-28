import datetime
import json
import os
import time

import requests

from parsons import VAN, Redshift, Table, logger

# Committee Information and Credentials

# This script can be run against multiple EveryAction committees.
# The COMMITTEES_STR variable should be a list of committee information in JSON format.
# The information should include the committee's name, ID, and API key.
# [{"committee": "Committee 1", "committee_id": "12345", "api_key": "Committee 1 API key"},
# {"committee": "Committee 2", "committee_id": "56789", "api_key": "Committee 2 API key"}]
# This script was originally written to run in Civis Platform, which pulls environment variables
# in as strings.
COMMITTEES_STR = os.environ["COMMITTEES_PASSWORD"]
COMMITTEES = json.loads(COMMITTEES_STR)

# Configuration Variables

# It is assumed that the tables below live in a schema in Redshift
# Therefore, in order to interact with them, we must name them using the format schema.table.
# More on this here: https://docs.aws.amazon.com/redshift/latest/gsg/t_creating_schema.html

# The OPT_OUT_TABLE is a table of phones to opt out.
# The variable must be a string with the format schema.table.
# The table must contain the columns phone, committeeid, and vanid.
OPT_OUT_TABLE = os.environ["OPT_OUT_TABLE"]

# The SUCCESS_TABLE is a table where successful opt-outs will be logged.
# The variable must be a string with the format schema.table.
# This table's columns will be: vanid, phone, committeeid, and applied_at.
SUCCESS_TABLE = os.environ["SUCCESS_TABLE"]

# The ERROR_TABLE is a table where errors will be logged.
# The variable must be a string with the format schema.table.
# This table's columns will be : vanid, phone, committeeid, errored_at, and error.
ERROR_TABLE = os.environ["ERROR_TABLE"]

# To use the Redshift connector, set the following environmental variables:
# REDSHIFT_USERNAME
# REDSHIFT_PASSWORD
# REDSHIFT_HOST
# REDSHIFT_DB
# REDSHIFT_PORT

rs = Redshift()


def attempt_optout(
    every_action, row, applied_at, committeeid, success_log, error_log, attempts_left=3
):
    vanid = row["vanid"]
    phone = row["phone"]

    # Documentation on this json construction is here
    # https://docs.ngpvan.com/reference/common-models
    match_json = {"phones": [{"phoneNumber": phone, "phoneOptInStatus": "O"}]}

    try:
        response = every_action.update_person_json(id=vanid, match_json=match_json)

        # If the response is a dictionary the update was successful
        if isinstance(response, dict):
            success_log.append(
                {
                    "vanid": response.get("vanId"),
                    "phone": phone,
                    "committeeid": committeeid,
                    "applied_at": applied_at,
                }
            )

            return response

    # If we get an HTTP Error add it to the error log
    # Usually these errors mean a vanid has been deleted from EveryAction
    except requests.exceptions.HTTPError as error:
        error_message = str(error)[:999]
        error_log.append(
            {
                "vanid": vanid,
                "phone": phone,
                "committeeid": committeeid,
                "errored_at": applied_at,
                "error": error_message,
            }
        )

        return error_message

    # If we get a connection error we wait a bit and try again.
    except requests.exceptions.ConnectionError as connection_error:
        logger.info("Got disconnected, waiting and trying again")

        while attempts_left > 0:
            attempts_left -= 1

            # Wait 10 seconds, then try again
            time.sleep(10)
            attempt_optout(every_action, row, attempts_left)

        else:
            # If we are still getting a connection error after our maximum number of attempts
            # we add the error to the log, save our full success and error logs in Redshift,
            # and raise the error.
            connection_error_message = str(connection_error)[:999]

            error_log.append(
                {
                    "vanid": vanid,
                    "phone": phone,
                    "committeeid": committeeid,
                    "errored_at": applied_at,
                    "error": connection_error_message,
                }
            )

            if len(success_log) > 0:
                success_parsonstable = Table(success_log)
                logger.info("Copying success data into log table...")
                rs.copy(
                    success_parsonstable,
                    SUCCESS_TABLE,
                    if_exists="append",
                    alter_table=True,
                )
                logger.info("Success log complete.")

            if len(error_log) > 0:
                error_parsonstable = Table(error_log)
                logger.info("Copying error data into log table...")
                rs.copy(
                    error_parsonstable,
                    ERROR_TABLE,
                    if_exists="append",
                    alter_table=True,
                )
                logger.info("Error log complete.")

            raise Exception(f"Connection Error {connection_error}")


def main():
    # Creating empty lists where we'll log successes and errors
    success_log = []
    error_log = []

    # Get the opt out data
    all_opt_outs = rs.query(f"select * from {OPT_OUT_TABLE}")

    # Loop through each committee to opt-out phones
    for committee in COMMITTEES:
        api_key = committee["api_key"]
        committeeid = committee["committee_id"]
        committee_name = committee["committee"]

        every_action = VAN(db="EveryAction", api_key=api_key)

        logger.info(f"Working on opt outs in {committee_name} committee...")

        # Here we narrow the all_opt_outs table to only the rows that correspond
        # to this committee.
        opt_outs = all_opt_outs.select_rows(lambda row: str(row.committeeid) == committeeid)  # noqa: B023

        logger.info(f"Found {opt_outs.num_rows} phones to opt out in {committee_name} committee...")

        # Now we actually update the records

        if opt_outs.num_rows > 0:
            for opt_out in opt_outs:
                applied_at = str(datetime.datetime.now(tz=datetime.timezone.utc)).split(".")[0]
                attempt_optout(
                    every_action,
                    opt_out,
                    applied_at,
                    committeeid,
                    success_log,
                    error_log,
                )

    # Now we log results
    logger.info(f"There were {len(success_log)} successes and {len(error_log)} errors.")

    if len(success_log) > 0:
        success_parsonstable = Table(success_log)
        logger.info("Copying success data into log table...")
        rs.copy(success_parsonstable, SUCCESS_TABLE, if_exists="append", alter_table=True)
        logger.info("Success log complete.")

    if len(error_log) > 0:
        error_parsonstable = Table(error_log)
        logger.info("Copying error data into log table...")
        rs.copy(error_parsonstable, ERROR_TABLE, if_exists="append", alter_table=True)
        logger.info("Error log complete.")


if __name__ == "__main__":
    main()
