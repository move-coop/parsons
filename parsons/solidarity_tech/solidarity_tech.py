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
from parsons.solidarity_tech.st_organizations import SolidarityTechOrganizations
from parsons.solidarity_tech.st_pages import SolidarityTechPages
from parsons.solidarity_tech.st_phonebanks import SolidarityTechPhonebanks
from parsons.solidarity_tech.st_scheduled_calls import SolidarityTechScheduledCalls
from parsons.solidarity_tech.st_scheduled_tasks import SolidarityTechScheduledTasks
from parsons.solidarity_tech.st_task_agents import SolidarityTechTaskAgents
from parsons.solidarity_tech.st_task_assignments import SolidarityTechTaskAssignments
from parsons.solidarity_tech.st_team_members import SolidarityTechTeamMembers
from parsons.solidarity_tech.st_text_blasts import SolidarityTechTextBlasts
from parsons.solidarity_tech.st_text_templates import SolidarityTechTextTemplates
from parsons.solidarity_tech.st_textbanks import SolidarityTechTextbanks
from parsons.solidarity_tech.st_texts import SolidarityTechTexts
from parsons.solidarity_tech.st_user_actions import SolidarityTechUserActions
from parsons.solidarity_tech.st_user_lists import SolidarityTechUserLists
from parsons.solidarity_tech.st_user_notes import SolidarityTechUserNotes
from parsons.solidarity_tech.st_user_relationships import SolidarityTechUserRelationships
from parsons.solidarity_tech.st_users import SolidarityTechUsers

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
    SolidarityTechOrganizations,
    SolidarityTechPages,
    SolidarityTechPhonebanks,
    SolidarityTechScheduledCalls,
    SolidarityTechScheduledTasks,
    SolidarityTechTaskAgents,
    SolidarityTechTaskAssignments,
    SolidarityTechTeamMembers,
    SolidarityTechTextBlasts,
    SolidarityTechTextTemplates,
    SolidarityTechTextbanks,
    SolidarityTechTexts,
    SolidarityTechUserActions,
    SolidarityTechUserLists,
    SolidarityTechUserNotes,
    SolidarityTechUserRelationships,
    SolidarityTechUsers,
):
    pass
