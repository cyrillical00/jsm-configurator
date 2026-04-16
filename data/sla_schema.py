"""
Schema definition for JSM SLA tiers.
Each tier maps a priority level to response and resolution time targets.
"""

PRIORITIES = ["P1", "P2", "P3", "P4"]

COVERAGE_OPTIONS = ["24/7", "Business hours"]


def empty_sla_tier(id_val: str) -> dict:
    return {
        "id": id_val,
        "priority": "P1",
        "description": "",
        "first_response_hours": 1.0,
        "resolution_hours": 8.0,
        "escalation_hours": 4.0,
        "business_hours_only": False,
        "notification_target": "",
    }
