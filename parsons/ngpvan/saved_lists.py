from parsons.etl.table import Table


class SavedLists(object):

    def __init__(self, van_connection):

        # Some sort of test if the van_connection is not present.

        self.connection = van_connection

    def get_saved_lists(self, folder_id=None):
        """
        Get all saved lists

        `Args:`
            folder_id : int
                Optional; the id for a VAN folder. If included returns only
                the saved lists in the folder
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'savedLists'

        return self.connection.request_paginate(
            url, args={'folderId': folder_id})

    def get_saved_list(self, saved_list_id):
        """
        Returns a single saved list object

        `Args:`
            saved_list_id : int
                The saved list id associated with the saved list.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'savedLists/{}'.format(str(saved_list_id))

        return self.connection.request(url)

    def download_saved_list(self, saved_list_id):
        """
        Download a saved list

        `Args:`
            saved_list_id
                The saved list id associated with the saved list.
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

    def folders(self):
        """
        List all folders

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'folders'

        return self.connection.request_paginate(url)

    def folder(self, folder_id):
        """
        Get a single folder

        `Args:`
            folder_id: int
                The folder id associated with the folder.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'folders/{}'.format(str(folder_id))

        return self.connection.request(url)


class ExportJobs(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def export_job_types(self):
        """
        Lists export job types

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'exportJobTypes'

        return self.connection.request_paginate(url)

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

    def export_job(self, export_job_id):
        """
        Returns a single export job

        `Args:`
            export_job_id: int
                Export job id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'exportJobs/{}'.format(str(export_job_id))

        return self.connection.request(url)
