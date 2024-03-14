import logging
import surveygizmo
from parsons.etl import Table
from parsons.utilities import check_env

logger = logging.getLogger(__name__)


def sg_compatibility():
    # Create backwards compatibility with SurveyGizmo class

    import os

    if os.getenv("SURVEYGIZMO_API_TOKEN"):
        os.environ["ALCHEMER_API_TOKEN"] = os.getenv("SURVEYGIZMO_API_TOKEN")

    if os.getenv("SURVEYGIZMO_API_TOKEN_SECRET"):
        os.environ["ALCHEMER_API_TOKEN_SECRET"] = os.getenv("SURVEYGIZMO_API_TOKEN_SECRET")

    if os.getenv("SURVEYGIZMO_API_VERSION"):
        os.environ["ALCHEMER_API_VERSION"] = os.getenv("SURVEYGIZMO_API_VERSION")


class Alchemer(object):
    """
    Instantiate Alchemer Class

    `Args:`
        api_token:
            The Alchemer-provided application token. Not required if
            ``ALCHEMER_API_TOKEN`` env variable set.

        api_token:
            The Alchemer-provided application token. Not required if
            ``ALCHEMER_API_TOKEN_SECRET`` env variable set.

        api_version:
            The version of the API that you would like to use. Not required if
            ``ALCHEMER_API_VERSION`` env variable set.
            Default v5

    `Returns:`
        Alchemer Class
    """

    def __init__(self, api_token=None, api_token_secret=None, api_version="v5"):

        sg_compatibility()

        self.api_token = check_env.check("ALCHEMER_API_TOKEN", api_token)
        self.api_token_secret = check_env.check("ALCHEMER_API_TOKEN_SECRET", api_token_secret)
        self.api_version = check_env.check("ALCHEMER_API_VERSION", api_version)

        self._client = surveygizmo.SurveyGizmo(
            api_version=self.api_version,
            api_token=self.api_token,
            api_token_secret=self.api_token_secret,
        )

    def get_surveys(self, page=None):
        """
        Get a table of lists under the account.

        `Args:`
            page : int
                Retrieve a specific page of responses. If not given,
                then all pages are retrieved.

        `Returns:`
            Table Class
        """

        r = self._client.api.survey.list(page)
        data = r["data"]

        if not page:
            while r["page"] < r["total_pages"]:
                r = self._client.api.survey.list(page=(r["page"] + 1))
                data.extend(r["data"])

        tbl = Table(data).remove_column("links")
        tbl.unpack_dict("statistics", prepend=False)

        logger.info(f"Found {tbl.num_rows} surveys.")

        return tbl

    def get_survey_responses(self, survey_id, page=None):
        """
        Get the responses for a given survey.

        `Args:`
            survey_id: string
                The id of survey for which to retrieve the responses.

            page : int
                Retrieve a specific page of responses. If not given,
                then all pages are retrieved.

        `Returns:`
            Table Class
        """

        r = self._client.api.surveyresponse.list(survey_id, page)
        logger.info(f"{survey_id}: {r['total_count']} responses.")
        data = r["data"]

        if not page:
            while r["page"] < r["total_pages"]:
                r = self._client.api.surveyresponse.list(survey_id, page=(r["page"] + 1))
                data.extend(r["data"])

        tbl = Table(data).add_column("survey_id", survey_id, index=1)

        logger.info(f"Found #{tbl.num_rows} responses.")

        return tbl


# Backwards compatibility for old SurveyGizmo class.
SurveyGizmo = Alchemer
