from typing import Literal

AttendanceType = Literal["yes", "no", "maybe", "waitlisted"]
EventType = Literal["virtual", "in_person"]
FieldType = Literal[
    "input", "textarea", "number", "date", "checkbox", "select", "radios", "checkboxes"
]
InviteType = Literal["sms", "email"]
ScopeType = Literal["Organization", "Chapter"]
InteractionType = Literal["in_person", "call", "text", "email"]
