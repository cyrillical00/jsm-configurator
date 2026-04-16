"""
Schema definition for JSM request types.
A request type describes a category of ticket users can submit.
"""

CATEGORIES = ["Access", "Hardware", "Software", "Onboarding", "Account", "Other"]

FIELD_TYPES = ["Text", "Text Area", "Dropdown", "Date", "Checkbox", "Number", "Attachment"]

TEAMS = ["IT Ops", "IT Support", "Security", "HR", "Facilities", "Engineering", "Other"]

VISIBILITY_OPTIONS = ["Internal", "External", "Both"]


def empty_request_type(id_val: str) -> dict:
    return {
        "id": id_val,
        "name": "",
        "category": CATEGORIES[0],
        "fields": [],
        "assignee_team": TEAMS[0],
        "visibility": "Both",
    }


def empty_field() -> dict:
    return {
        "name": "",
        "type": "Text",
        "required": True,
    }
