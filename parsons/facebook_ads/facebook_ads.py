import os
import collections
import copy
import logging
from joblib import Parallel, delayed
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.customaudience import CustomAudience
from parsons.etl.table import Table

logger = logging.getLogger(__name__)

FBKeySchema = CustomAudience.Schema.MultiKeySchema

# Max number of custom audience users we're allowed to send in one API call
MAX_FB_AUDIENCE_API_USERS = 10000


class FacebookAds(object):
    """
    Instantiate the FacebookAds class

    `Args:`
        app_id: str
            A Facebook app ID. Required if env var FB_APP_ID is not populated.
        app_secret: str
            A Facebook app secret. Required if env var FB_APP_SECRET is not populated.
        access_token: str
            A Facebook access token. Required if env var FB_ACCESS_TOKEN is not populated.
        ad_account_id: str
            A Facebook ad account ID. Required if env var FB_AD_ACCOUNT_ID isnot populated.
    """

    # The data columns that are valid for creating a custom audience.
    # Feel free to add more variants to capture common column names, as long as they're fairly
    # unambiguous.
    # IMPORTANT - Keep these maps in sync with the comments in the ``add_users_to_custom_audience``
    # method!
    # TODO add support for parsing full names from one column
    KeyMatchMap = {
        FBKeySchema.email: ["email", "email address", "voterbase_email"],
        FBKeySchema.fn: ["fn", "first", "first name", "vb_tsmart_first_name"],
        FBKeySchema.ln: ["ln", "last", "last name", "vb_tsmart_last_name"],
        FBKeySchema.phone: [
            "phone",
            "phone number",
            "cell",
            "landline",
            "vb_voterbase_phone",
            "vb_voterbase_phone_wireless",
        ],
        FBKeySchema.ct: ["ct", "city", "vb_vf_reg_city", "vb_tsmart_city"],
        FBKeySchema.st: [
            "st",
            "state",
            "state code",
            "vb_vf_source_state",
            "vb_tsmart_state",
            "vb_vf_reg_state",
            "vb_vf_reg_cass_state",
        ],
        FBKeySchema.zip: ["zip", "zip code", "vb_vf_reg_zip", "vb_tsmart_zip"],
        FBKeySchema.country: ["country", "country code"],
        # Yes, it's not kosher to confuse gender and sex. However, gender is all that FB
        # supports in their audience targeting.
        FBKeySchema.gen: ["gen", "gender", "sex", "vb_voterbase_gender"],
        FBKeySchema.doby: ["doby", "dob year", "birth year"],
        FBKeySchema.dobm: ["dobm", "dob month", "birth month"],
        FBKeySchema.dobd: ["dobd", "dob day", "birth day"],
    }

    PreprocessKeyMatchMap = {
        # Data in this column will be parsed into the FBKeySchema.dobX keys.
        "DOB YYYYMMDD": ["dob", "vb_voterbase_dob", "vb_tsmart_dob"]
    }

    def __init__(self, app_id=None, app_secret=None, access_token=None, ad_account_id=None):

        try:
            self.app_id = app_id or os.environ["FB_APP_ID"]
            self.app_secret = app_secret or os.environ["FB_APP_SECRET"]
            self.access_token = access_token or os.environ["FB_ACCESS_TOKEN"]
            self.ad_account_id = ad_account_id or os.environ["FB_AD_ACCOUNT_ID"]
        except KeyError as error:
            logger.error(
                "FB Marketing API credentials missing. Must be specified as env vars " "or kwargs"
            )
            raise error

        FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
        self.ad_account = AdAccount("act_%s" % self.ad_account_id)

    @staticmethod
    def _get_match_key_for_column(column):
        # Finds a FB match key for a given table column.

        normalized_col = Table.get_normalized_column_name(column)

        for k, match_list in FacebookAds.KeyMatchMap.items():
            for match in match_list:
                if normalized_col == Table.get_normalized_column_name(match):
                    return k
        return None

    @staticmethod
    def _get_preprocess_key_for_column(column):
        normalized_col = Table.get_normalized_column_name(column)

        for k, match_list in FacebookAds.PreprocessKeyMatchMap.items():
            for match in match_list:
                if normalized_col == Table.get_normalized_column_name(match):
                    return k
        return None

    @staticmethod
    def _preprocess_dob_column(table, column):
        # Parse the DOB column into 3 new columns, and remove the original column
        # TODO Throw an error if the values are not 6 characters long?

        table.add_column(FBKeySchema.doby, lambda row: row[column][:4] if row[column] else None)
        table.add_column(FBKeySchema.dobm, lambda row: row[column][4:6] if row[column] else None)
        table.add_column(FBKeySchema.dobd, lambda row: row[column][6:8] if row[column] else None)
        table.remove_column(column)

    @staticmethod
    def _preprocess_users_table(table):
        # Handle columns that require special parsing
        for column in table.columns:
            preprocess_key = FacebookAds._get_preprocess_key_for_column(column)
            if preprocess_key == "DOB YYYYMMDD":
                FacebookAds._preprocess_dob_column(table, column)
        return table

    @staticmethod
    def _get_first_non_empty_value_from_dict(dict, cols):
        for c in cols:
            if dict[c]:
                return dict[c]
        return None

    @staticmethod
    def get_match_table_for_users_table(users_table):
        """
        Prepared an input table for matching into a FB custom audience, by identifying which
        columns are supported for matching, renaming those columns to what FB expects, and
        cutting away the other columns.

        See ``FacebookAds.create_custom_audience`` for more details.

        `Args`:
            users_table: Table
                The source table for matching

        `Returns:`
            Table
                The prepared table
        """

        # Copy the table to avoid messing up the source table
        t = copy.deepcopy(users_table)

        FacebookAds._preprocess_users_table(t)

        # Map the FB keys to whatever source columns match.
        matched_cols = []
        fb_keys_to_orig_cols = collections.defaultdict(set)
        for c in t.columns:
            match_key = FacebookAds._get_match_key_for_column(c)
            if match_key:
                matched_cols.append(c)
                fb_keys_to_orig_cols[match_key].add(c)

        # Cut the table to just the columns that we can use for matching in FB
        t = t.cut(matched_cols)

        # For each of the FB match keys, create a new column from the source column.
        # If there are more than one source cols for a given FB match key, we'll pick
        # the first non-empty value for each row.

        for fb_key, orig_cols in fb_keys_to_orig_cols.items():
            value_fn = (
                lambda bound_cols: lambda row: FacebookAds._get_first_non_empty_value_from_dict(
                    row, bound_cols
                )
            )(orig_cols)

            # A little trickery here to handle the case where one of the "orig_cols" is already
            # named like the "fb_key".
            t.add_column(fb_key + "_fb_temp_col", value_fn)
            t.remove_column(*orig_cols)
            t.rename_column(fb_key + "_fb_temp_col", fb_key)

        # Convert None values to empty strings. Otherwise the FB SDK chokes.
        petl_table = t.to_petl()
        t = Table(petl_table.replaceall(None, ""))

        return t

    @staticmethod
    def _get_match_schema_and_data(table):
        # Grab the raw data as a list of tuples
        data_list = [row for row in table.data]
        return (table.columns, data_list)

    @staticmethod
    def _is_valid_data_source(data_source):
        valid_sources = [
            CustomAudience.CustomerFileSource.user_provided_only,
            CustomAudience.CustomerFileSource.partner_provided_only,
            CustomAudience.CustomerFileSource.both_user_and_partner_provided,
        ]
        return data_source in valid_sources

    def create_custom_audience(self, name, data_source, description=None):
        """
        Creates a FB custom audience.

        `Args:`
            name: str
                The name of the custom audience
            data_source: str
                One of ``USER_PROVIDED_ONLY``, ``PARTNER_PROVIDED_ONLY``, or
                ``BOTH_USER_AND_PARTNER_PROVIDED``.
                This tells FB whether the data for a custom audience was provided by actual users,
                or acquired via partners. FB requires you to specify.
            description: str
                Optional. The description of the custom audience

        `Returns:`
            ID of the created audience
        """

        if not self._is_valid_data_source(data_source):
            raise KeyError("Invalid data_source provided")

        params = {
            "name": name,
            "subtype": "CUSTOM",
            "description": description,
            "customer_file_source": data_source,
        }

        res = self.ad_account.create_custom_audience(params=params)
        return res["id"]

    def delete_custom_audience(self, audience_id):
        """
        Deletes a FB custom audience.

        `Args:`
            audience_id: str
                The ID of the custom audience to delete.
        """

        CustomAudience(audience_id).api_delete()

    @staticmethod
    def _add_batch_to_custom_audience(
        app_id,
        app_secret,
        access_token,
        audience_id,
        schema,
        batch,
        added_so_far,
        total_rows,
    ):
        # Since this method runs in parallel, we need to re-initialize the Facebook API each time
        # to avoid SSL-related errors. Basically, the FacebookAdsApi python framework isn't
        # built to run in parallel.
        FacebookAdsApi.init(app_id, app_secret, access_token)

        # Note that the FB SDK handles basic normalization and hashing of the data
        CustomAudience(audience_id).add_users(schema, batch, is_raw=True)
        logger.info(f"Added {added_so_far + len(batch)} / {total_rows} users to custom audience...")

    def add_users_to_custom_audience(self, audience_id, users_table):
        """
        Adds user data to a custom audience.

        Each user row in the provided table should have at least one of the supported columns
        defined. Otherwise the row will be ignored. Beyond that, the rows may have any other
        non-supported columns filled out, and those will all be ignored.

        .. list-table::
            :widths: 20 80
            :header-rows: 1

            * - Column Type
              - Valid Column Names
            * - Email Address
              - ``email``, ``email address``, ``voterbase_email``
            * - First Name
              - ``fn``, ``first``, ``first name``, ``vb_tsmart_first_name``
            * - Last Name
              - ``ln``, ``last``, ``last name``, ``vb_tsmart_last_name``
            * - Phone Number
              - ``phone``, ``phone number``, ``cell``, ``landline``, ``vb_voterbase_phone``, ``vb_voterbase_phone_wireless``
            * - City
              - ``ct``, ``city``, ``vb_vf_reg_city``, ``vb_tsmart_city``
            * - State
              - ``st``, ``state``, ``state code``, ``vb_vf_source_state``, ``vb_tsmart_state``, ``vb_vf_reg_state``, ``vb_vf_reg_cass_state``
            * - Zip Code
              - ``zip``, ``zip code``, ``vb_vf_reg_zip``, ``vb_tsmart_zip``
            * - County
              - ``country``, ``country code``
            * - Gender
              - ``gen``, ``gender``, ``sex``, ``vb_vf_reg_zip``
            * - Birth Year
              - ``doby``, ``dob year``, ``birth year``
            * - Birth Month
              - ``dobm``, ``dob month``, ``birth month``
            * - Birth Day
              - ``dobd``, ``dob day``, ``birth day``
            * - Date of Birth
              - ``dob``, ``vb_voterbase_dob``, ``vb_tsmart_dob`` (Format: YYYYMMDD)

        The column names will be normalized before comparing to this list - eg. removing
        whitespace and punctuation - so you don't need to match exactly.

        If more than one of your columns map to a single FB key, then for each row we'll use any
        non-null value for those columns.
        Eg. If you have both ``vb_voterbase_phone`` and ``vb_voterbase_phone_wireless`` (which
        both map to the FB "phone" key), then for each person in your table, we'll try to pick one
        valid phone number.

        For details of the expected data formats for each column type, see
        `Facebook Audience API <https://developers.facebook.com/docs/marketing-api/audiences-api>`_,
        under "Hashing and Normalization for Multi-Key".

        Note that you shouldn't have to do normalization on your data, as long as it's
        reasonably close to what FB expects. Eg. It will convert "Male" to "m", and " JoSH"
        to "josh".

        FB will attempt to match the data to users in their system. You won't be able to find out
        which users were matched. But if you provide enough data, FB will tell you roughly how many
        of them were matched. (You can find the custom audience in your business account at
        https://business.facebook.com).

        Note that because FB's matching is so opaque, it will hide lots of data issues. Eg. if you
        use "United States" instead of "US" for the "country" field, the API will appear to accept
        it, when in reality it is probably ignoring that field. So read the docs if you're worried.

        `Args:`
            audience_id: str
                The ID of the custom audience to delete.
            users_table: obj
                Parsons table

        """  # noqa: E501,E261

        logger.info(
            f"Adding custom audience users from provided table with " f"{users_table.num_rows} rows"
        )

        match_table = FacebookAds.get_match_table_for_users_table(users_table)
        if not match_table.columns:
            raise KeyError(
                "No valid columns found for audience matching. "
                "See FacebookAds.KeyMatchMap for supported columns"
            )

        num_rows = match_table.num_rows
        logger.info(f"Found {num_rows} rows with valid FB matching keys")
        logger.info(f"Using FB matching keys: {match_table.columns}")

        (schema, data) = FacebookAds._get_match_schema_and_data(match_table)

        # Use the FB API to add users, respecting the limit per API call.
        # Process and upload batches in parallel, to improve performance.

        batch_size = MAX_FB_AUDIENCE_API_USERS

        parallel_jobs = (
            delayed(FacebookAds._add_batch_to_custom_audience)(
                self.app_id,
                self.app_secret,
                self.access_token,
                audience_id,
                schema,
                data[i : i + batch_size],
                i,
                num_rows,
            )
            for i in range(0, len(data), batch_size)
        )

        n_jobs = os.environ.get("PARSONS_NUM_PARALLEL_JOBS", 4)
        Parallel(n_jobs=n_jobs)(parallel_jobs)
