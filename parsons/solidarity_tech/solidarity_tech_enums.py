from enum import Enum


class AttendanceStatus(Enum):
    YES = "yes"
    NO = "no"
    MAYBE = "maybe"
    WAITLISTED = "waitlisted"


class EventType(Enum):
    VIRTUAL = "virtual"
    IN_PERSON = "in_person"
    HYBRID = "hybrid"


class FieldType(Enum):
    INPUT = "input"
    TEXT_AREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    CHECKBOX = "checkbox"
    SELECT = "select"
    RADIOS = "radios"
    CHECKBOXES = "checkboxes"


class InviteType(Enum):
    SMS = "sms"
    EMAIL = "email"


class ScopeType(Enum):
    ORGANIZATION = "Organization"
    CHAPTER = "Chapter"


class InteractionType(Enum):
    IN_PERSON = "in_person"
    CALL = "call"
    TEXT = "text"
    EMAIL = "email"
