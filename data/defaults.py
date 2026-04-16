"""
Life360 example JSM configuration.

Based on the actual JSM setup built at Life360 for a ~900-person remote org over 6 years
of production use. Where a specific value was not recalled with certainty, a reasonable
operational default is used and noted with a comment.
"""

import uuid


def _id():
    return str(uuid.uuid4())


def get_life360_request_types():
    return [
        {
            "id": _id(),
            "name": "Software Access Request",
            "category": "Access",
            "fields": [
                {"name": "Software name", "type": "Text", "required": True},
                {"name": "Business justification", "type": "Text Area", "required": True},
                {"name": "Manager approval", "type": "Text", "required": True},
                {"name": "Start date", "type": "Date", "required": True},
                {"name": "Duration needed", "type": "Dropdown", "required": False},
            ],
            "assignee_team": "IT Ops",
            "visibility": "Both",
        },
        {
            "id": _id(),
            "name": "Hardware Issue",
            "category": "Hardware",
            "fields": [
                {"name": "Device type", "type": "Dropdown", "required": True},
                {"name": "Serial number", "type": "Text", "required": True},
                {"name": "Issue description", "type": "Text Area", "required": True},
                {"name": "Urgency", "type": "Dropdown", "required": True},
            ],
            "assignee_team": "IT Support",
            "visibility": "Both",
        },
        {
            "id": _id(),
            "name": "Account Locked / Password Reset",
            "category": "Account",
            "fields": [
                {"name": "Username or email", "type": "Text", "required": True},
                {"name": "Preferred contact method", "type": "Dropdown", "required": True},
            ],
            "assignee_team": "IT Support",
            "visibility": "Both",
        },
        {
            "id": _id(),
            "name": "New Hire Setup",
            "category": "Onboarding",
            "fields": [
                {"name": "Employee name", "type": "Text", "required": True},
                {"name": "Start date", "type": "Date", "required": True},
                {"name": "Department", "type": "Dropdown", "required": True},
                {"name": "Manager", "type": "Text", "required": True},
                {"name": "Device type", "type": "Dropdown", "required": True},
                {"name": "Software package", "type": "Dropdown", "required": True},
            ],
            "assignee_team": "IT Ops",
            "visibility": "Internal",
        },
        {
            "id": _id(),
            "name": "Offboarding Request",
            "category": "Onboarding",
            "fields": [
                {"name": "Employee name", "type": "Text", "required": True},
                {"name": "Last day", "type": "Date", "required": True},
                {"name": "Manager", "type": "Text", "required": True},
                {"name": "Equipment return method", "type": "Dropdown", "required": True},
            ],
            "assignee_team": "IT Ops",
            "visibility": "Internal",
        },
        {
            "id": _id(),
            "name": "VPN / Remote Access Issue",
            "category": "Access",
            "fields": [
                {"name": "Issue type", "type": "Dropdown", "required": True},
                {"name": "Location", "type": "Text", "required": True},
                {"name": "Device being used", "type": "Text", "required": True},
            ],
            "assignee_team": "IT Support",
            "visibility": "Both",
        },
    ]


def get_life360_sla_tiers():
    return [
        {
            "id": _id(),
            "priority": "P1",
            "description": "Production outage or full loss of access for 10+ users",
            # 15 minutes = 0.25 hours
            "first_response_hours": 0.25,
            "resolution_hours": 4.0,
            "escalation_hours": 2.0,
            "business_hours_only": False,
            "notification_target": "IT Manager, VP Engineering",
        },
        {
            "id": _id(),
            "priority": "P2",
            "description": "Significant impact on a team or key business system",
            "first_response_hours": 1.0,
            "resolution_hours": 8.0,
            "escalation_hours": 4.0,
            "business_hours_only": False,
            "notification_target": "IT Manager",
        },
        {
            "id": _id(),
            "priority": "P3",
            "description": "Single user impacted with a workaround available",
            "first_response_hours": 4.0,
            # 2 business days = 16 hours
            "resolution_hours": 16.0,
            # 1 business day = 8 hours; using 8.0 as a reasonable operational default
            "escalation_hours": 8.0,
            "business_hours_only": True,
            "notification_target": "IT Lead",
        },
        {
            "id": _id(),
            "priority": "P4",
            "description": "How-to question or non-urgent request",
            # 1 business day = 8 hours
            "first_response_hours": 8.0,
            # 5 business days = 40 hours
            "resolution_hours": 40.0,
            # 3 business days = 24 hours
            "escalation_hours": 24.0,
            "business_hours_only": True,
            "notification_target": "IT Lead",
        },
    ]


def get_life360_automation_rules():
    return [
        {
            "id": _id(),
            "name": "P1 Alert",
            "trigger": "New issue created",
            # No request-type condition: fires for any P1 ticket regardless of request type
            "condition": "Priority = P1",
            "condition_request_type": "",
            "actions": [
                "Assign to IT on-call",
                "Post to #it-alerts Slack channel",
                "Send email to IT Manager",
            ],
            "active": True,
            "description": "Immediately alerts IT on-call and management when a P1 ticket is opened.",
        },
        {
            "id": _id(),
            "name": "Auto-assign Access Requests",
            "trigger": "New issue created",
            "condition": "Request type = Software Access Request",
            "condition_request_type": "Software Access Request",
            "actions": [
                "Assign to IT Ops",
                "Set priority to P3 if not already set",
            ],
            "active": True,
            "description": "Routes all software access requests to IT Ops and applies a default P3 priority.",
        },
        {
            "id": _id(),
            "name": "SLA Breach Escalation",
            "trigger": "SLA breached",
            # No request-type condition: fires for any ticket when resolution SLA is breached
            "condition": "SLA clock = Resolution",
            "condition_request_type": "",
            "actions": [
                "Add comment tagging IT Manager",
                "Send Slack message to team lead",
            ],
            "active": True,
            "description": "Escalates any ticket that breaches its resolution SLA to the IT Manager.",
        },
        {
            "id": _id(),
            "name": "New Hire Auto-triage",
            "trigger": "New issue created",
            "condition": "Request type = New Hire Setup",
            "condition_request_type": "New Hire Setup",
            "actions": [
                "Create sub-task: Equipment provisioning (assigned to IT Ops)",
                "Create sub-task: Software provisioning (assigned to IT Ops)",
                "Create sub-task: Access provisioning (assigned to IT Ops)",
            ],
            "active": True,
            "description": "Automatically breaks a New Hire Setup ticket into three parallel sub-tasks.",
        },
        {
            "id": _id(),
            "name": "Okta Lockout Fast-track",
            "trigger": "New issue created",
            "condition": "Request type = Account Locked / Password Reset",
            "condition_request_type": "Account Locked / Password Reset",
            "actions": [
                "Set priority to P2",
                "Assign to IT Support",
                "Post to #it-support Slack channel",
            ],
            "active": True,
            "description": "Prioritizes account lockout tickets and routes them to IT Support immediately.",
        },
        {
            "id": _id(),
            "name": "Stale Ticket Reminder",
            "trigger": "Scheduled",
            # No request-type condition: runs daily across all in-progress tickets
            "condition": "Status = In Progress AND last updated >= 48 hours ago",
            "condition_request_type": "",
            "actions": [
                "Add comment requesting status update",
                "Notify assignee via email",
            ],
            "active": True,
            "description": "Runs daily and nudges assignees on any ticket that has not been updated in 48+ hours.",
        },
    ]


def get_life360_escalation_paths():
    return [
        {
            "id": _id(),
            "name": "P1 Escalation",
            "applies_to_priority": "P1",
            "steps": [
                {
                    "step": 1,
                    "time_hours": 0.0,
                    "action_type": "Page on-call",
                    "target_role": "IT on-call",
                },
                {
                    "step": 2,
                    # 30 minutes = 0.5 hours
                    "time_hours": 0.5,
                    "action_type": "Notify via Slack",
                    "target_role": "IT Manager",
                },
                {
                    "step": 3,
                    "time_hours": 1.0,
                    "action_type": "Notify via Slack",
                    "target_role": "VP Engineering",
                },
            ],
        },
        {
            "id": _id(),
            "name": "P2 Escalation",
            "applies_to_priority": "P2",
            "steps": [
                {
                    "step": 1,
                    "time_hours": 0.0,
                    "action_type": "Notify via Slack",
                    "target_role": "IT Lead",
                },
                {
                    "step": 2,
                    "time_hours": 4.0,
                    "action_type": "Escalate to manager",
                    "target_role": "IT Manager",
                },
            ],
        },
        {
            "id": _id(),
            "name": "P3 Escalation",
            "applies_to_priority": "P3",
            "steps": [
                {
                    "step": 1,
                    "time_hours": 0.0,
                    "action_type": "Notify via email",
                    "target_role": "Assignee",
                },
                {
                    "step": 2,
                    "time_hours": 24.0,
                    "action_type": "Notify via email",
                    "target_role": "IT Lead",
                },
            ],
        },
        {
            "id": _id(),
            "name": "P4 Escalation",
            "applies_to_priority": "P4",
            "steps": [
                {
                    "step": 1,
                    "time_hours": 0.0,
                    "action_type": "Notify via email",
                    "target_role": "Assignee",
                },
                {
                    "step": 2,
                    "time_hours": 24.0,
                    "action_type": "Notify via email",
                    "target_role": "IT Lead",
                },
            ],
        },
    ]


def load_life360_example():
    """Return the complete Life360 example configuration as a dict."""
    return {
        "request_types": get_life360_request_types(),
        "sla_tiers": get_life360_sla_tiers(),
        "automation_rules": get_life360_automation_rules(),
        "escalation_paths": get_life360_escalation_paths(),
    }
