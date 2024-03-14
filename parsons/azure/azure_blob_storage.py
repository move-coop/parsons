import logging
import os
from urllib.parse import urlparse

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContentSettings, generate_blob_sas

from parsons.utilities import check_env, files

logger = logging.getLogger(__name__)


class AzureBlobStorage(object):
    """
    Instantiate AzureBlobStorage Class for a given Azure storage account.

    `Args:`
        account_name: str
            The name of the Azure storage account to use. Not required if ``AZURE_ACCOUNT_NAME``
            environment variable is set, or if ``account_url`` is supplied.
        credential: str
            An account shared access key with access to the Azure storage account, an SAS token
            string, or an instance of a TokenCredentials class. Not required if ``AZURE_CREDENTIAL``
            environment variable is set.
        account_domain: str
            The domain of the Azure storage account, defaults to "blob.core.windows.net".
            Not required if ``AZURE_ACCOUNT_DOMAIN`` environment variable is set or if
            ``account_url`` is supplied.
        account_url: str
            The account URL for the Azure storage account including the account name and domain.
            Not required if ``AZURE_ACCOUNT_URL`` environment variable is set.
    `Returns:`
        `AzureBlobStorage`
    """

    def __init__(
        self,
        account_name=None,
        credential=None,
        account_domain="blob.core.windows.net",
        account_url=None,
    ):
        self.account_url = os.getenv("AZURE_ACCOUNT_URL", account_url)
        self.credential = check_env.check("AZURE_CREDENTIAL", credential)
        if not self.account_url:
            self.account_name = check_env.check("AZURE_ACCOUNT_NAME", account_name)
            self.account_domain = check_env.check("AZURE_ACCOUNT_DOMAIN", account_domain)
            self.account_url = f"https://{self.account_name}.{self.account_domain}/"
        else:
            if not self.account_url.startswith("http"):
                self.account_url = f"https://{self.account_url}"
            # Update the account name and domain if a URL is supplied
            parsed_url = urlparse(self.account_url)
            self.account_name = parsed_url.netloc.split(".")[0]
            self.account_domain = ".".join(parsed_url.netloc.split(".")[1:])
        self.client = BlobServiceClient(account_url=self.account_url, credential=self.credential)

    def list_containers(self):
        """
        Returns a list of container names for the storage account

        `Returns:`
            list[str]
                List of container names
        """

        container_names = [container.name for container in self.client.list_containers()]
        logger.info(f"Found {len(container_names)} containers.")
        return container_names

    def container_exists(self, container_name):
        """
        Verify that a container exists within the storage account

        `Args:`
            container_name: str
                The name of the container
        `Returns:`
            bool
        """

        container_client = self.get_container(container_name)
        try:
            container_client.get_container_properties()
            logger.info(f"{container_name} exists.")
            return True
        except ResourceNotFoundError:
            logger.info(f"{container_name} does not exist.")
            return False

    def get_container(self, container_name):
        """
        Returns a container client

        `Args:`
            container_name: str
                The name of the container
        `Returns:`
            `ContainerClient`
        """

        logger.info(f"Returning {container_name} container client")
        return self.client.get_container_client(container_name)

    def create_container(self, container_name, metadata=None, public_access=None, **kwargs):
        """
        Create a container

        `Args:`
            container_name: str
                The name of the container
            metadata: Optional[dict[str, str]]
                A dict with metadata to associated with the container.
            public_access: Optional[Union[PublicAccess, str]]
                Settings for public access on the container, can be 'container' or 'blob' if not
                ``None``
            kwargs:
                Additional arguments to be supplied to the Azure Blob Storage API. See `Azure Blob
                Storage SDK documentation <https://docs.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobserviceclient?view=azure-python#create-container-name--metadata-none--public-access-none----kwargs->`_
                for more info.
        `Returns:`
            `ContainerClient`
        """  # noqa

        container_client = self.client.create_container(
            container_name, metadata=metadata, public_access=public_access, **kwargs
        )
        logger.info(f"Created {container_name} container.")
        return container_client

    def delete_container(self, container_name):
        """
        Delete a container.

        `Args:`
            container_name: str
                The name of the container
        `Returns:`
            ``None``
        """

        self.client.delete_container(container_name)
        logger.info(f"{container_name} container deleted.")

    def list_blobs(self, container_name, name_starts_with=None):
        """
        List all of the names of blobs in a container

        `Args:`
            container_name: str
                The name of the container
            name_starts_with: Optional[str]
                A prefix to filter blob names
        `Returns:`
            list[str]
                A list of blob names
        """

        container_client = self.get_container(container_name)
        blobs = [blob for blob in container_client.list_blobs(name_starts_with=name_starts_with)]
        logger.info(f"Found {len(blobs)} blobs in {container_name} container.")
        return blobs

    def blob_exists(self, container_name, blob_name):
        """
        Verify that a blob exists in the specified container

        `Args:`
            container_name: str
                The container name
            blob_name: str
                The blob name
        `Returns:`
            bool
        """

        blob_client = self.get_blob(container_name, blob_name)
        try:
            blob_client.get_blob_properties()
            logger.info(f"{blob_name} exists in {container_name} container.")
            return True
        except ResourceNotFoundError:
            logger.info(f"{blob_name} does not exist in {container_name} container.")
            return False

    def get_blob(self, container_name, blob_name):
        """
        Get a blob object

        `Args:`
            container_name: str
                The container name
            blob_name: str
                The blob name
        `Returns:`
            `BlobClient`
        """

        blob_client = self.client.get_blob_client(container_name, blob_name)
        logger.info(f"Got {blob_name} blob from {container_name} container.")
        return blob_client

    def get_blob_url(
        self,
        container_name,
        blob_name,
        account_key=None,
        permission=None,
        expiry=None,
        start=None,
    ):
        """
        Get a URL with a shared access signature for a blob

        `Args:`
            container_name: str
                The container name
            blob_name: str
                The blob name
            account_key: Optional[str]
                An account shared access key for the storage account. Will default to the key used
                on initialization if one was provided as the credential, but required if it was not.
            permission: Optional[Union[BlobSasPermissions, str]]
                Permissions associated with the blob URL. Can be either a BlobSasPermissions object
                or a string where 'r', 'a', 'c', 'w', and 'd' correspond to read, add, create,
                write, and delete permissions respectively.
            expiry: Optional[Union[datetime, str]]
                The datetime when the URL should expire. Defaults to UTC.
            start: Optional[Union[datetime, str]]
                The datetime when the URL should become valid. Defaults to UTC. If it is ``None``,
                the URL becomes active when it is first created.
        `Returns:`
            str
                URL with shared access signature for blob
        """

        if not account_key:
            if not self.credential:
                raise ValueError(
                    "An account shared access key must be provided if it was not on initialization"
                )
            account_key = self.credential

        sas = generate_blob_sas(
            self.account_name,
            container_name,
            blob_name,
            account_key=account_key,
            permission=permission,
            expiry=expiry,
            start=start,
        )
        return f"{self.account_url}/{container_name}/{blob_name}?sas={sas}"

    def _get_content_settings_from_dict(self, kwargs_dict):
        """
        Removes any keys for ``ContentSettings`` from a dict and returns a tuple of the generated
        settings or ``None`` and a dict with the settings keys removed.

        `Args:`
            kwargs_dict: dict
                A dict which should be processed and may have keys for ``ContentSettings``
        `Returns:`
            Tuple[Optional[ContentSettings], dict]
                Any created settings or ``None`` and the dict with settings keys remvoed
        """

        kwargs_copy = {**kwargs_dict}
        content_settings = None
        content_settings_dict = {}
        content_settings_keys = [
            "content_type",
            "content_encoding",
            "content_language",
            "content_disposition",
            "cache_control",
            "content_md5",
        ]
        kwarg_keys = list(kwargs_copy.keys())
        for key in kwarg_keys:
            if key in content_settings_keys:
                content_settings_dict[key] = kwargs_copy.pop(key)
        if content_settings_dict:
            content_settings = ContentSettings(**content_settings_dict)

        return content_settings, kwargs_copy

    def put_blob(self, container_name, blob_name, local_path, **kwargs):
        """
        Puts a blob (aka file) in a bucket

        `Args:`
            container_name: str
                The name of the container to store the blob
            blob_name: str
                The name of the blob to be stored
            local_path: str
                The local path of the file to upload
            kwargs:
                Additional arguments to be supplied to the Azure Blob Storage API. See `Azure Blob
                Storage SDK documentation <https://docs.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.blobclient?view=azure-python#upload-blob-data--blob-type--blobtype-blockblob---blockblob----length-none--metadata-none----kwargs->`_
                for more info. Any keys that belong to the ``ContentSettings`` object will be
                provided to that class directly.
        `Returns:`
            `BlobClient`
        """  # noqa

        blob_client = self.get_blob(container_name, blob_name)

        # Move all content_settings keys into a ContentSettings object
        content_settings, kwargs_dict = self._get_content_settings_from_dict(kwargs)

        with open(local_path, "rb") as f:
            data = f.read()

        blob_client = blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=content_settings,
            **kwargs_dict,
        )
        logger.info(f"{blob_name} blob put in {container_name} container")

        # Return refreshed BlobClient object
        return self.get_blob(container_name, blob_name)

    def download_blob(self, container_name, blob_name, local_path=None):
        """
        Downloads a blob from a container into the specified file path or a temporary file path

        `Args:`
            container_name: str
                The container name
            blob_name: str
                The blob name
            local_path: Optional[str]
                The local path where the file will be downloaded. If not specified, a temporary
                file will be created and returned, and that file will be removed automatically
                when the script is done running.
        `Returns:`
            str
                The path of the downloaded file
        """

        if not local_path:
            local_path = files.create_temp_file_for_path("TEMPFILEAZURE")

        blob_client = self.get_blob(container_name, blob_name)

        logger.info(f"Downloading {blob_name} blob from {container_name} container.")
        with open(local_path, "wb") as f:
            blob_client.download_blob().readinto(f)
        logger.info(f"{blob_name} blob saved to {local_path}.")

        return local_path

    def delete_blob(self, container_name, blob_name):
        """
        Delete a blob in a specified container.

        `Args:`
            container_name: str
                The container name
            blob_name: str
                The blob name
        `Returns:`
            ``None``
        """

        blob_client = self.get_blob(container_name, blob_name)
        blob_client.delete_blob()
        logger.info(f"{blob_name} blob in {container_name} container deleted.")

    def upload_table(self, table, container_name, blob_name, data_type="csv", **kwargs):
        """
        Load the data from a Parsons table into a blob.

        `Args:`
            table: obj
                A :ref:`parsons-table`
            container_name: str
                The container name to upload the data into
            blob_name: str
                The blob name to upload the data into
            data_type: str
                The file format to use when writing the data. One of: `csv` or `json`
            kwargs:
                Additional keyword arguments to supply to ``put_blob``
        `Returns:`
            `BlobClient`
        """

        if data_type == "csv":
            local_path = table.to_csv()
            content_type = "text/csv"
        elif data_type == "json":
            local_path = table.to_json()
            content_type = "application/json"
        else:
            raise ValueError(f"Unknown data_type value ({data_type}): must be one of: csv or json")

        return self.put_blob(
            container_name, blob_name, local_path, content_type=content_type, **kwargs
        )
