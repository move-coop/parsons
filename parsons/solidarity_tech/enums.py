"""Enums for known Solidarity Tech values."""

from __future__ import annotations

from enum import Enum


class AttendanceStatus(Enum):
    """Attendance statuses for an event RSVP."""

    YES = "yes"
    NO = "no"
    MAYBE = "maybe"
    WAITLISTED = "waitlisted"


class EventType(Enum):
    """Event types for a Solidarity Tech event."""

    VIRTUAL = "virtual"
    IN_PERSON = "in_person"
    HYBRID = "hybrid"


class FieldType(Enum):
    """Field types for Solidarity Tech user properties."""

    INPUT = "input"
    TEXT_AREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    CHECKBOX = "checkbox"
    SELECT = "select"
    RADIOS = "radios"
    CHECKBOXES = "checkboxes"


class InviteType(Enum):
    """Methods used to invite Solidarity Tech team members."""

    SMS = "sms"
    EMAIL = "email"


class ScopeType(Enum):
    """Scopes for Solidarity Tech records."""

    ORGANIZATION = "Organization"
    CHAPTER = "Chapter"


class InteractionType(Enum):
    """Types of interactions recorded in Solidarity Tech user notes."""

    IN_PERSON = "in_person"
    CALL = "call"
    TEXT = "text"
    EMAIL = "email"
