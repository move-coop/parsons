"""Class for Box API.

To get authentication info (this eventually belongs in the docs for
this connector):

Information on Box site here:
https://developer.box.com/guides/applications/custom-apps/oauth2-setup/

1. Set up Box account.
2. Go to Developer console (https://app.box.com/developers/console).
3. Either select an existing app or create a new one. To create a new one:
  - Select "New App" > "Custom App" > "OAuth 2.0 with JWT".
4. View your app and select "Configuration" in the left menu.
5. Scroll down to get the client id & secret, and just above it
   select OAuth2.0 with JWT (Server Authentication) and
   generate a developer token, aka "access token".

"""

import logging

import boxsdk

from parsons.etl.table import Table
from parsons.utilities.check_env import check as check_env
from parsons.utilities.files import create_temp_file, create_temp_file_for_path

import tempfile

logger = logging.getLogger(__name__)

DEFAULT_FOLDER_ID = "0"


class Box(object):
    """Box is a file storage provider.

    `Args:`
        client_id: str
            Box client (account) id -- probably a 16-char alphanumeric.
            Not required if ``BOX_CLIENT_ID`` env variable is set.
        client_secret: str
            Box private key -- probably a 32-char alphanumeric.
            Not required if ``BOX_CLIENT_SECRET`` env variable is set.
        access_token: str
            Box developer access token -- probably a 32-char alphanumeric.
            Note that this is only valid for developer use only, and should not
            be used when creating and maintaining access for typical users.
            Not required if ''BOX_ACCESS_TOKEN'' env variable is set.
    `Returns:`
            Box class

    *NOTE*: All path-based methods in this class use an intermediate
    method that looks up the relevant folder/file id by successive API
    calls. This can be slow for long paths or intermediate folders
    that contain many items. If performance is an issue, please use the
    corresponding folder_id/file_id methods for each function.
    """

    # In what formats can we upload/save Tables to Box? For now csv and JSON.
    ALLOWED_FILE_FORMATS = ["csv", "json"]

    def __init__(self, client_id=None, client_secret=None, access_token=None):
        client_id = check_env("BOX_CLIENT_ID", client_id)
        client_secret = check_env("BOX_CLIENT_SECRET", client_secret)
        access_token = check_env("BOX_ACCESS_TOKEN", access_token)

        oauth = boxsdk.OAuth2(
            client_id=client_id, client_secret=client_secret, access_token=access_token
        )
        self.client = boxsdk.Client(oauth)

    def create_folder(self, path) -> str:
        """Create a Box folder.

        `Args`:
            path: str
               Path to the folder to be created. If no slashes are present,
               path will be name of folder created in the default folder.

        `Returns`:
            str: The Box id of the newly-created folder.
        """
        if "/" in path:
            parent_folder_path, folder_name = path.rsplit(sep="/", maxsplit=1)
            parent_folder_id = self.get_item_id(path=parent_folder_path)
        else:
            folder_name = path
            parent_folder_id = DEFAULT_FOLDER_ID
        return self.create_folder_by_id(folder_name, parent_folder_id=parent_folder_id)

    def create_folder_by_id(self, folder_name, parent_folder_id=DEFAULT_FOLDER_ID) -> str:
        """Create a Box folder.

        `Args`:
            folder_name: str
               The name to give to the new folder.
            parent_folder_id: str
               Folder id of the parent folder in which to create the new folder. If
               omitted, the default folder will be used.

        `Returns`:
            str: The Box id of the newly-created folder.
        """
        subfolder = self.client.folder(parent_folder_id).create_subfolder(folder_name)
        return subfolder.id

    def delete_folder(self, path) -> None:
        """Delete a Box folder.

        `Args`:
            folder_id: str
               Path to the folder to delete.
        """
        folder_id = self.get_item_id(path)
        self.delete_folder_by_id(folder_id=folder_id)

    def delete_folder_by_id(self, folder_id) -> None:
        """Delete a Box folder.

        `Args`:
            folder_id: str
               The Box id of the folder to delete.
        """
        self.client.folder(folder_id=folder_id).delete()

    def delete_file(self, path) -> None:
        """Delete a Box file.

        `Args`:
            path: str
              Path to the file to delete.
        """
        file_id = self.get_item_id(path)
        self.delete_file_by_id(file_id=file_id)

    def delete_file_by_id(self, file_id) -> None:
        """Delete a Box file.

        `Args`:
            file_id: str
              The Box id of the file to delete.
        """
        self.client.file(file_id=file_id).delete()

    def list(self, path="", item_type=None) -> Table:
        """Return a Table of Box files and/or folders found at a path.

        `Args`:
            path:str
               If specified, the slash-separated path of the folder to be listed.
               If omitted, the default folder will be used.
            item_type: str
               Optionally which type of items should be returned, typically either
               `file` or `folder`. If omitted, all items will be returned.

        `Returns`: Table
            A Parsons table of items in the folder and their attributes.
        """
        if path:
            folder_id = self.get_item_id(path)
        else:
            folder_id = DEFAULT_FOLDER_ID
        return self.list_items_by_id(folder_id=folder_id, item_type=item_type)

    def list_items_by_id(self, folder_id=DEFAULT_FOLDER_ID, item_type=None) -> Table:
        url = "https://api.box.com/2.0/folders/" + folder_id
        json_response = self.client.make_request("GET", url)

        items = Table(json_response.json()["item_collection"]["entries"])
        if item_type:
            items = items.select_rows(lambda row: row.type == item_type)
        return items

    def list_files_by_id(self, folder_id=DEFAULT_FOLDER_ID) -> Table:
        """List all Box files in a folder.

        `Args`:
            folder_id: str
               The Box id of the folder in which to search. If omitted,
               search in the default folder.
        `Returns`: Table
            A Parsons table of files and their attributes.
        """
        return self.list_items_by_id(folder_id=folder_id, item_type="file")

    def list_folders_by_id(self, folder_id=DEFAULT_FOLDER_ID) -> Table:
        """List all Box folders.

        `Args`:
            folder_id: str
               The Box id of the folder in which to search. If omitted,
               search in the default folder.
        `Returns`: Table
            A Parsons table of folders and their attributes.
        """
        return self.list_items_by_id(folder_id=folder_id, item_type="folder")

    def upload_table(self, table, path="", format="csv") -> boxsdk.object.file.File:
        """Save the passed table to Box.

        `Args`:
            table:Table
               The Parsons table to be saved.
            path: str
               Optionally, file path to filename where table should be saved.
            format: str
               For now, only 'csv' and 'json'; format in which to save table.

        `Returns`: BoxFile
            A Box File object
        """
        if "/" in path:
            folder_path, file_name = path.rsplit(sep="/", maxsplit=1)
            folder_id = self.get_item_id(path=folder_path)
        else:  # pragma: no cover
            file_name = path
            folder_id = DEFAULT_FOLDER_ID

        return self.upload_table_to_folder_id(
            table=table, file_name=file_name, folder_id=folder_id, format=format
        )

    def upload_table_to_folder_id(
        self, table, file_name, folder_id=DEFAULT_FOLDER_ID, format="csv"
    ) -> boxsdk.object.file.File:
        """Save the passed table to Box.

        `Args`:
            table:Table
               The Parsons table to be saved.
            file_name: str
               The filename under which it should be saved in Box.
            folder_id: str
               Optionally, the id of the subfolder in which it should be saved.
            format: str
               For now, only 'csv' and 'json'; format in which to save table.

        `Returns`: BoxFile
            A Box File object
        """

        if format not in self.ALLOWED_FILE_FORMATS:
            raise ValueError(
                f"Format argument to upload_table() must be in one "
                f'of {self.ALLOWED_FILE_FORMATS}; found "{format}"'
            )

        # Create a temp directory in which we will let Parsons create a
        # file. Both will go away automatically when we leave scope.
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_file_path = temp_dir_name + "/table.tmp"
            if format == "csv":
                table.to_csv(local_path=temp_file_path)
            elif format == "json":
                table.to_json(local_path=temp_file_path)
            else:
                raise SystemError(
                    f"Got (theoretically) impossible " f'format option "{format}"'
                )  # pragma: no cover

            new_file = self.client.folder(folder_id).upload(
                file_path=temp_file_path, file_name=file_name
            )
        return new_file

    def download_file(self, path: str, local_path: str = None) -> str:
        """Download a Box object to a local file.

        `Args`:
            path: str
                The slash-separated path to the file in Box.
            local_path: str
                The local path where the file will be downloaded. If not
                specified, a temporary file will be created and returned, and
                that file will be removed automatically when the script is done
                running.

        `Returns:`
            str
                The path of the new file
        """
        if not local_path:
            # Temp file will be around as long as enclosing process is running,
            # which we need, because the Table we return will continue to use it.
            local_path = create_temp_file_for_path(path)

        file_id = self.get_item_id(path)

        with open(local_path, "wb") as output_file:
            self.client.file(file_id).download_to(output_file)

        return local_path

    def get_table(self, path, format="csv") -> Table:
        """Get a table that has been saved to Box in csv or JSON format.

        `Args`:
            path: str
                The slash-separated path to the file containing the table.
            format: str
                 Format in which Table has been saved; for now, only 'csv' or 'json'.

        `Returns`: Table
            A Parsons Table.
        """
        file_id = self.get_item_id(path)
        return self.get_table_by_file_id(file_id=file_id, format=format)

    def get_table_by_file_id(self, file_id, format="csv") -> Table:
        """Get a table that has been saved to Box in csv or JSON format.

        `Args`:
            file_id: str
                The Box file_id of the table to be retrieved.
            format: str
                 Format in which Table has been saved; for now, only 'csv' or 'json'.

        `Returns`: Table
            A Parsons Table.
        """
        if format not in self.ALLOWED_FILE_FORMATS:
            raise ValueError(
                f"Format argument to upload_table() must be in one "
                f'of {self.ALLOWED_FILE_FORMATS}; found "{format}"'
            )

        # Temp file will be around as long as enclosing process is running,
        # which we need, because the Table we return will continue to use it.
        output_file_name = create_temp_file()
        with open(output_file_name, "wb") as output_file:
            self.client.file(file_id).download_to(output_file)

        if format == "csv":
            return Table.from_csv(output_file_name)
        elif format == "json":
            return Table.from_json(output_file_name)
        else:
            raise SystemError(
                f"Got (theoretically) impossible " f'format option "{format}"'
            )  # pragma: no cover

    def get_item_id(self, path, base_folder_id=DEFAULT_FOLDER_ID) -> str:
        """Given a path-like object, try to return the id for the file or
        folder at the end of the path.

        *NOTE*: This method makes one API call for each level in
        `path`, so can be slow for long paths or intermediate folders
        containing very many items.

        `Args`:
            path: str
                A slash-separated path from the base folder to the file or
                folder in question.
            base_folder_id: str
                 What to use as the base folder for the path. By default, use
                 the default folder.

        `Returns`: Table
            A Parsons Table.

        """
        try:
            # Grab the leftmost element in the path - this is what we're
            # looking for in this folder.
            if "/" in path:
                this_element, path = path.split(sep="/", maxsplit=1)
                if path == "":
                    raise ValueError('Illegal trailing "/" in file path')

            else:
                this_element = path
                path = ""

            # Look in our current base_folder for an item whose name matches the
            # current element. If we're at initial, non-recursed call, base_folder
            # will be default folder.
            item_id = None
            for item in self.client.folder(folder_id=base_folder_id).get_items():
                if item.name == this_element:
                    item_id = item.id
                    break

            if item_id is None:
                raise ValueError(f'No file or folder named "{this_element}"')

            # If there are no more elements left in path, this is the item we're after.
            if not len(path):
                return item_id

            # If there *are* more elements in the path, we need to check that this item is
            # in fact a folder so we can recurse and search inside it.
            if item.type != "folder":
                raise ValueError(f'Invalid folder "{this_element}"')

            return self.get_item_id(path=path, base_folder_id=item_id)

        # At the top level of the recursion, when we have the entire path, we want
        # to attach it to the error message. If caught at some inner level of the
        # recursion, just pass it on up.
        except ValueError as e:
            if base_folder_id == DEFAULT_FOLDER_ID:
                raise ValueError(f'{e}: "{path}"')
            else:
                raise
