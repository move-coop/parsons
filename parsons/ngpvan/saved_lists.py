"""NGPVAN Saved List Endpoints"""

from parsons.etl.table import Table
from parsons.utilities import cloud_storage, files
import logging
import uuid

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

    def upload_saved_list(self, tbl, list_name, folder_id, url_type, id_type='vanid', replace=False,
                          **url_args):
        """
        Upload a saved list.

        `Args:`
            tbl: parsons.Table
                A parsons table object.
            list_name: str
                The saved list name.
            folder_id: int
                The folder id where the list will be stored.
            url_post_type: str
                The cloud file storage to use to post the file. Currently only ``S3``.
            id_type: str
                The primary key type. The options, beyond ``vanid`` are specific to your
                instance of VAN.
            replace: boolean
                Replace saved list if already exists.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type.
                    * S3 requires ``bucket`` argument and, if not stored as env variables
                      ``aws_access_key`` and ``aws_secret_access_key``.
        """

        # Move to cloud storage
        file_name = str(uuid.uuid1()) + '.zip'
        public_url = cloud_storage.post_file(tbl, url_type, file_path=file_name, **url_args)
        csv_name = files.extract_file_name(file_name, include_suffix=False) + '.csv'
        logger.info(f'Table uploaded to {url_type}.')

        # Create XML
        xml = self.connection.soap_client.factory.create('CreateAndStoreSavedListMetaData')
        xml.SavedList._Name = list_name
        xml.DestinationFolder._ID = folder_id
        xml.SourceFile.FileName = csv_name
        xml.SourceFile.FileUrl = public_url
        xml.SourceFile.FileCompression = 'zip'
        xml.Options.OverwriteExistingList = replace

        # Describe file
        file_desc = self.connection.soap_client.factory.create('SeparatedFileFormatDescription')
        file_desc._name = 'csv'
        file_desc.HasHeaderRow = True

        # Only support single column for now
        col = self.connection.soap_client.factory.create('Column')
        col.Name = id_type
        col.RefersTo._Path = f"Person[@PersonIDType=\'{id_type}\']"
        col._Index = '0'

        # VAN errors are not particularly descriptive for this method, particularly when adding to
        # an existing list when the replace boolean is set to false. This is likely to be a common
        # mistake that folks make, so we will check on our own to see if it exists.
        if not replace:
            logger.info('Checking to see if list already exists.')
            for r in self.get_saved_lists(folder_id):
                if r['name'] == list_name:
                    raise ValueError("Saved list already exists. Set to replace"
                                     " or change the list name.")

        # Assemble request
        file_desc.Columns.Column.append(col)
        xml.SourceFile.Format = file_desc

        self.connection.soap_client.service.CreateAndStoreSavedList(xml)
        logger.info(f'Uploaded {tbl.num_rows} records to {list_name} saved list.')


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
            dict
                The export job object
        """

        json = {"savedListId": str(list_id),
                "type": str(export_type),
                "webhookUrl": webhookUrl
                }

        r = self.connection.post_request('exportJobs', json=json)
        logger.info('Retrieved export job.')
        return r

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
