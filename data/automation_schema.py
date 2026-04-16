"""
Schema definition for JSM automation rules.
Rules define trigger-condition-action chains that run automatically.
"""

TRIGGER_OPTIONS = [
    "New issue created",
    "Issue transitioned",
    "SLA breached",
    "Field changed",
    "Scheduled",
]


def empty_automation_rule(id_val: str) -> dict:
    return {
        "id": id_val,
        "name": "",
        "trigger": TRIGGER_OPTIONS[0],
        "condition": "",
        # Empty string means this rule applies to all request types (general rule).
        # A non-empty value means it only fires when the request type matches.
        "condition_request_type": "",
        "actions": [],
        "active": True,
        "description": "",
    }
