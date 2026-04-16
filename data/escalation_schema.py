"""
Schema definition for JSM escalation paths.
Each path defines the sequence of notifications triggered after an SLA breach.
"""

ACTION_TYPES = [
    "Notify via email",
    "Notify via Slack",
    "Notify via phone",
    "Page on-call",
    "Escalate to manager",
    "Create bridge call",
]

ROLE_OPTIONS = [
    "Assignee",
    "IT Support",
    "IT Ops",
    "IT Lead",
    "IT Manager",
    "IT on-call",
    "VP Engineering",
    "CTO",
    "HR",
    "Security",
]


def empty_escalation_path(id_val: str) -> dict:
    return {
        "id": id_val,
        "name": "",
        "applies_to_priority": "P1",
        "steps": [],
    }


def empty_step(step_num: int) -> dict:
    return {
        "step": step_num,
        "time_hours": 0.0,
        "action_type": ACTION_TYPES[0],
        "target_role": ROLE_OPTIONS[0],
    }
