import logging
from typing import Literal, Optional

from scraplib import Scraper

from parsons.ngpvan.activist_codes import ActivistCodes
from parsons.ngpvan.bulk_import import BulkImport
from parsons.ngpvan.canvass_responses import CanvassResponses
from parsons.ngpvan.changed_entities import ChangedEntities
from parsons.ngpvan.codes import Codes
from parsons.ngpvan.contact_notes import ContactNotes
from parsons.ngpvan.custom_fields import CustomFields
from parsons.ngpvan.email import Email
from parsons.ngpvan.events import Events
from parsons.ngpvan.introspection import Introspection
from parsons.ngpvan.locations import Locations
from parsons.ngpvan.people import People
from parsons.ngpvan.printed_lists import PrintedLists
from parsons.ngpvan.saved_lists import ExportJobs, Folders, SavedLists
from parsons.ngpvan.scores import FileLoadingJobs, Scores
from parsons.ngpvan.signups import Signups
from parsons.ngpvan.supporter_groups import SupporterGroups
from parsons.ngpvan.survey_questions import SurveyQuestions
from parsons.ngpvan.targets import Targets
from parsons.ngpvan.van_connector import VANConnector

logger = logging.getLogger(__name__)


class VAN(
    People,
    Events,
    Email,
    SavedLists,
    PrintedLists,
    Folders,
    ExportJobs,
    ActivistCodes,
    CanvassResponses,
    SurveyQuestions,
    Codes,
    Scores,
    FileLoadingJobs,
    SupporterGroups,
    Signups,
    Locations,
    BulkImport,
    ChangedEntities,
    ContactNotes,
    CustomFields,
    Targets,
    Introspection,
):
    """
    Returns the VAN class

    `Args:`
        api_key : str
            A valid api key Not required if ``VAN_API_KEY`` env variable set.
        db: str
            One of ``MyVoters``, ``MyMembers``, ``MyCampaign``, or ``EveryAction``
    `Returns:`
        VAN object
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        db: Optional[Literal["MyVoters", "MyCampaign", "MyMembers", "EveryAction"]] = None,
    ):
        if db == "MyVoters":
            db_code = 0
        elif db in ["MyMembers", "MyCampaign", "EveryAction"]:
            db_code = 1
        else:
            raise KeyError(
                "Invalid database type specified. Pick one of:"
                " MyVoters, MyCampaign, MyMembers, EveryAction."
            )

        session = Scraper()
        session.auth = ("default", api_key + "|" + str(db_code))

        self.connection = VANConnector(session=session, URI="https://api.securevan.com/v4/")

        # The size of each page to return. Currently set to maximum.
        self.page_size = 200
