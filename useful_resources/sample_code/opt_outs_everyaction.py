import os
import ast
import requests
import time
from parsons import Redshift, Table, VAN
from parsons import logger
from datetime import datetime

# Credentials

# The API_KEYS_STR variable contains API keys for EA committees in this format:
# {"committee": "Comm. 1 Name", "committee_id": "Comm. 1 ID", "api_key": "Comm. 1 API key"},
# {"committee": "Comm. 2 Name", "committee_id": "Comm. 2 ID", "api_key": "Comm. 2 API key"}
API_KEYS_STR = os.environ['VAN_API_KEYS_PASSWORD']

# Configuration Variables

# The OPT_OUT_TABLE is a schema.table of phones to opt out.
# The table must contain the columns phone, committeeid, and vanid.
OPT_OUT_TABLE = os.environ['OPT_OUT_TABLE']

# The SUCCESS_TABLE is a schema.table where successful opt-outs will be logged.
# This table's columns will be: vanid, phone, committeeid, and applied_at.
SUCCESS_TABLE = os.environ['SUCCESS_TABLE']

# The ERROR_TABLE is a schema.table where errors will be logged.
# This table's columns will be : vanid, phone, committeeid, errored_at, and error.
ERROR_TABLE = os.environ['ERROR_TABLE']

# To use the Redshift connector, set the following environmental variables:
# REDSHIFT_USERNAME
# REDSHIFT_PASSWORD
# REDSHIFT_HOST
# REDSHIFT_DB
# REDSHIFT_PORT

rs = Redshift()


def attempt_optout(ea, row, applied_at, committeeid, success_log, error_log, attempts_left=3):

    vanid = row['vanid']
    phone = row['phone']

    # Documentation on this json construction is here: https://docs.ngpvan.com/reference/common-models
    json = {
        "phones": [
            {"phoneNumber": phone,
            "phoneOptInStatus": "O"}
        ]
    }

    try:
        r = ea.update_person_json(id = vanid, match_json=json)
        
        if isinstance(r, dict):
            # Response is only a dict upon success
            success_log.append({
                "vanid": r.get('vanId'),
                "phone": phone,
                "committeeid": committeeid,
                "applied_at": applied_at
            })

    # If we get an HTTP Error we log it
    # Usually these errors are due to a vanid being deleted or merged
    except requests.exceptions.HTTPError as e:
        r = e
        error_log.append({
            "vanid": vanid,
            "phone": phone,
            "committeeid": committeeid,
            "errored_at": applied_at,
            "error": r
        })

    # If we get a connection error we wait a bit and try again.
    except requests.exceptions.ConnectionError as c:
        logger.info("Got disconnected, waiting and trying again")

        while attempts_left > 0:
            attempts_left -= 1

            # Wait 10 seconds, then try again
            time.sleep(10)
            attempt_optout(ea, row, attempts_left)
            
        else:
            r = str(c)[:999]
            return r
            
            error_log.append({
                "vanid": vanid,
                "phone": phone,
                "committeeid": committeeid,
                "errored_at": applied_at,
                "error": r
            })
            error_tbl = Table(error_log)
            if error_tbl.num_rows() > 0:
                error_tbl.to_redshift(
                    ERROR_TABLE,
                    if_exists='append',
                    alter_table=True
                )
            raise Exception(f"Connection Error {r}")

    return r

def main():
    # Creating empty lists where we'll log successes and errors
    success_log = []
    error_log = []

    # Get the opt out data
    s = rs.query(f"select * from {OPT_OUT_TABLE}")

    # Turn the API keys into a list
    API_KEYS = list(ast.literal_eval(API_KEYS_STR)) if '},' in API_KEYS_STR else [ast.literal_eval(API_KEYS_STR)]

    # Loop through each API key to update phones in each committee
    for k in API_KEYS:

        api = k['api_key']
        committeeid = k['committee_id']
        committee = k['committee'] # This is the committee name
        ea = VAN(db='EveryAction', api_key=api)

        logger.info(f"Working on opt outs in {committee} committee...")

        update = s.select_rows(lambda row: str(row.committeeid) == committeeid)

        logger.info(f"Found {update.num_rows} phones to opt out in {committee} committee...")

        # Now we actually update the records

        if update.num_rows > 0:

            for u in update:

                applied_at = str(datetime.now()).split(".")[0]
                attempt_optout(ea, u, applied_at, committeeid, success_log, error_log)

    # Now we log results
    logger.info(f"There were {len(success_log)} successes and {len(error_log)} errors updating subscription statuses.")

    if len(success_log) > 0:
        success_t = Table(success_log)
        logger.info("Copying success data into log table...")
        rs.copy(success_t, SUCCESS_TABLE, if_exists='append', alter_table = True)
        logger.info("Success log complete.")

    if len(error_log) > 0:
        error_t = Table(error_log)
        logger.info("Copying error data into log table...")
        rs.copy(error_t, ERROR_TABLE, if_exists='append', alter_table = True)
        logger.info("Error log complete.")


if __name__ == '__main__':
    main()
