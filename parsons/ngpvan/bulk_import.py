"""NGPVAN Bulk Import Endpoints"""

from parsons.etl.table import Table
from parsons.utilities import cloud_storage

import logging
import uuid
import csv

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

        r = self.connection.get_request("bulkImportJobs/resources")
        logger.info(f"Found {len(r)} bulk import resources.")
        return r

    def get_bulk_import_job(self, job_id):
        """
        Get a bulk import job status.

        `Args:`
            job_id : int
                The bulk import job id.
        `Returns:`
            dict
                The bulk import job
        """

        r = self.connection.get_request(f"bulkImportJobs/{job_id}")
        logger.info(f"Found bulk import job {job_id}.")
        return r

    def get_bulk_import_job_results(self, job_id):
        """
        Get result file of a bulk upload job. This will include one row
        per record processed as well as the status of each.

        If the job results have not been generated, either due to an error in the
        process or the fact the job is still processing, it will return ``None``.

        `Args:`
            job_id: int
                The bulk import job id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        r = self.get_bulk_import_job(job_id)
        logger.info(f"Bulk Import Job Status: {r['status']}")
        if r["status"] == "Completed":
            return Table.from_csv(r["resultFiles"][0]["url"])

        return None

    def get_bulk_import_mapping_types(self):
        """
        Get bulk import mapping types.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("bulkImportMappingTypes"))
        logger.info(f"Found {tbl.num_rows} bulk import mapping types.")
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

        r = self.connection.get_request(f"bulkImportMappingTypes/{type_name}")
        logger.info(f"Found {type_name} bulk import mapping type.")
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

        r = self.connection.get_request(f"bulkImportMappingTypes/{type_name}/{field_name}/values")
        logger.info(f"Found {type_name} bulk import mapping type field values.")
        return r

    def post_bulk_import(
        self,
        tbl,
        url_type,
        resource_type,
        mapping_types,
        description,
        result_fields=None,
        **url_kwargs,
    ):
        # Internal method to post bulk imports.

        # Move to cloud storage
        file_name = str(uuid.uuid1())
        url = cloud_storage.post_file(
            tbl,
            url_type,
            file_path=file_name + ".zip",
            quoting=csv.QUOTE_ALL,
            **url_kwargs,
        )
        logger.info(f"Table uploaded to {url_type}.")

        # Generate request json
        json = {
            "description": description,
            "file": {
                "columnDelimiter": "csv",
                "columns": [{"name": c} for c in tbl.columns],
                "fileName": file_name + ".csv",
                "hasHeader": "True",
                "hasQuotes": "True",
                "sourceUrl": url,
            },
            "actions": [
                {
                    "resultFileSizeKbLimit": 5000,
                    "resourceType": resource_type,
                    "actionType": "loadMappedFile",
                    "mappingTypes": mapping_types,
                }
            ],
        }

        if result_fields:
            result_fields = [{"name": c} for c in result_fields]
            json["actions"][0]["columnsToIncludeInResultsFile"] = result_fields

        r = self.connection.post_request("bulkImportJobs", json=json)
        logger.info(f"Bulk upload {r['jobId']} created.")
        return r["jobId"]

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
            * - ``canvassedby``
              - No
              - A valid User ID; Required when DateCanvassed is provided
            * - ``contacttypeid``
              - No
              - The method of contact.

        `Args:`
            table: Parsons table
                A Parsons table.
            url_type: str
                The cloud file storage to use to post the file (``S3`` or ``GCS``).
                See :ref:`Cloud Storage <cloud-storage>` for more details.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type. See
                :ref:`Cloud Storage <cloud-storage>` for more details.
        `Returns:`
            int
                The bulk import job id
        """

        return self.post_bulk_import(
            tbl,
            url_type,
            "ContactsActivistCodes",
            [{"name": "ActivistCode"}],
            "Activist Code Upload",
            **url_kwargs,
        )

    def bulk_upsert_contacts(self, tbl, url_type, result_fields=None, **url_kwargs):
        """
        Bulk create or update contact records. Provide a Parsons table of contact data to
        create or update records.

        .. note::
            * The first column of the table must be VANID.
            * The other columns can be a combination of the columns listed below.
              The valid column names also accept permutations with underscores, spaces
              and capitalization (e.g. ``phonenumber`` = ``Phone_Number``).

        **Table Fields**

        .. list-table::
            :widths: 500 100 10
            :header-rows: 1

            * - Column
              - Valid Column Names
              - Notes
            * - VANID
              - ``vanid``
              -
            * - Voter VAN ID
              - ``votervanid``
              - The contact's MyVoters VANID
            * - External ID
              - ``externalid``, ``id``, ``pk``, ``voterbaseid``
              - An external id to be stored.
            * - **PII**
              -
              -
            * - First Name
              - ``fn``, ``firstname``, ``first``
              -
            * - Middle Name
              - ``mn``, ``middlename``, ``middle``
              -
            * - Last Name
              - ``ln``, ``lastname``, ``last``
              -
            * - Date of Birth
              - ``dob``, ``dateofbirth``, ``birthdate``
              - An ISO formatted date
            * - Sex
              - ``sex``, ``gender``
              -
            * - **Physical Address**
              -
              -
            * - Address Line 1
              - ``addressline1``, ``address1``, ``address``
              -
            * - Address Line 2
              - ``addressline2``, ``address2``
              -
            * - Address Line 3
              - ``addressline3``, ``address3``
              -
            * - City
              - ``city``
              -
            * - State Or Province
              - ``state``, ``st``, ``stateorprovince``
              -
            * - Zip or Postal Code
              - ``ziporpostal``, ``postal``, ``postalcode``, ``zip``, ``zipcode``
              -
            * - Country Code
              - ``countrycode``, ``country``
              - A valid two character country code (e.g. ``US``)
            * - Display As Entered
              - ``displayasentered``
              - Required values are ``Y`` and ``N``. Determines if the address is
                processed through address correction.
            * - **Phones**
              -
              -
            * - Cell Phone
              - ``cellphone``, ``cell``
              -
            * - Cell Phone Country Code
              - ``cellcountrycode``, ``cellphonecountrycode``
              - A valid two digit country code (e.g. ``01``)
            * - Home Phone
              - ``homephone``, ``home``, ``phone``
              -
            * - Home Phone Country Code
              - ``homecountrycode``, ``homephonecountrycode``
              -
            * - **Email**
              -
              -
            * - Email
              - ``email``, ``emailaddress``
              -
            * - Other Email
              - ``otheremail``, ``email2``, ``emailaddress2``
              -

        `Args:`
            table: Parsons table
              A Parsons table.
            url_type: str
              The cloud file storage to use to post the file. Currently only ``S3``.
            results_fields: list
              A list of fields to include in the results file.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type. See
                :ref:`Cloud Storage <cloud-storage>` for more details.
        `Returns:`
            int
                The bulk import job id
        """

        tbl = tbl.map_columns(CONTACTS_COLUMN_MAP, exact_match=False)

        return self.post_bulk_import(
            tbl,
            url_type,
            "Contacts",
            [{"name": "CreateOrUpdateContact"}],
            "Create Or Update Contact Records",
            result_fields=result_fields,
            **url_kwargs,
        )

    def bulk_apply_suppressions(self, tbl, url_type, **url_kwargs):
        """
        Bulk apply contact suppression codes.

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
            * - ``suppressionid``
              - Yes
              - A valid suppression id

        `Args:`
            table: Parsons table
                A Parsons table.
            url_type: str
                The cloud file storage to use to post the file (``S3`` or ``GCS``).
                See :ref:`Cloud Storage <cloud-storage>` for more details.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type. See
                :ref:`Cloud Storage <cloud-storage>` for more details.
        `Returns:`
            int
                The bulk import job id
        """

        return self.post_bulk_import(
            tbl,
            url_type,
            "Contacts",
            [{"name": "Suppressions"}],
            "Apply Suppressions",
            **url_kwargs,
        )

    def bulk_apply_canvass_results(self, tbl, url_type, **url_kwargs):
        """
        Bulk apply contact canvass results.

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
            * - ``contacttypeid``
              - Yes
              - Valid Contact Type ID
            * - ``resultid``
              - Yes
              - Valid Contact Result ID
            * - ``datecanvassed``
              - Yes
              - ISO Date Format
            * - ``canvassedby``
              - Yes
              - Valid User ID
            * - ``phone``
              - No
              - Attempted Phone Number
            * - ``countrycode``
              - No
              - Country Code (ISO 3166-1 alpha-2)
            * - ``phonetypeid``
              - No
              - Phone Type
            * - ``phoneoptinstatusid``
              - No
              - SMS Opt-In Status
            * - ``addressid``
              - No
              - The Contact Address ID of the address that was canvassed

        `Args:`
            table: Parsons table
                A Parsons table.
            url_type: str
                The cloud file storage to use to post the file (``S3`` or ``GCS``).
                See :ref:`Cloud Storage <cloud-storage>` for more details.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type. See
                :ref:`Cloud Storage <cloud-storage>` for more details.
        `Returns:`
            int
                The bulk import job id
        """

        return self.post_bulk_import(
            tbl,
            url_type,
            "Contacts",
            [{"name": "CanvassResults"}],
            "Apply Canvass Results",
            **url_kwargs,
        )

    def bulk_apply_contact_custom_fields(self, custom_field_group_id, tbl, url_type, **url_kwargs):
        """
        Bulk apply contact custom fields.

        The table may include the following columns. The first column
        must be ``vanid``.

        .. list-table::
            :widths: 25 25 60
            :header-rows: 1

            * - Column Name
              - Required
              - Description
            * - ``vanid``
              - Yes
              - A valid VANID primary key
            * - ***``CF{CustomFieldID}``
              - Yes
              - At least one custom field column to be loaded associated with the provided
                custom_field_group_id. The column name should be a valid Custom Field ID
                prefixed with ``CF``, i.e. CF123.

        `Args:`
            custom_field_group_id: int
                Valid Custom Contact Field Group ID; must be the parent of
                the provided Custom Field IDs in the file.
            table: Parsons table
                A Parsons table.
            url_type: str
                The cloud file storage to use to post the file (``S3`` or ``GCS``).
                See :ref:`Cloud Storage <cloud-storage>` for more details.
            **url_kwargs: kwargs
                Arguments to configure your cloud storage url type. See
                :ref:`Cloud Storage <cloud-storage>` for more details.
        `Returns:`
            int
                The bulk import job id
        """

        mapping_types = [
            {
                "name": "ApplyContactCustomFields",
                "fieldValueMappings": [
                    {
                        "fieldName": "CustomFieldGroupID",
                        "staticValue": custom_field_group_id,
                    },
                ],
            }
        ]

        return self.post_bulk_import(
            tbl,
            url_type,
            "Contacts",
            mapping_types,
            "Apply Contact Custom Fields",
            **url_kwargs,
        )


# This is a column mapper that is used to accept additional column names and provide
# flexibility for the user.

CONTACTS_COLUMN_MAP = {
    "firstname": ["fn", "first"],
    "middlename": ["mn", "middle"],
    "lastname": ["ln", "last"],
    "dob": ["dateofbirth", "birthdate"],
    "sex": ["gender"],
    "addressline1": ["address", "addressline1", "address1"],
    "addressline2": ["addressline2", "address2"],
    "addressline3": ["addressline3", "address3"],
    "city": [],
    "stateorprovince": ["state", "st"],
    "ziporpostal": ["postal", "postalcode", "zip", "zipcode"],
    "countrycode": ["country"],
    "displayasentered": [],
    "cellphone": ["cell"],
    "cellphonecountrycode": ["cellcountrycode"],
    "phone": ["home", "homephone"],
    "phonecountrycode": ["phonecountrycode"],
    "email": ["emailaddress"],
    "otheremail": ["email2", "emailaddress2"],
}
