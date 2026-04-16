"""
Export engine: generates Confluence-paste-ready Markdown and structured JSON.

Confluence Markdown notes:
- Confluence's built-in editor supports pasting Markdown via the slash command
  /markdown or the Insert menu. The output here uses standard Markdown (ATX headers,
  GFM tables, fenced code blocks) which Confluence renders correctly via that path.
- Panels / info macros are not included because they require wiki markup mode.
- Tables use standard pipe syntax which Confluence renders after Markdown import.
"""

import json
from datetime import datetime


def _fmt_hours(h: float) -> str:
    """Format a fractional hour value into a readable string."""
    if h == 0:
        return "0 min"
    total_minutes = int(h * 60)
    if total_minutes < 60:
        return f"{total_minutes} min"
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if minutes == 0:
        return f"{hours} hr" if hours == 1 else f"{hours} hrs"
    return f"{hours} hr {minutes} min"


def export_markdown(request_types, sla_tiers, automation_rules, escalation_paths, org_name="") -> str:
    org_label = org_name.strip() if org_name else "Your Organization"
    date_str = datetime.now().strftime("%B %d, %Y")
    lines = []

    lines.append(f"# JSM Configuration Runbook: {org_label}")
    lines.append("")
    lines.append(f"**Generated:** {date_str}")
    lines.append("")
    lines.append(
        "> This is a configuration design document, not a live JSM export. "
        "It describes the intended setup and should be reviewed before implementation."
    )
    lines.append("")

    # ------------------------------------------------------------------
    # Request Types
    # ------------------------------------------------------------------
    lines.append("## Request Types")
    lines.append("")
    lines.append("| Name | Category | Assignee Team | Visibility | Fields |")
    lines.append("|------|----------|---------------|------------|--------|")
    for rt in request_types:
        field_names = ", ".join(f["name"] for f in rt["fields"])
        lines.append(
            f"| {rt['name']} | {rt['category']} | {rt['assignee_team']} "
            f"| {rt['visibility']} | {field_names} |"
        )
    lines.append("")

    for rt in request_types:
        lines.append(f"### {rt['name']}")
        lines.append("")
        lines.append(f"- **Category:** {rt['category']}")
        lines.append(f"- **Assignee Team:** {rt['assignee_team']}")
        lines.append(f"- **Visibility:** {rt['visibility']}")
        lines.append("")
        if rt["fields"]:
            lines.append("**Fields:**")
            lines.append("")
            lines.append("| Field Name | Type | Required |")
            lines.append("|------------|------|----------|")
            for f in rt["fields"]:
                req = "Yes" if f["required"] else "No"
                lines.append(f"| {f['name']} | {f['type']} | {req} |")
            lines.append("")

    # ------------------------------------------------------------------
    # SLA Tiers
    # ------------------------------------------------------------------
    lines.append("## SLA Tiers")
    lines.append("")
    lines.append("| Priority | Description | First Response | Resolution | Escalation Threshold | Coverage |")
    lines.append("|----------|-------------|----------------|------------|----------------------|----------|")
    for tier in sla_tiers:
        coverage = "Business hours" if tier["business_hours_only"] else "24/7"
        lines.append(
            f"| {tier['priority']} | {tier['description']} "
            f"| {_fmt_hours(tier['first_response_hours'])} "
            f"| {_fmt_hours(tier['resolution_hours'])} "
            f"| {_fmt_hours(tier['escalation_hours'])} "
            f"| {coverage} |"
        )
    lines.append("")
    lines.append("**Breach notification targets:**")
    lines.append("")
    for tier in sla_tiers:
        if tier["notification_target"]:
            lines.append(f"- **{tier['priority']}:** {tier['notification_target']}")
    lines.append("")

    # ------------------------------------------------------------------
    # Automation Rules
    # ------------------------------------------------------------------
    lines.append("## Automation Rules")
    lines.append("")
    lines.append("| Rule Name | Trigger | Status |")
    lines.append("|-----------|---------|--------|")
    for rule in automation_rules:
        status = "Active" if rule["active"] else "Inactive"
        lines.append(f"| {rule['name']} | {rule['trigger']} | {status} |")
    lines.append("")

    for rule in automation_rules:
        status = "Active" if rule["active"] else "Inactive"
        lines.append(f"### {rule['name']}")
        lines.append("")
        if rule.get("description"):
            lines.append(rule["description"])
            lines.append("")
        lines.append(f"- **Status:** {status}")
        lines.append(f"- **Trigger:** {rule['trigger']}")
        if rule.get("condition"):
            lines.append(f"- **Condition:** {rule['condition']}")
        lines.append("")
        if rule.get("actions"):
            lines.append("**Actions:**")
            lines.append("")
            for action in rule["actions"]:
                lines.append(f"1. {action}")
            lines.append("")

    # ------------------------------------------------------------------
    # Escalation Paths
    # ------------------------------------------------------------------
    lines.append("## Escalation Paths")
    lines.append("")

    for path in escalation_paths:
        lines.append(f"### {path['name']} ({path['applies_to_priority']})")
        lines.append("")
        if path.get("steps"):
            lines.append("| Step | Trigger | Action | Target |")
            lines.append("|------|---------|--------|--------|")
            for step in sorted(path["steps"], key=lambda s: s["step"]):
                trigger_label = (
                    "Immediately on breach" if step["time_hours"] == 0
                    else f"{_fmt_hours(step['time_hours'])} after breach"
                )
                lines.append(
                    f"| {step['step']} | {trigger_label} "
                    f"| {step['action_type']} | {step['target_role']} |"
                )
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "*Generated by [JSM Configurator](https://github.com/cyrillical00/jsm-configurator). "
        "This document describes a configuration design, not a live JSM export.*"
    )

    return "\n".join(lines)


def export_json(request_types, sla_tiers, automation_rules, escalation_paths, org_name="") -> str:
    """
    Export configuration as structured JSON.

    NOTE: This is NOT a direct Jira API import format. It is a human-readable
    design document in JSON form. Use it as a reference when manually configuring
    your JSM project.
    """
    org_label = org_name.strip() if org_name else "Your Organization"
    payload = {
        "_note": (
            "This is a JSM configuration design document. "
            "It is NOT a direct Jira API import format. "
            "Use this as a reference when manually configuring your JSM project."
        ),
        "org_name": org_label,
        "generated": datetime.now().isoformat(),
        "request_types": [
            {
                "name": rt["name"],
                "category": rt["category"],
                "assignee_team": rt["assignee_team"],
                "visibility": rt["visibility"],
                "fields": rt["fields"],
            }
            for rt in request_types
        ],
        "sla_tiers": [
            {
                "priority": tier["priority"],
                "description": tier["description"],
                "first_response_hours": tier["first_response_hours"],
                "resolution_hours": tier["resolution_hours"],
                "escalation_hours": tier["escalation_hours"],
                "business_hours_only": tier["business_hours_only"],
                "notification_target": tier["notification_target"],
            }
            for tier in sla_tiers
        ],
        "automation_rules": [
            {
                "name": rule["name"],
                "trigger": rule["trigger"],
                "condition": rule.get("condition", ""),
                "condition_request_type": rule.get("condition_request_type", ""),
                "actions": rule["actions"],
                "active": rule["active"],
                "description": rule.get("description", ""),
            }
            for rule in automation_rules
        ],
        "escalation_paths": [
            {
                "name": path["name"],
                "applies_to_priority": path["applies_to_priority"],
                "steps": sorted(path["steps"], key=lambda s: s["step"]),
            }
            for path in escalation_paths
        ],
    }
    return json.dumps(payload, indent=2)
