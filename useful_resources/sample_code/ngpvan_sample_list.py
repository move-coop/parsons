# ### METADATA

# Connectors: VAN
# Description: Creates a new saved list from a random sample of an existing saved list in VAN

# ### CONFIGURATION

# Set the configuration variables below or set environmental variables of the same name and leave
# these with empty strings.  We recommend using environmental variables if possible.

config_vars = {
    # VAN
    "VAN_API_KEY": "",
    "VAN_DB_NAME": "",  # One of MyVoters, MyCampaign, MyMembers, EveryAction
    "VAN_FOLDER_ID": "",  # Can be found in the URL on a Folder page in the FolderID param
    "VAN_SAVED_LIST_ID": "",
    "VAN_SAMPLE_LIST_SIZE": "",  # Must be a string
    "VAN_SAMPLE_LIST_NAME": "",
    # AWS
    "AWS_ACCESS_KEY_ID": "",
    "AWS_SECRET_ACCESS_KEY": "",
    "S3_BUCKET": "",  # Bucket that the sample list data should be uploaded to
}


# ### CODE

import os  # noqa: E402
import random  # noqa: E402

from parsons import VAN, logger  # noqa: E402

# Setup

# If variables specified above, sets them as environmental variables
for name, value in config_vars.items():
    if value.strip() != "":
        os.environ[name] = value

van = VAN(db=os.environ["VAN_DB_NAME"])

# Get details on the saved list we're pulling from and the folder we're uploading to
saved_list = van.get_saved_list(os.environ["VAN_SAVED_LIST_ID"])
folder = van.get_folder(os.environ["VAN_FOLDER_ID"])

# If you're receiving errors when trying to call this method related to permissions, you may want to
# reach out to apidevelopers@ngpvan.com to make sure your API key has the correct permissions.
saved_list_download = van.download_saved_list(os.environ["VAN_SAVED_LIST_ID"])

# Generate a random sample of VAN IDs from the list
saved_list_sample_ids = random.sample(
    saved_list_download["VanID"],
    int(os.environ["VAN_SAMPLE_LIST_SIZE"]),
)

# Create a new sample list from the sampled IDs that only includes the VanID column
saved_list_sample = saved_list_download.cut("VanID").select_rows(
    lambda row: row["VanID"] in saved_list_sample_ids
)

logger.info(
    f"Uploading saved list '{os.environ['VAN_SAMPLE_LIST_NAME']}' with "
    f"{os.environ['VAN_SAMPLE_LIST_SIZE']} people"
)

# Upload to VAN through an intermediate S3 bucket where we save the data
van.upload_saved_list(
    saved_list_sample,
    os.environ["VAN_SAMPLE_LIST_NAME"],
    folder["folderId"],
    "S3",
    id_type="vanid",
    replace=True,
    bucket=os.environ["S3_BUCKET"],
)
