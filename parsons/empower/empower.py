import logging

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons.utilities.datetime import convert_unix_to_readable

logger = logging.getLogger(__name__)

EMPOWER_API_ENDPOINT = "https://api.getempower.com/v1/export"


class Empower:
    """
    Instantiate class.

    Args:
            api_key: str
                The Empower provided API key.The Empower provided Client UUID. Not
                required if ``EMPOWER_API_KEY`` env variable set.
            empower_uri: str
                The URI to access the Empower API. The default is currently set to
                https://api.getempower.com/v1/export. You can set an ``EMPOWER_URI`` env
                variable or use this URI parameter if a different endpoint is necessary.
            cache: boolean
                The Empower API returns all account data after each call. Setting cache
                to ``True`` stores the blob and then extracts Parsons tables for each method.
                Setting cache to ``False`` will download all account data for each method call.

    """

    def __init__(self, api_key=None, empower_uri=None, cache=True):
        self.api_key = check_env.check("EMPOWER_API_KEY", api_key)
        self.empower_uri = (
            check_env.check("EMPOWER_URI", empower_uri, optional=True) or EMPOWER_API_ENDPOINT
        )
        self.headers = {"accept": "application/json", "secret-token": self.api_key}
        self.client = APIConnector(
            self.empower_uri,
            headers=self.headers,
        )
        self.data = None
        self.data = self._get_data(cache)

    def _get_data(self, cache):
        """Gets fresh data from Empower API based on cache setting."""
        if not cache or self.data is None:
            r = self.client.get_request(self.empower_uri)
            logger.info("Empower data downloaded.")
            return r

        else:
            return self.data

    def _empty_obj(self, obj_name):
        """Determine if a dict object is empty."""

        return len(self.data[obj_name]) == 0

    def get_profiles(self):
        """
        Get Empower profiles.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = Table(self.data["profiles"])
        for col in ["createdMts", "lastUsedEmpowerMts", "updatedMts"]:
            tbl.convert_column(col, lambda x: convert_unix_to_readable(x))
        tbl.remove_column("activeCtaIds")  # Get as a method via get_profiles_active_ctas
        return tbl

    def get_profiles_active_ctas(self):
        """
        Get active ctas assigned to Empower profiles.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = Table(self.data["profiles"]).long_table("eid", "activeCtaIds")
        return tbl

    def get_regions(self):
        """
        Get Empower regions.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = Table(self.data["regions"])
        tbl.convert_column("inviteCodeCreatedMts", lambda x: convert_unix_to_readable(x))
        return tbl

    def get_cta_results(self):
        """
        Get Empower call to action results.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        # unpacks answerIdsByPromptId into standalone rows
        tbl = Table(self.data["ctaResults"])
        tbl.convert_column("contactedMts", lambda x: convert_unix_to_readable(x))
        tbl = tbl.unpack_nested_columns_as_rows(
            "answerIdsByPromptId", key="profileEid", expand_original=True
        )
        tbl.unpack_list("answerIdsByPromptId_value", replace=True)
        col_list = [v for v in tbl.columns if v.find("value") != -1]
        tbl.coalesce_columns("answer_id", col_list, remove_source_columns=True)
        tbl.remove_column("uid")
        tbl.remove_column("answers")  # Per docs, this is deprecated.
        return tbl

    def _split_ctas(self):
        """Internal method to split CTA objects into tables."""

        ctas = Table(self.data["ctas"])
        for col in [
            "createdMts",
            "scheduledLaunchTimeMts",
            "updatedMts",
            "activeUntilMts",
        ]:
            ctas.convert_column(col, lambda x: convert_unix_to_readable(x))
        # Get following data as their own tables via their own methods
        ctas.remove_column("regionIds")  # get_cta_regions()
        ctas.remove_column("shareables")  # get_cta_shareables()
        ctas.remove_column("prioritizations")  # get_cta_prioritizations()
        ctas.remove_column("questions")  # This column has been deprecated.

        cta_prompts = ctas.long_table("id", "prompts", prepend=False, retain_original=False)
        cta_prompts.remove_column("ctaId")

        cta_prompt_answers = cta_prompts.long_table("id", "answers", prepend=False)

        return {
            "ctas": ctas,
            "cta_prompts": cta_prompts,
            "cta_prompt_answers": cta_prompt_answers,
        }

    def get_ctas(self):
        """
        Get Empower calls to action.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        return self._split_ctas()["ctas"]

    def get_cta_prompts(self):
        """
        Get Empower calls to action prompts.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        return self._split_ctas()["cta_prompts"]

    def get_cta_prompt_answers(self):
        """
        Get Empower calls to action prompt answers.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        return self._split_ctas()["cta_prompt_answers"]

    def get_cta_regions(self):
        """
        Get a list of regions that each call to active is active in.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = Table(self.data["ctas"]).long_table("id", "regionIds")
        return tbl

    def get_cta_shareables(self):
        """
        Get a list of shareables associated with calls to action.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = Table(self.data["ctas"]).long_table("id", "shareables")
        return tbl

    def get_cta_prioritizations(self):
        """
        Get a list prioritizations associated with calls to action.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = Table(self.data["ctas"]).long_table("id", "prioritizations")
        return tbl

    def get_outreach_entries(self):
        """
        Get outreach entries.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """
        if self._empty_obj("outreachEntries"):
            logger.info("No Outreach Entries found.")
            return Table([])

        tbl = Table(self.data["outreachEntries"])
        for col in [
            "outreachCreatedMts",
            "outreachSnoozeUntilMts",
            "outreachScheduledFollowUpMts",
        ]:
            tbl.convert_column(col, lambda x: convert_unix_to_readable(x))
        return tbl

    def get_full_export(self):
        """
        Get a table of the complete, raw data as returned by the API.
        Meant to facilitate pure ELT pipelines

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = Table([self.data])
        return tbl
