# This script checks the status of all jobs and workflows in a given Civis Project
# and posts them to a Slack channel.

import datetime
import logging

import civis

from parsons import Slack, Table

# Environment variables
# To use the Civis connector, set the environment variables CIVIS_DATABASE and CIVIS_API_KEY.
# These environment variables are not necessary if you run this code in a Civis container script.
client = civis.APIClient()
# To use the Slack connector, set the environment variable SLACK_API_TOKEN
slack = Slack()
# More on environmental variables:
# https://move-coop.github.io/parsons/html/use_cases/contribute_use_cases.html#sensitive-information

# Configuration variables
SLACK_CHANNEL = ""  # Slack channel where the alert will post.
CIVIS_PROJECT = ""  # ID of the Civis project with jobs and workflows you want to see the status of.

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter("%(levelname)s %(message)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel("INFO")


# Cleans up datetime format for posting to Slack.
def format_datetime(text):
    formatted_text = text.replace("Z", "")
    dt = datetime.datetime.fromisoformat(formatted_text)
    return dt.strftime("%Y-%m-%d")


# Assigns an emoji for each potential run status a Civis job or workflow might have.
def get_run_state_emoji(run_state):
    if run_state == "succeeded":
        return ":white_check_mark:"
    elif run_state == "failed":
        return ":x:"
    elif run_state == "running":
        return ":runner:"
    else:
        return ":shrug:"


# Returns a Parsons table with workflow and job data from the specified Civis project.
def get_workflows_and_jobs(project_id):
    project = client.projects.get(project_id)

    # Get workflow and the job data from the project
    workflows = [dict(workflow) for workflow in project["workflows"]]
    table = Table(workflows)
    # We need to distinguish between jobs and workflows later on,
    # so adding a column noting these are workflows.
    table.add_column("object_type", "workflow")

    # Imports and other scripts are separated out in the response but they are all treated as jobs
    # so we pull and combine
    jobs = [dict(job) for job in project["scripts"]]
    imports = [dict(import_job) for import_job in project["imports"]]
    full_list = jobs + imports
    jobs_table = Table(full_list)
    jobs_table.add_column("object_type", "job")

    # Here we combine the table of jobs and imports into the table of workflows.
    # The object_type column lets us distinguish between the types,
    # which is necessary for the get_last_success function.
    table.concat(jobs_table)

    return table


# Returns the date and time of the last successful run for a Civis job or workflow.
def get_last_success(object_id, object_type):
    last_success = "-"

    if object_type == "workflow":
        workflow_executions = client.workflows.list_executions(object_id, order="updated_at")
        for execution in workflow_executions:
            if execution["state"] != "succeeded":
                continue
            else:
                last_success = format_datetime(execution["finished_at"])
                break

    elif object_type == "job":
        job_runs = client.jobs.list_runs(object_id)
        job_runs_tbl = Table([dict(run) for run in job_runs]).sort(
            columns="finished_at", reverse=True
        )
        for run in job_runs_tbl:
            if run["state"] != "succeeded":
                continue
            else:
                last_success = format_datetime(run["finished_at"])
                break

    else:
        logger.info(f"{object_type} is not a valid object type.")

    return last_success


def main():
    project_name = client.projects.get(CIVIS_PROJECT)["name"]

    scripts_table = get_workflows_and_jobs(CIVIS_PROJECT).sort(columns=["state", "name"])

    logger.info(f"Found {scripts_table.num_rows} jobs and workflows in {project_name} project.")

    # This is a list of strings we will build with each job's status
    output_lines = []

    for run in scripts_table:
        last_success = get_last_success(run["id"], run["object_type"])

        output_line = f"""{get_run_state_emoji(run['state'])}
        {run['name']} (last success: {last_success})"""
        output_lines.append(output_line)

    # Output our message to Slack
    # Combine the list of statuses into one string
    line_items = "\n".join(output_lines)
    message = f"*{project_name} Status*\n{line_items}"
    logger.info(f"Posting message to Slack channel {SLACK_CHANNEL}")
    # Post message
    slack.message_channel(SLACK_CHANNEL, message)
    logger.info("Slack message posted")


if __name__ == "__main__":
    main()
