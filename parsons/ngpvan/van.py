import logging
from parsons.ngpvan.events import Events
from parsons.ngpvan.email import Email
from parsons.ngpvan.van_connector import VANConnector
from parsons.ngpvan.people import People
from parsons.ngpvan.saved_lists import SavedLists, Folders, ExportJobs
from parsons.ngpvan.activist_codes import ActivistCodes
from parsons.ngpvan.canvass_responses import CanvassResponses
from parsons.ngpvan.survey_questions import SurveyQuestions
from parsons.ngpvan.supporter_groups import SupporterGroups
from parsons.ngpvan.codes import Codes
from parsons.ngpvan.scores import Scores, FileLoadingJobs
from parsons.ngpvan.signups import Signups
from parsons.ngpvan.locations import Locations
from parsons.ngpvan.bulk_import import BulkImport
from parsons.ngpvan.changed_entities import ChangedEntities
from parsons.ngpvan.contact_notes import ContactNotes
from parsons.ngpvan.custom_fields import CustomFields
from parsons.ngpvan.targets import Targets
from parsons.ngpvan.printed_lists import PrintedLists

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
):
    """
    Returns the VAN class

    `Args:`
        api_key : str
            A valid api key Not required if ``VAN_API_KEY`` env variable set.
        auth_name: str
            Should not pass this argument
        db: str
            One of ``MyVoters``, ``MyMembers``, ``MyCampaign``, or ``EveryAction``
        uri: str
            Base uri to make api calls.
        raise_for_status: boolean
            Raise excection when encountering a 4XX or 500 error.
    `Returns:`
        VAN object
    """

    def __init__(self, api_key=None, auth_name="default", db=None, raise_for_status=True):

        self.connection = VANConnector(api_key=api_key, db=db)
        self.api_key = api_key
        self.db = db

        # The size of each page to return. Currently set to maximum.
        self.page_size = 200
