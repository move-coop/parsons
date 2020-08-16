"""NGPVAN Bulk Import Endpoints"""
from parsons.etl.table import Table
from parsons.utilities import cloud_storage

import logging
import uuid

logger = logging.getLogger(__name__)


class BulkImport(object):

    def __init__(self):

        pass

    def get_bulk_import_resources(self):
        """
        Get bulk import resources that available to the user. These define
        the types of bulk imports that you can run. These might include
        ``Contacts``, ``ActivistCodes``, ``ContactsActivistCodes`` and others.

        `Returns:`
            list
                A list of resources.
        """

        r = self.connection.get_request(f'bulkImportJobs/resources')
        logger.info(f'Found {len(r)} bulk import resources.')
        return r

    def get_bulk_import_job(self, job_id):
        """
        Get a bulk import job status.

        .. note::
            The job status may not be immediately avaliable for polling job
            once the job is posted.

        `Args:`
            job_id : int
                The bulk import job id.
        `Returns:`
            dict
                The bulk import job
        """

        r = self.connection.get_request(f'bulkImportJobs/{job_id}')
        logger.info(f'Found bulk import job {job_id}.')
        return r

    def get_bulk_import_job_results(self, job_id):
        """
        Get result file of a bulk upload job. This will include one row
        per record processed as well as the status of each.

        If the job results have not been generated, either due to an error in the
        process or the fact the job is still processing, it will return ``None``.

        `Args:`
            job_id : int
                The bulk import job id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        r = self.get_bulk_import_job(job_id)
        logger.info(f"Bulk Import Job Status: {r['status']}")
        if r['status'] == 'Completed':
            return Table.from_csv(r['resultFiles'][0]['url'])

        return None

    def get_bulk_import_mapping_types(self):
        """
        Get bulk import mapping types.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request('bulkImportMappingTypes'))
        logger.info(f'Found {tbl.num_rows} bulk import mapping types.')
        return tbl

    def get_bulk_import_mapping_type(self, type_name):
        """
        Get a single bulk import mapping type.

        `Args:`
            type_name: str
        `Returns`:
            dict
                A mapping type json
        """

        r = self.connection.get_request(f'bulkImportMappingTypes/{type_name}')
        logger.info(f'Found {type_name} bulk import mapping type.')
        return r

    def get_bulk_import_mapping_type_fields(self, type_name, field_name):
        """
        Get data about a field in a mapping type.

        `Args:`
            type_name: str
                The mapping type name
            field_name: str
                The field name
        `Returns:`
            dict
                A mapping type fields json
        """

        r = self.connection.get_request(f'bulkImportMappingTypes/{type_name}/{field_name}/values')
        logger.info(f'Found {type_name} bulk import mapping type field values.')
        return r

    def post_bulk_import(self, tbl, url_type, resource_type, mapping_types,
                         description, **url_kwargs):
        # Internal method to post bulk imports.

        # Move to cloud storage
        file_name = str(uuid.uuid1())
        url = cloud_storage.post_file(tbl, url_type, file_path=file_name + '.zip', **url_kwargs)
        logger.info(f'Table uploaded to {url_type}.')

        # Generate request json
        json = {"description": description,
                "file": {
                    "columnDelimiter": 'csv',
                    "columns": [{'name': c} for c in tbl.columns],
                    "fileName": file_name + '.csv',
                    "hasHeader": "True",
                    "hasQuotes": "False",
                    "sourceUrl": url},
                "actions": [{"resultFileSizeKbLimit": 5000,
                             "resourceType": resource_type,
                             "actionType": "loadMappedFile",
                             "mappingTypes": mapping_types}]
                }

        r = self.connection.post_request('bulkImportJobs', json=json)
        logger.info(f"Bulk upload {r['jobId']} created.")
        return r['jobId']

    def bulk_apply_activist_codes(self, tbl, url_type, **url_kwargs):
        """
        Bulk apply activist codes.

        The table may include the following columns. The first column
        must be ``vanid``.

        .. list-table::
            :widths: 25 25 50
            :header-rows: 1

            * - Column Name
              - Required
              - Description
            * - ``vanid``
              - Yes
              - A valid VANID primary key
            * - ``activistcodeid``
              - Yes
              - A valid activist code id
            * - ``datecanvassed``
              - No
              - An ISO formatted date
            * - ``contacttypeid``
              - No
              - The method of contact.

        `Args:`
            table: Parsons table
                A Parsons table.
            url_type: str
                The cloud file storage to use to post the file. Currently only ``S3``.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type.
                    * S3 requires ``bucket`` argument and, if not stored as env variables
                      ``aws_access_key`` and ``aws_secret_access_key``.
        `Returns:`
            int
                The bulk import job id
        """

        return self.post_bulk_import(tbl,
                                     url_type,
                                     'ContactsActivistCodes',
                                     [{"name": "ActivistCode"}],
                                     'Activist Code Upload',
                                     **url_kwargs)

    def bulk_update_contacts(self, tbl, url_type, **url_kwargs):
        """
        Bulk update contact records. Provide a Parsons table of contact data to
        update records.

        .. note::
            **The first column of the table must be VANID**. The other columns can be a
            combination of the columns listed below. The valid column names also accept
            permutations with underscores, spaces and capitalization (e.g. ``phonenumber`` =
            ``Phone_Number``).

        **Mailing Address**

        .. list-table::
            :widths: 10 10 20
            :header-rows: 1

            * - Column
              - Valid Column Names
              - Values
            * - Mailing Address
              - ``mailingAddress``, ``address``, ``addressline1``, ``mailaddress``,
                ``mailaddressline1``
              -
            * - Mailing Address Line 2
              - ``mailingaddressline2``, ``address2``, ``mailaddressline2``
              -
            * - Mailing Address Line 3
              - ``mailingaddressline3``, ``address3``, ``mailaddressline3``
              -
            * - Mailing City
              - ``mailingcity``, ``city``, ``mailcity``
              -
            * - Mailing Zip or Postal
              - ``mailingziporpostal``, ``zipcode``, ``mailzipcode``, ``mailzip``, ``zip``
              -
            * - Mailing State or Province
              - ``mailingstateorprovince``, ``mailingstate``, ``st``, ``state``
              - A valid two digit state or province code (e.g. ``IL``)
            * - Mailing Country Code*
              - ``mailingcountrycode``, ``countrycode``, ``country``, ``mailcountry``,
                ``countrycode``
              - A valid two digit country code (e.g. ``US``)
            * - Mailing Display As Entered*
              - ``maildisplayasentered``, ``addressdisplayasentered``, ``displayasentered``
              - ``1`` True, ``0`` False

        **Phones**

        .. list-table::
            :widths: 10 10 20
            :header-rows: 1

            * - Column
              - Valid Column Names
              - Values
            * - Phone
              - ``phone``, ``phonenumber``, ``cell``, ``workphone``, ``homephone``
              -
            * - Phone Type ID*
              - ``phonetype``, ``phonetypeid``
              - ``C`` Cell, ``F`` Fax, ``H`` Home, ``M`` Main, ``O`` Office,
                ``U`` Unknown, ``W`` Work
            * - Country Code
              - ``countrycode``
              - Two character code (e.g. ``US``)
            * - Phone OptIn Status ID
              - ``smsoptin``, ``phoneoptin``, ``optinstatus``
              - ``1``: Opt-In, ``2``: Unknown, ``3``: Opt-Out
            * - Email Subscription Status Id
              - ``emailsubscriptionstatus``, ``emailstatus``, ``subscriptionstatus``
              - ``0``: Unsubscribed, ``1`` Not Subscribed, ``2`` Subscribed

        **Emails**

        .. list-table::
            :widths: 10 10 20
            :header-rows: 1

            * - Column
              - Valid Column Names
              - Values
            * - Email*
              - ``email``, ``emailaddress``
              -
            * - EmailTypeId
              - ``emailtypeid``, ``emailtype``
              - ``1`` Personal, ``2`` Work, ``3`` Other
            * - EmailSubscriptionStatusId
              - ``emailsubscriptionstatus``, ``emailstatus``, ``subscriptionstatus``
              - ``0`` Unsubscribed, ``1`` Not Subscribed, ``2`` Subscribed

        **Custom Fields**

        .. list-table::
            :widths: 10 10 20
            :header-rows: 1

            * - Column
              - Valid Column Names
              - Values
            * - Custom Field Group ID*
              - ``customfieldgroupid``, ``customfield``, ``customfieldid``
              -

        .. [*] Required field if contact type is selected. For example, phonetypeid is
               not required if you are not uploading phone numbers.

        `Args:`
            table: Parsons table
                A Parsons table.
            url_type: str
                The cloud file storage to use to post the file. Currently only ``S3``.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type.
                    * S3 requires ``bucket`` argument and, if not stored as env variables
                      ``aws_access_key`` and ``aws_secret_access_key``.
        `Returns:`
            int
                The bulk import job id
        """

        tbl = tbl.map_columns(COLUMN_MAP, exact_match=False)

        return self.post_bulk_import(tbl,
                                     url_type,
                                     'Contacts',
                                     self.create_mapping_types(tbl),
                                     'Update Contact Records',
                                     **url_kwargs)

    def create_mapping_types(self, tbl):
        # Internal method to generate the correct mapping types based on
        # the columns passed in the table.

        mapping_types = []

        # If one of the following columns is found in the table, then add
        # that mapping type.
        mp = [('Email', 'Email'),
              ('MailingAddress', 'MailingAddress'),
              ('Phone', 'Phones'),
              ('ApplyContactCustomFields', 'CustomFieldGroupId')]

        for col in tbl.columns:
            for i in mp:
                if col.lower() == i[0].lower():
                    mapping_types.append({'name': i[1]})

        return mapping_types


# This is a column mapper that is used to accept additional column names and provide
# flexibility for the user.
COLUMN_MAP = {'MailingAddress': ['address', 'addressline1', 'mailaddress', 'mailaddressline1'],
              'MailingAddressLine2': ['address2', 'mailaddressline2'],
              'MailingAddressLine3': ['address3', 'mailaddressline3'],
              'MailingCity': ['city', 'mailcity'],
              'MailingZipOrPostal': ['zipcode', 'mailzipcode', 'mailzip', 'zip'],
              'MailingCountryCode': ['countrycode', 'country', 'mailcountry', 'countrycode'],
              'MailingDisplayAsEntered': ['maildisplayasentered', 'addressdisplayasentered',
                                          'displayasentered'],
              'MailingStateOrProvince': ['mailingstate', 'st', 'state'],
              'Email': ['email', 'emailaddress'],
              'EmailTypeId': ['emailtype'],
              'EmailSubscriptionStatusId': ['emailsubscriptionstatus', 'emailstatus',
                                            'subscriptionstatus'],
              'Phone': ['phonenumber', 'cell', 'homephone', 'workphone'],
              'CountryCode': ['countrycode'],
              'PhoneTypeID': ['phonetype'],
              'PhoneOptInStatusID': ['smsoptin', 'phoneoptin', 'optinstatus'],
              'IsCellStatusID': ['iscell'],
              'CustomFieldGroupID': ['customfield', 'customfieldid']}
