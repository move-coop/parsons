import logging

from parsons.solidarity_tech.solidarity_tech_activities import SolidarityTechActivities
from parsons.solidarity_tech.solidarity_tech_agent_assignments import SolidarityTechAgentAssignments
from parsons.solidarity_tech.solidarity_tech_automation_enrollments import (
    SolidarityTechAutomationEnrollments,
)
from parsons.solidarity_tech.solidarity_tech_calls import SolidarityTechCalls
from parsons.solidarity_tech.solidarity_tech_chapter_phone_numbers import (
    SolidarityTechChapterPhoneNumbers,
)
from parsons.solidarity_tech.solidarity_tech_chapters import SolidarityTechChapters
from parsons.solidarity_tech.solidarity_tech_custom_user_properties import (
    SolidarityTechCustomUserProperties,
)
from parsons.solidarity_tech.solidarity_tech_donation_charges import SolidarityTechDonationCharges
from parsons.solidarity_tech.solidarity_tech_email_blasts import SolidarityTechEmailBlasts
from parsons.solidarity_tech.solidarity_tech_email_senders import SolidarityTechEmailSenders
from parsons.solidarity_tech.solidarity_tech_emails import SolidarityTechEmails
from parsons.solidarity_tech.solidarity_tech_event_attendances import SolidarityTechEventAttendances
from parsons.solidarity_tech.solidarity_tech_event_rsvps import SolidarityTechEventRSVPs
from parsons.solidarity_tech.solidarity_tech_event_sessions import SolidarityTechEventSessions

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
):
    pass
