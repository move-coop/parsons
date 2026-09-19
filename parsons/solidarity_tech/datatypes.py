"""Types, Enums, and TypedDicts for known Solidarity Tech values."""

from __future__ import annotations

import numbers
from enum import Enum
from typing import Any, Literal, TypedDict

from typing_extensions import NotRequired, Required

from parsons.utilities.api_connector import _JsonType

# Type Aliases

CompareValueType = str | numbers.Rational | bool


# Enums


class AttendanceStatus(str, Enum):
    """Attendance statuses for an event RSVP."""

    YES = "yes"
    NO = "no"
    MAYBE = "maybe"
    WAITLISTED = "waitlisted"


class EventType(str, Enum):
    """Event types for a Solidarity Tech event."""

    VIRTUAL = "virtual"
    IN_PERSON = "in_person"
    HYBRID = "hybrid"


class FieldType(str, Enum):
    """Field types for Solidarity Tech user properties."""

    INPUT = "input"
    TEXT_AREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    CHECKBOX = "checkbox"
    SELECT = "select"
    RADIOS = "radios"
    CHECKBOXES = "checkboxes"


class InviteType(str, Enum):
    """Methods used to invite Solidarity Tech team members."""

    SMS = "sms"
    EMAIL = "email"


class ScopeType(str, Enum):
    """Scopes for Solidarity Tech records."""

    ORGANIZATION = "Organization"
    CHAPTER = "Chapter"


class InteractionType(str, Enum):
    """Types of interactions recorded in Solidarity Tech user notes."""

    IN_PERSON = "in_person"
    CALL = "call"
    TEXT = "text"
    EMAIL = "email"


# TypedDicts (Metadata)


class Metadata(TypedDict):
    """Standard metadata dictionary returned by the SolidarityTech API."""

    total_count: int
    limit: int
    offset: int


class ActivityMetadata(TypedDict, total=False):
    """Metadata returned when looking up activities."""

    total_count: int
    limit: Required[int]
    offset: Required[int]
    cursor: int
    next_cursor: int


class UserMergeMetadata(TypedDict):
    """Metadata returned when merging users."""

    message: str
    primary_user_id: int
    merged_user_ids: list[int]
    merged_count: int
    not_found_user_ids: NotRequired[list[int]]


class UserDeleteMetadata(TypedDict):
    """Metadata returned when deleting a user."""

    message: str
    id: NotRequired[int]


# TypedDicts (Component / Sub-types First)


class UserPropertyDataValue(TypedDict):
    """Data representing a single known value for a custom user property."""

    label: dict[str, _JsonType]
    value: str


class ActionData(TypedDict):
    """Data representing the action taken by a user as part of an activity."""

    id: int
    user_id: int
    agent_user_id: NotRequired[int]
    field_type: NotRequired[str]
    old_value: NotRequired[str]
    new_value: NotRequired[str]
    data_import_id: NotRequired[int]
    created_at: str
    updated_at: str


class TranscriptData(TypedDict, total=False):
    """Data representing a transcript of a call."""

    summary: str
    rating: int
    sentiment: str
    engagement_analysis: str
    engagement_analysis_justification: str


class DonationChargeDataChapter(TypedDict):
    """Data representing which chapter a donation charge was made to."""

    id: int
    name: str


class DonationChargeDataUser(TypedDict):
    """Data representing a user who made a donation charge."""

    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: str
    created_at: str
    address1: NotRequired[str]
    address2: NotRequired[str]
    city: NotRequired[str]
    state: NotRequired[str]
    zip_code: NotRequired[str]
    country_name: NotRequired[str]


class DonationChargeDataActionPage(TypedDict):
    """Data representing the page where a donation charge was made."""

    id: int
    title: str
    url_slug: str


class AddressData(TypedDict, total=False):
    """Data representing a user's address."""

    address1: str
    address2: str
    city: str
    state: str
    zip_code: str
    country: str


class TargetRule(TypedDict):
    """Targeting rule for email blast targeting parameters."""

    id: str
    type: str
    input: FieldType
    value: list[str]
    operator: str


class TargetParam(TypedDict):
    """Parameters for targeting an email blast."""

    rules: TargetRule


class EventRSVPUserData(TypedDict):
    """Data representing a user RSVPing to an event."""

    first_name: str
    last_name: str
    email: NotRequired[str]
    phone: NotRequired[str]


class LocationCoordinatesData(TypedDict):
    """Data returned for the coordinates of a location."""

    lat: float
    lng: float


class LocationComponentsData(TypedDict):
    """Data returned for the components of a location."""

    long_name: str
    short_name: str
    types: list[str]


class LocationDataData(TypedDict, total=False):
    """Data returned for the location data of an event session."""

    components: LocationComponentsData
    coordinates: LocationCoordinatesData
    address_city: str
    full_address: str
    address_state: str
    address_line_1: str
    address_line_2: str
    address_country: str
    address_postal_code: str


class EventSessionHostData(TypedDict):
    """Data representing a user RSVPing to an event."""

    id: str
    first_name: str
    last_name: str


class AutomationStatusData(TypedDict, total=False):
    """Data representing the status of the event's automated communications."""

    rsvp_confirmation_email: bool
    rsvp_confirmation_text: bool
    day_before_email_reminder: bool
    day_before_text_reminder: bool
    day_of_email_reminder: bool
    day_of_text_reminder: bool
    ten_min_before_text_reminder: bool
    post_event_survey_email: bool
    post_event_survey_text: bool


class AssessmentStatusData(TypedDict):
    """Data representing the status of an assessment."""

    key: str
    color: str
    label: str
    description: str


# Data representing a form element on a page
# The format of this has to be different because "class" is a reserved keyword in Python
FormData = TypedDict(
    "FormData",
    {
        "hint": dict[str, str],
        "name": Required[str],
        "show": Required[str],
        "type": Required[str],
        "class": Required[str],
        "label": dict[str, str],
        "style": Required[str],
        "default": Any,
        "options": list[Any],
        "disabled": Any,
    },
    total=False,
)


# --- TypedDicts (Main Entities) ---


class UserPropertyData(TypedDict):
    """Data returned for a custom user property."""

    id: int
    name: str
    key: str
    field_type: FieldType
    options: NotRequired[list[UserPropertyDataValue]]
    scope_id: NotRequired[int]
    scope_type: NotRequired[ScopeType]


class ActivityData(TypedDict):
    """Data returned for an activity."""

    id: int
    user_id: int
    name: str
    actionable_id: int
    actionable_type: str
    action: ActionData
    created_at: str
    updated_at: str


class AgentAssignmentData(TypedDict):
    """Data returned for an agent assignment."""

    id: int
    agent_user_id: int
    user_id: int
    created_at: str
    is_active: bool


class CallData(TypedDict, total=False):
    """Data returned for a call."""

    id: Required[int]
    user_id: Required[int]
    chapter_id: int
    direction: Required[str]
    from_number: str
    to_number: str
    phonebank_id: int
    agent_user_id: int
    notes: str
    duration: Required[int]
    picked_up: Required[bool]
    left_voicemail: Required[bool]
    twilio_call_sid: Required[str]
    created_at: Required[str]
    ended_at: str
    transcription: TranscriptData


class ChapterData(TypedDict, total=False):
    """Data returned for a chapter."""

    id: Required[int]
    name: Required[str]
    assigned_user_count: int
    logo_url: str
    organization_id: Required[int]
    chapter_phone_number: str
    calendar_feed_url: str


class DonationChargeData(TypedDict):
    """Data returned for a donation charge."""

    id: int
    amount: int
    created_at: str
    updated_at: str
    success: bool
    refunded: bool
    receipt_number: str
    hash_id: str
    processing_fee_cents: NotRequired[int]
    external_donation_id: NotRequired[str]
    external_donation_date: NotRequired[str]
    is_external: bool
    amount_in_dollars: str
    currency: str
    currency_symbol: str
    receipt_url: str
    brand: str
    last4: str
    json: dict[str, _JsonType]
    user: DonationChargeDataUser
    action_page: DonationChargeDataActionPage
    chapter: DonationChargeDataChapter


# The format of this has to be different because "from" is a reserved keyword in Python
EmailSenderData = TypedDict(
    "EmailSenderData",
    {
        "id": int,
        "name": str,
        "email": str,
        "from": str,
        "default_for_scope": bool,
        "scope_type": str,
        "scope_id": int,
        "created_at": str,
    },
)


class FieldSurveyURL(TypedDict):
    """Data returned for a survey URL."""

    url: str
    expires_at: str


class QueryRule(TypedDict):
    """Specific query rule for filtering users."""

    id: str
    type: str
    operator: str
    value: CompareValueType | list[CompareValueType]


class QueryParams(TypedDict):
    """Query parameters for filtering users."""

    condition: Literal["AND", "OR"]
    valid: bool
    rules: list[QueryRule]


class UserRelationshipData(TypedDict):
    """Data returned for a user relationship."""

    id: str
    text: str


class UserData(TypedDict):
    """Data returned for a single user."""

    id: int
    hash_id: str
    phone_number: NotRequired[str]
    email: NotRequired[str]
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    alternate_name: NotRequired[str]
    preferred_language: str
    second_language: NotRequired[str]
    chapter_id: int
    chapter_ids: list[int]
    branch_id: NotRequired[int]
    created_at: str
    custom_user_properties: dict[str, str | list[str]]
    address: AddressData
    sms_permission: bool
    call_permission: bool
    email_permission: bool
    other_emails: list[str]
    other_phone_numbers: list[str]


class ChapterPhoneNumberData(TypedDict):
    """Data returned for a single chapter phone number."""

    id: int
    phone_number: str
    assigned_user_count: int
    chapters: list[ChapterData]
    created_at: str


# The format of this has to be different because "from" is a reserved keyword in Python
EmailBlastData = TypedDict(
    "EmailBlastData",
    {
        "id": int,
        "name": str,
        "target_parameters": TargetParam,
        "subject": dict[str, str],
        "content": dict[str, str],
        "attachments": dict[str, str],
        "from": str,
        "email_sender_id": int,
        "reply_to": str,
        "email_wrapper_id": int,
        "supported_languages": list[str],
        "track_opens": bool,
        "track_clicks": bool,
        "limit_sends": NotRequired[int],
        "is_valid": bool,
        "scheduled_to_send_at": NotRequired[str],
        "is_send_in_progress": bool,
        "finished_delivering_at": NotRequired[str],
        "target_count_at_send_time": NotRequired[int],
        "campaign_tags": NotRequired[list[str]],
        "created_at": str,
        "results": dict[str, _JsonType],
    },
)


class SentEmailData(TypedDict):
    """Data returned after successfully sending a one-off email."""

    message: str
    user_id: int
    to: str
    subject: str
    email_sender_id: int


class EventAttendanceData(TypedDict):
    """Data returned for an event attendance record."""

    id: int
    event_id: int
    event_session_id: int
    user_id: int
    attended: bool
    created_at: str


class EventRSVPData(TypedDict):
    """Data returned for an event rsvp record."""

    id: int
    event_id: int
    event_session_id: int
    user_id: int
    user_details: (
        EventRSVPUserData | dict[str, _JsonType]
    )  # TODO(bmos): add all fields to EventRSVPUserData
    is_attending: str
    is_confirmed: bool
    confirmed_at: NotRequired[str]
    confirmed_by_agent_id: NotRequired[int]
    unconfirmed_at: NotRequired[str]
    unconfirmed_by_agent_id: NotRequired[int]
    confirmation_source: NotRequired[str]
    mobilize_event_task_id: NotRequired[int]
    agent_user_id: NotRequired[int]
    source: NotRequired[str]
    source_system: NotRequired[str]
    cancel_rsvp_url: str
    confirm_rsvp_url: str
    created_at: str
    updated_at: str


class EventSessionData(TypedDict, total=False):
    """Data returned for an event session record."""

    id: Required[int]
    mobilize_event_id: int
    start_time: Required[str]
    end_time: Required[str]
    title: Required[str]
    created_at: Required[str]
    updated_at: Required[str]
    location_name: str
    location_data: Required[LocationDataData]
    lonlat: str
    location_address: str
    show_rsvp_bar: bool
    show_title_in_form: bool
    max_capacity: int
    note: str
    tags: list[str]
    zoom_account_id: Any
    zoom_meeting_id: Any
    zoom_meeting_data: Any
    zoom_join_before_host: bool
    zoom_attendance_synced_at: str
    source_calendar_item_id: Any
    event_type: EventType
    paired_meci_id: Any
    recurring_schedule_id: Any
    mobilize_event_task_id: int
    host_user_ids: list[int]
    rsvp_count: Required[int]
    attendance_count: Required[int]
    host_tools_url: Required[str]
    primary_session_id: int
    city_state_label: str
    hosts: list[EventSessionHostData]


class EventData(TypedDict, total=False):
    """Data returned for an event record."""

    id: Required[int]
    title: Required[str]
    scope_id: Required[int]
    scope_type: Required[ScopeType]
    event_type: Required[EventType]
    location_name: str
    location_data: LocationDataData
    tags: list[str]
    campaign_tags: list[str]
    event_sessions: list[EventSessionData]
    event_page_url: str
    event_page_id: int
    image_url: str
    description: str
    hide_address_until_rsvp: Required[bool]
    show_in_web_calendars: Required[bool]
    accessibility_info: str
    waitlist_enabled: Required[bool]
    automation_status: Required[AutomationStatusData]
    primary_event_id: Required[int]
    is_co_hosted_mirror: Required[bool]
    internal_co_host_chapters: list[int]
    created_at: Required[str]


class OrganizationData(TypedDict):
    """Data returned for an organization record."""

    id: int
    name: str
    image_url: NotRequired[str]
    parent_organization_id: NotRequired[int]
    default_language: str
    supported_languages: list[str]
    assessment_statuses: list[AssessmentStatusData]


class PageData(TypedDict):
    """Data returned for a page record."""

    id: int
    type: str
    url_slug: str
    name: str
    website_id: int
    is_published: bool
    full_url: str
    scope_id: int
    scope_type: ScopeType
    supported_languages: str
    follow_up: dict[str, _JsonType]
    confirmations: dict[str, _JsonType]
    admin_notifications: dict[str, _JsonType]
    requires_user: bool
    always_hide_primary_nav: bool
    always_hide_footer: bool
    allow_multiple_responses: bool
    form: list[FormData]
    description: str
    campaign_tags: list[str]
    created_at: str
    action_count: NotRequired[int]
    action_goal: NotRequired[int]


class PhonebankData(TypedDict):
    """Data returned for a phonebank record."""

    # TODO(bmos): Fill this in.
    attempts: NotRequired[int]
    contacted: NotRequired[int]
    reached: NotRequired[int]


class ScheduledCallData(TypedDict):
    """Data returned for a scheduled call record."""

    user_id: int
    agent_user_id: NotRequired[int]
    call_time: str
    created_at: str
