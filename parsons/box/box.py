"""Class for Box API.

To get authentication info (this eventually belongs in the docs for
this connector):

Information on Box site here:
https://developer.box.com/guides/applications/platform-apps/create/

1. Set up Box account.
2. Go to Developer console (https://app.box.com/developers/console).
3. Either select an existing app or create a new one. To create a new one:
  - Select "New App" > Choose an App Name > Select "Server Auth - JWT" for App Type.
4. View your app and select "Configuration" in the top menu.
5. Scroll down to select OAuth 2.0 with JSON Web Tokens (Server Authentication) and
   generate a Developer Token, aka "access token".

"""

import logging
import tempfile
from pathlib import Path
from typing import Literal

from box_sdk_gen import BoxClient, BoxDeveloperTokenAuth
from box_sdk_gen.managers.folders import CreateFolderParent
from box_sdk_gen.managers.uploads import (
    UploadFileAttributesParentField,
    UploadWithPreflightCheckAttributes,
)
from box_sdk_gen.schemas.file import File

from parsons.etl.table import Table
from parsons.utilities.check_env import check as check_env
from parsons.utilities.files import create_temp_file, create_temp_file_for_path

logger = logging.getLogger(__name__)

DEFAULT_FOLDER_ID = "0"


class Box:
    """Box is a file storage provider.

    `Args:`
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

    def __init__(self, access_token: str = None):
        access_token = check_env("BOX_ACCESS_TOKEN", access_token)
        oauth = BoxDeveloperTokenAuth(token=access_token)
        self.client = BoxClient(auth=oauth)

    def __replace_backslashes(self, path: str) -> str:
        """Replace the back slashes in a string with forward slashes.

        `Args`:
            path: str
               Path that may need slashes replaced.

        `Returns`:
            str: A string for a path with back slashes replaced by forward slashes.
        """
        if path is not None and "\\" in path:
            new_path = path.replace("\\", "/")
            return new_path
        else:
            return path

    def __getPathFromString(self, path: str) -> (str, str, str):
        """Parse a file name out from a string representing a Box path.

        `Args`:
            path: str
               A path in Box.

        `Returns`:
            (str, str, str): The item parent, item name, and item id for the path.
        """
        new_path = self.__replace_backslashes(path)

        if "/" in new_path:
            item_path, item_name = new_path.rsplit(sep="/", maxsplit=1)
            item_id = self.get_item_id(item_path)
        else:
            item_path, item_name, item_id = new_path, None, DEFAULT_FOLDER_ID

        if item_name is None:
            item_name = item_path
            item_path = ""

        return item_path, item_name, item_id

    def create_folder(self, path: str) -> str:
        """Create a Box folder.

        `Args`:
            path: str
               Path to the folder to be created. If no slashes are present,
               path will be name of folder created in the default folder. Any
               back slashes will be treated as forward slashes.

        `Returns`:
            str: The Box id of the newly-created folder.
        """
        folder_parent_name, folder_name, folder_id = self.__getPathFromString(path)
        return self.create_folder_by_id(folder_name, parent_folder_id=folder_id)

    def create_folder_by_id(
        self, folder_name: str, parent_folder_id: str = DEFAULT_FOLDER_ID
    ) -> str:
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
        parent = CreateFolderParent(id=parent_folder_id)
        subfolder = self.client.folders.create_folder(name=folder_name, parent=parent)
        return subfolder.id

    def delete_folder(self, path: str) -> None:
        """Delete a Box folder.

        `Args`:
            folder_id: str
               Path to the folder to delete. Any back slashes will be treated
               as forward slashes.
        """
        new_path = self.__replace_backslashes(path)
        folder_id = self.get_item_id(new_path)
        self.delete_folder_by_id(folder_id=folder_id)

    def delete_folder_by_id(self, folder_id: str) -> None:
        """Delete a Box folder.

        `Args`:
            folder_id: str
               The Box id of the folder to delete.
        """
        self.client.folders.delete_folder_by_id(folder_id=folder_id, recursive=True)

    def delete_file(self, path: str) -> None:
        """Delete a Box file.

        `Args`:
            path: str
              Path to the file to delete. Any back slashes will be treated as
              forward slashes.
        """
        file_id = self.get_item_id(path)
        self.delete_file_by_id(file_id=file_id)

    def delete_file_by_id(self, file_id: str) -> None:
        """Delete a Box file.

        `Args`:
            file_id: str
              The Box id of the file to delete.
        """
        self.client.files.delete_file_by_id(file_id=file_id)

    def list(
        self, path: str | None = None, item_type: Literal["file", "folder"] | None = None
    ) -> Table:
        """Return a Table of Box files and/or folders found at a path.

        `Args`:
            path:str
               If specified, the slash-separated path of the folder to be listed.
               If omitted, the default folder will be used.
            item_type: str
               Optionally which type of items should be returned, typically either
               `file` or `folder`. If omitted, all items will be returned. Any back
               slashes will be treated as forward slashes.

        `Returns`: Table
            A Parsons table of items in the folder and their attributes.
        """
        folder_id = DEFAULT_FOLDER_ID if path is None else self.get_item_id(path)
        return self.list_items_by_id(folder_id=folder_id, item_type=item_type)

    def list_items_by_id(
        self, folder_id: str = DEFAULT_FOLDER_ID, item_type: Literal["file", "folder"] | None = None
    ) -> Table:
        """Return a Table of Box files and/or folders found in a folder.

        `Args`:
            folder_id: str
              The Box id of the folder to list items for.
            item_type: str
               Optionally which type of items should be returned, typically either
               `file` or `folder`. If omitted, all items will be returned.

        `Returns`: Table
            A Parsons table of items in the folder and their attributes.
        """
        folder_items = self.client.folders.get_folder_items(folder_id)
        if item_type is not None:
            items = Table([vars(x) for x in folder_items.entries if x.type == item_type])
        else:
            items = Table([vars(x) for x in folder_items.entries])

        return items

    def list_files_by_id(self, folder_id: str | None = None) -> Table:
        """List all Box files in a folder.

        `Args`:
            folder_id: str
               The Box id of the folder in which to search. If omitted,
               search in the default folder.
        `Returns`: Table
            A Parsons table of files and their attributes.
        """
        use_folder_id = DEFAULT_FOLDER_ID if folder_id is None else folder_id
        return self.list_items_by_id(folder_id=use_folder_id, item_type="file")

    def list_folders_by_id(self, folder_id: str | None = None) -> Table:
        """List all Box folders.

        `Args`:
            folder_id: str
               The Box id of the folder in which to search. If omitted,
               search in the default folder.
        `Returns`: Table
            A Parsons table of folders and their attributes.
        """
        use_folder_id = DEFAULT_FOLDER_ID if folder_id is None else folder_id
        return self.list_items_by_id(folder_id=use_folder_id, item_type="folder")

    def upload_table(self, table: Table, path: str, format: Literal["csv", "json"] = "csv") -> File:
        """Save the passed table to Box.

        `Args`:
            table:Table
               The Parsons table to be saved.
            path: str
               File path to filename where table should be saved. Any back
               slashes will be treated as forward slashes.
            format: str
               For now, only 'csv' and 'json'; format in which to save table.

        `Returns`: File
            A Box File object
        """
        folder_parent_name, table_name, folder_id = self.__getPathFromString(path)
        return self.upload_table_to_folder_id(
            table=table, file_name=table_name, folder_id=folder_id, format=format
        )

    def upload_table_to_folder_id(
        self,
        table: Table,
        file_name: str,
        folder_id: str | None = None,
        format: Literal["csv", "json"] = "csv",
    ) -> File:
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

        `Returns`: File
            A Box File object
        """
        use_folder_id = DEFAULT_FOLDER_ID if folder_id is None else folder_id

        if format not in self.ALLOWED_FILE_FORMATS:
            raise ValueError(
                f'Format argument must be in one of {self.ALLOWED_FILE_FORMATS}; found "{format}"'
            )

        # Create a temp directory in which we will let Parsons create a
        # file. Both will go away automatically when we leave scope.
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_file_path = f"{temp_dir_name}/table.tmp"
            if format == "csv":
                table.to_csv(local_path=temp_file_path)
            elif format == "json":
                table.to_json(local_path=temp_file_path)
            else:
                raise SystemError(
                    f'Got (theoretically) impossible format option "{format}"'
                )  # pragma: no cover

            new_file = self.upload_file_to_folder_id(
                file=Path(temp_file_path), file_name=file_name, folder_id=use_folder_id
            )

        return new_file

    def upload_file(self, file: Path, path: str | None = None) -> File:
        """Save the passed file to Box.

        `Args`:
            file: Path
               The local file to be saved to Box.
            path: str
               Optionally, file path to filename where table should be saved. Any back
               slashes will be treated as forward slashes.

        `Returns`: File
            A Box File object
        """
        if path is not None:
            _, file_name, folder_id = self.__getPathFromString(path)
        else:
            _, file_name, folder_id = "", file.name, DEFAULT_FOLDER_ID

        return self.upload_file_to_folder_id(file=file, file_name=file_name, folder_id=folder_id)

    def upload_file_to_folder_id(
        self, file: Path, file_name: str | None = None, folder_id: str | None = None
    ) -> File:
        """Save the passed file to Box.

        `Args`:
            file: Path
               The local file to be saved to Box.
            file_name: str
               Optionally, the filename under which it should be saved in Box.
            folder_id: str
               Optionally, the id of the subfolder in which it should be saved.

        `Returns`: File
            A Box File object
        """
        use_file_name = file.name if file_name is None else file_name
        use_folder_id = DEFAULT_FOLDER_ID if folder_id is None else folder_id

        # Utilize chunked uploads depending on file size as suggested
        # by Box documentation. Files over 50MB should use chunked uploads.
        file_size = file.stat().st_size
        with file.open(mode="rb") as upload_file:
            if file_size > 50000000:
                new_file = self.client.chunked_uploads.upload_big_file(
                    file=upload_file,
                    file_name=use_file_name,
                    file_size=file_size,
                    parent_folder_id=use_folder_id,
                )
            else:
                file_parent = UploadFileAttributesParentField(id=use_folder_id)
                file_attributes = UploadWithPreflightCheckAttributes(
                    name=use_file_name, parent=file_parent, size=file_size
                )
                uploaded_files = self.client.uploads.upload_with_preflight_check(
                    attributes=file_attributes, file=upload_file
                )
                if uploaded_files.total_count > 0:
                    new_file = uploaded_files.entries[0]
                else:
                    raise SystemError(
                        "Did not receive file upload list from upload response"
                    )  # pragma: no cover

        return new_file

    def download_file(self, path: str, local_path: Path | None = None) -> Path:
        """Download a Box object to a local file.

        `Args`:
            path: str
                The slash-separated path to the file in Box. Any back slashes will be
                treated as forward slashes.
            local_path: Path
                The local path where the file will be downloaded. If not
                specified, a temporary file will be created and returned, and
                that file will be removed automatically when the script is done
                running.

        `Returns:`
            str
                The absolute path of the new file
        """
        if not local_path:
            # Temp file will be around as long as enclosing process is running,
            # which we need, because the Table we return will continue to use it.
            use_local_path = Path(create_temp_file_for_path(path))
        else:
            use_local_path = Path(create_temp_file_for_path(path))

        file_id = self.get_item_id(path)

        with use_local_path.open(mode="wb") as output_file:
            self.client.downloads.download_file_to_output_stream(
                file_id=file_id, output_stream=output_file
            )

        return use_local_path

    def get_table(self, path: str, format: Literal["csv", "json"] = "csv") -> Table:
        """Get a table that has been saved to Box in csv or JSON format.

        `Args`:
            path: str
                The slash-separated path to the file containing the table. Any back
                slashes will be treated as forward slashes.
            format: str
                 Format in which Table has been saved; for now, only 'csv' or 'json'.

        `Returns`: Table
            A Parsons Table.
        """
        file_id = self.get_item_id(path)
        return self.get_table_by_file_id(file_id=file_id, format=format)

    def get_table_by_file_id(self, file_id: str, format: Literal["csv", "json"] = "csv") -> Table:
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
                f'Format argument must be in one of {self.ALLOWED_FILE_FORMATS}; found "{format}"'
            )

        # Temp file will be around as long as enclosing process is running,
        # which we need, because the Table we return will continue to use it.
        output_file_name = create_temp_file()
        with Path(output_file_name).open(mode="wb") as output_file:
            self.client.downloads.download_file_to_output_stream(
                file_id=file_id, output_stream=output_file
            )

        if format == "csv":
            return Table.from_csv(output_file_name)
        elif format == "json":
            return Table.from_json(output_file_name)
        else:
            raise SystemError(
                f'Got (theoretically) impossible format option "{format}"'
            )  # pragma: no cover

    def get_item_id(self, path: str, base_folder_id: str | None = DEFAULT_FOLDER_ID) -> str:
        """Given a path-like object, try to return the id for the file or
        folder at the end of the path.

        *NOTE*: This method makes one API call for each level in
        `path`, so can be slow for long paths or intermediate folders
        containing very many items.

        `Args`:
            path: str
                A slash-separated path from the base folder to the file or
                folder in question. Any back slashes will be treated as forward
                slashes.
            base_folder_id: str
                 What to use as the base folder for the path. By default, use
                 the default folder.

        `Returns`: Table
            A Parsons Table.

        """
        try:
            if "/" in path:
                this_element, use_path = path.split(sep="/", maxsplit=1)
                if path == "":
                    raise ValueError('Illegal trailing "/" in file path')
            else:
                this_element = path
                use_path = ""

            use_base_folder_id = DEFAULT_FOLDER_ID if base_folder_id is None else base_folder_id

            # Look in our current base_folder for an item whose name matches the
            # current element. If we're at initial, non-recursed call, base_folder
            # will be default folder.
            item_id = None
            for item in self.client.folders.get_folder_items(folder_id=use_base_folder_id).entries:
                if item.name == this_element:
                    item_id = item.id
                    break

            if item_id is None:
                raise ValueError(f'No file or folder named "{this_element}"')

            # If there are no more elements left in path, this is the item we're after.
            if not len(use_path):
                return item_id

            # If there *are* more elements in the path, we need to check that this item is
            # in fact a folder so we can recurse and search inside it.
            if item.type != "folder":
                raise ValueError(f'Invalid folder "{this_element}"')

            return self.get_item_id(path=use_path, base_folder_id=item_id)

        # At the top level of the recursion, when we have the entire path, we want
        # to attach it to the error message. If caught at some inner level of the
        # recursion, just pass it on up.
        except ValueError as e:
            if use_base_folder_id == DEFAULT_FOLDER_ID:
                raise ValueError(f'{e}: "{use_path}"') from e
            else:
                raise
