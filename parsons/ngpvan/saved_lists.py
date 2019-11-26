"""NGPVAN Saved List Endpoints"""

from parsons.etl.table import Table
from parsons.utilities import cloud_storage
import logging
import uuid
from suds.client import Client

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
                          **url_kwargs):
        """
        Upload a saved list. Invalid or unmatched person id records will be ignored. Your api user
        must be shared on the target folder.

        `Args:`
            tbl: parsons.Table
                A parsons table object containing one column of person ids.
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
        `Returns:`
            dict
                Upload results information included the number of matched and saved
                records in your list.
        """

        # Move to cloud storage
        file_name = str(uuid.uuid1())
        url = cloud_storage.post_file(tbl, url_type, file_path=file_name + '.zip', **url_kwargs)
        logger.info(f'Table uploaded to {url_type}.')

        # Create XML
        xml = self.connection.soap_client.factory.create('CreateAndStoreSavedListMetaData')
        xml.SavedList._Name = list_name
        xml.DestinationFolder._ID = folder_id
        xml.SourceFile.FileName = file_name + '.csv'
        xml.SourceFile.FileUrl = url
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

        # VAN errors for this method are not particularly useful or helpful. For that reason, we
        # will check that the folder exists and if the list already exists.
        logger.info('Validating folder id and list name.')
        if folder_id not in [x['folderId'] for x in self.get_folders()]:
            raise ValueError("Folder does not exist or is not shared with API user.")

        if not replace:
            if list_name in [x['name'] for x in self.get_saved_lists(folder_id)]:
                raise ValueError("Saved list already exists. Set to replace argument to True or "
                                 "change list name.")

        # Assemble request
        file_desc.Columns.Column.append(col)
        xml.SourceFile.Format = file_desc

        r = Client.dict(self.connection.soap_client.service.CreateAndStoreSavedList(xml))
        if r:
            logger.info(f"Uploaded {r['ListSize']} records to {r['_Name']} saved list.")
        return r


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
