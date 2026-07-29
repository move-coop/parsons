import logging

from parsons.solidarity_tech.st_activities import SolidarityTechActivities
from parsons.solidarity_tech.st_agent_assignments import SolidarityTechAgentAssignments
from parsons.solidarity_tech.st_automation_enrollments import SolidarityTechAutomationEnrollments
from parsons.solidarity_tech.st_calls import SolidarityTechCalls
from parsons.solidarity_tech.st_chapter_phone_numbers import SolidarityTechChapterPhoneNumbers
from parsons.solidarity_tech.st_chapters import SolidarityTechChapters
from parsons.solidarity_tech.st_custom_user_properties import SolidarityTechCustomUserProperties
from parsons.solidarity_tech.st_donation_charges import SolidarityTechDonationCharges
from parsons.solidarity_tech.st_email_blasts import SolidarityTechEmailBlasts
from parsons.solidarity_tech.st_email_senders import SolidarityTechEmailSenders
from parsons.solidarity_tech.st_emails import SolidarityTechEmails
from parsons.solidarity_tech.st_event_attendances import SolidarityTechEventAttendances
from parsons.solidarity_tech.st_event_rsvps import SolidarityTechEventRSVPs
from parsons.solidarity_tech.st_event_sessions import SolidarityTechEventSessions
from parsons.solidarity_tech.st_events import SolidarityTechEvents
from parsons.solidarity_tech.st_field_survey_urls import SolidarityTechFieldSurveyURLs

logger = logging.getLogger(__name__)


class SolidarityTech(
    SolidarityTechActivities,
    SolidarityTechAgentAssignments,
    SolidarityTechAutomationEnrollments,
    SolidarityTechCalls,
    SolidarityTechChapterPhoneNumbers,
    SolidarityTechChapters,
    SolidarityTechCustomUserProperties,
    SolidarityTechDonationCharges,
    SolidarityTechEmailBlasts,
    SolidarityTechEmailSenders,
    SolidarityTechEmails,
    SolidarityTechEventAttendances,
    SolidarityTechEventRSVPs,
    SolidarityTechEventSessions,
    SolidarityTechEvents,
    SolidarityTechFieldSurveyURLs,
):
    pass
