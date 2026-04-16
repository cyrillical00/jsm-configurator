"""
Validation engine for JSM configurations.

Severity levels:
  Error   - configuration will not behave as expected
  Warning - configuration is incomplete but will function
"""

from typing import List, Dict


def validate(request_types, sla_tiers, automation_rules, escalation_paths) -> List[Dict]:
    """
    Run all validation checks and return a list of findings.

    Each finding is a dict with keys:
      severity: "Error" | "Warning"
      code:     short identifier
      message:  human-readable description
    """
    findings = []

    # ------------------------------------------------------------------
    # 1. Request types with no automation rule referencing them (Warning)
    #    A rule "covers" a request type if it either (a) has a matching
    #    condition_request_type or (b) has no condition_request_type at all
    #    (i.e. it is a general rule that applies to every ticket).
    # ------------------------------------------------------------------
    active_rules = [r for r in automation_rules if r.get("active", True)]
    has_general_rule = any(r["condition_request_type"] == "" for r in active_rules)

    for rt in request_types:
        explicitly_covered = any(
            r["condition_request_type"] == rt["name"] for r in active_rules
        )
        if not explicitly_covered and not has_general_rule:
            findings.append(
                {
                    "severity": "Warning",
                    "code": "RT_NO_RULE",
                    "message": (
                        f"Request type '{rt['name']}' is not referenced by any "
                        "active automation rule. Tickets of this type will not be "
                        "automatically routed or prioritized."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # 2. SLA tiers with no corresponding escalation path (Warning)
    # ------------------------------------------------------------------
    path_priorities = {p["applies_to_priority"] for p in escalation_paths}
    for tier in sla_tiers:
        if tier["priority"] not in path_priorities:
            findings.append(
                {
                    "severity": "Warning",
                    "code": "SLA_NO_ESCALATION",
                    "message": (
                        f"SLA tier '{tier['priority']}' has no escalation path defined. "
                        "Breached tickets at this priority will not have a clear escalation chain."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # 3. Automation rules referencing a request type not in the list (Error)
    # ------------------------------------------------------------------
    rt_names = {rt["name"] for rt in request_types}
    for rule in automation_rules:
        ref = rule.get("condition_request_type", "")
        if ref and ref not in rt_names:
            findings.append(
                {
                    "severity": "Error",
                    "code": "RULE_UNKNOWN_RT",
                    "message": (
                        f"Automation rule '{rule['name']}' references request type "
                        f"'{ref}', which does not exist in the request types list."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # 4. Automation rules with no action defined (Error)
    # ------------------------------------------------------------------
    for rule in automation_rules:
        if not rule.get("actions"):
            findings.append(
                {
                    "severity": "Error",
                    "code": "RULE_NO_ACTION",
                    "message": (
                        f"Automation rule '{rule['name']}' has no actions defined. "
                        "This rule will trigger but do nothing."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # 5. Escalation path steps with non-ascending time triggers (Error)
    # ------------------------------------------------------------------
    for path in escalation_paths:
        steps = sorted(path.get("steps", []), key=lambda s: s["step"])
        for i in range(1, len(steps)):
            prev_t = steps[i - 1]["time_hours"]
            curr_t = steps[i]["time_hours"]
            if curr_t <= prev_t:
                findings.append(
                    {
                        "severity": "Error",
                        "code": "ESC_NONASCENDING",
                        "message": (
                            f"Escalation path '{path['name']}': step {steps[i]['step']} "
                            f"has a time trigger ({curr_t}h) that is not greater than "
                            f"the previous step ({prev_t}h). Steps must be in ascending order."
                        ),
                    }
                )

    # ------------------------------------------------------------------
    # 6. SLA tiers where resolution time is shorter than first response (Error)
    # ------------------------------------------------------------------
    for tier in sla_tiers:
        if tier["resolution_hours"] < tier["first_response_hours"]:
            findings.append(
                {
                    "severity": "Error",
                    "code": "SLA_RESOLUTION_TOO_SHORT",
                    "message": (
                        f"SLA tier '{tier['priority']}': resolution time "
                        f"({tier['resolution_hours']}h) is shorter than first response time "
                        f"({tier['first_response_hours']}h). This is not achievable."
                    ),
                }
            )

    return findings
