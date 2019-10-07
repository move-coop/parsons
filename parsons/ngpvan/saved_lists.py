"""NGPVAN Saved List Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class SavedLists(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_saved_lists(self, folder_id=None):
        """
        Get saved lists.

        `Args:`
            folder_id: int
                Filter by the id for a VAN folder. If included returns only
                the saved lists in the folder
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request('savedLists', params={'folderId': folder_id}))
        logger.info(f'Found {tbl.num_rows} saved lists.')
        return tbl

    def get_saved_list(self, saved_list_id):
        """
        Returns a saved list object.

        `Args:`
            saved_list_id: int
                The saved list id.
        `Returns:`
            dict
        """

        r = self.connection.get_request(f'savedLists/{saved_list_id}')
        logger.info(f'Found saved list {saved_list_id}.')
        return r

    def download_saved_list(self, saved_list_id):
        """
        Download the vanids associated with a saved list.

        `Args:`
            saved_list_id: int
                The saved list id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        ej = ExportJobs(self.connection)
        job = ej.export_job_create(saved_list_id)

        if isinstance(job, tuple):
            return job
        else:
            return Table.from_csv(job['downloadUrl'])


class Folders(object):

    def __init__(self, van_connection):

        # Some sort of test if the van_connection is not present.

        self.connection = van_connection

    def get_folders(self):
        """
        Get all folders owned or shared with the API user.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request('folders'))
        logger.info(f'Found {tbl.num_rows} folders.')
        return tbl

    def get_folder(self, folder_id):
        """
        Get a folder owned by or shared with the API user.

        `Args:`
            folder_id: int
                The folder id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        r = self.connection.get_request(f'folders/{folder_id}')
        logger.info(f'Found folder {folder_id}.')
        return r


class ExportJobs(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_export_job_types(self):
        """
        Get export job types

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request('exportJobTypes'))
        logger.info(f'Found {tbl.num_rows} export job types.')
        return tbl

    def export_job_create(self, list_id, export_type=4,
                          webhookUrl="https://www.nothing.com"):
        """
        Creates an export job

        Currently, this is only used for exporting saved lists. It is
        recommended that you use the :meth:`saved_list_download` method
        instead.

        `Args:`
            list_id: int
                This is where you should input the list id
            export_type: int
                The export type id, which defines the columns to export
            webhookUrl:
                A webhook to include to notify as to the status of the export
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options. Includes a
                download link for the file.
        """

        url = self.connection.uri + 'exportJobs'

        data = {"savedListId": str(list_id),
                "type": str(export_type),
                "webhookUrl": webhookUrl
                }

        return self.connection.request(url, req_type='POST', post_data=data, raw=True)

    def get_export_job(self, export_job_id):
        """
        Get an export job.

        `Args:`
            export_job_id: int
                The xxport job id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        r = self.connection.get_request(f'exportJobs/{export_job_id}')
        logger.info(f'Found export job {export_job_id}.')
        return r
