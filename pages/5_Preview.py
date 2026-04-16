"""
Page 5: Preview

Full read-only view of the complete configuration with inline validation results.
"""

import streamlit as st

from engine.validator import validate
from data.sla_schema import PRIORITIES


if "request_types" not in st.session_state:
    st.session_state.request_types = []
if "sla_tiers" not in st.session_state:
    st.session_state.sla_tiers = []
if "automation_rules" not in st.session_state:
    st.session_state.automation_rules = []
if "escalation_paths" not in st.session_state:
    st.session_state.escalation_paths = []


PRIORITY_COLORS = {
    "P1": "#ff4444",
    "P2": "#ffaa00",
    "P3": "#00aaff",
    "P4": "#00ff88",
}

CATEGORY_COLORS = {
    "Access": "#00ff88",
    "Hardware": "#00aaff",
    "Software": "#aa88ff",
    "Onboarding": "#ffaa00",
    "Account": "#ff6688",
    "Other": "#888888",
}


def _fmt_hours(h: float) -> str:
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


def _badge(text, color):
    return (
        f'<span style="display:inline-block;background:#0d0d14;border:1px solid {color};'
        f'color:{color};border-radius:3px;padding:2px 8px;font-size:11px;">{text}</span>'
    )


# -----------------------------------------------------------------------
# Page layout
# -----------------------------------------------------------------------
st.title("Preview")
st.caption("Read-only view of your complete JSM configuration.")
st.markdown("---")

rt = st.session_state.request_types
sla = st.session_state.sla_tiers
rules = st.session_state.automation_rules
paths = st.session_state.escalation_paths

if not rt and not sla and not rules and not paths:
    st.info("Nothing configured yet. Load the Life360 example from the sidebar or use the pages to build your configuration.")
    st.stop()

# -----------------------------------------------------------------------
# Section 1: Request Types
# -----------------------------------------------------------------------
st.markdown("## Request Types")
if not rt:
    st.caption("No request types configured.")
else:
    cols = st.columns([2.5, 1.5, 1.5, 1, 2])
    cols[0].markdown("**Name**")
    cols[1].markdown("**Category**")
    cols[2].markdown("**Team**")
    cols[3].markdown("**Fields**")
    cols[4].markdown("**Visibility**")
    st.markdown("---")

    for item in rt:
        cat_color = CATEGORY_COLORS.get(item["category"], "#888")
        c = st.columns([2.5, 1.5, 1.5, 1, 2])
        c[0].markdown(item["name"])
        c[1].markdown(
            _badge(item["category"], cat_color),
            unsafe_allow_html=True,
        )
        c[2].markdown(item["assignee_team"])
        c[3].markdown(str(len(item["fields"])))
        c[4].markdown(item["visibility"])

        if item["fields"]:
            with st.expander(f"Fields for {item['name']}", expanded=False):
                for f in item["fields"]:
                    req = "required" if f["required"] else "optional"
                    st.markdown(f"- **{f['name']}** ({f['type']}, {req})")

st.markdown("---")

# -----------------------------------------------------------------------
# Section 2: SLA Tiers
# -----------------------------------------------------------------------
st.markdown("## SLA Tiers")
if not sla:
    st.caption("No SLA tiers configured.")
else:
    sorted_sla = sorted(
        sla,
        key=lambda t: PRIORITIES.index(t["priority"]) if t["priority"] in PRIORITIES else 99,
    )
    header = st.columns([1, 3, 1.5, 1.5, 1.5, 1.5])
    header[0].markdown("**Priority**")
    header[1].markdown("**Description**")
    header[2].markdown("**First Response**")
    header[3].markdown("**Resolution**")
    header[4].markdown("**Escalation**")
    header[5].markdown("**Coverage**")
    st.markdown("---")

    for tier in sorted_sla:
        color = PRIORITY_COLORS.get(tier["priority"], "#888")
        coverage = "Business hrs" if tier["business_hours_only"] else "24/7"
        c = st.columns([1, 3, 1.5, 1.5, 1.5, 1.5])
        c[0].markdown(
            _badge(tier["priority"], color),
            unsafe_allow_html=True,
        )
        c[1].markdown(tier["description"])
        c[2].markdown(_fmt_hours(tier["first_response_hours"]))
        c[3].markdown(_fmt_hours(tier["resolution_hours"]))
        c[4].markdown(_fmt_hours(tier["escalation_hours"]))
        c[5].markdown(coverage)

st.markdown("---")

# -----------------------------------------------------------------------
# Section 3: Automation Rules
# -----------------------------------------------------------------------
st.markdown("## Automation Rules")
if not rules:
    st.caption("No automation rules configured.")
else:
    for rule in rules:
        status_color = "#00ff88" if rule["active"] else "#444"
        status_label = "ACTIVE" if rule["active"] else "OFF"
        header_html = (
            f'<span style="color:{status_color};font-size:11px;font-weight:bold;'
            f'background:#0d0d14;border:1px solid {status_color};border-radius:3px;'
            f'padding:1px 6px;margin-right:8px;">{status_label}</span>'
            f'<span style="font-size:13px;color:#e0e0e0;">{rule["name"]}</span>'
            f'<span style="font-size:11px;color:#888;margin-left:12px;">{rule["trigger"]}</span>'
        )

        with st.expander(rule["name"], expanded=False):
            st.markdown(header_html, unsafe_allow_html=True)
            st.markdown("")

            if rule.get("description"):
                st.markdown(f"_{rule['description']}_")

            if rule.get("condition"):
                st.markdown(f"**Condition:** {rule['condition']}")
            if rule.get("condition_request_type"):
                st.markdown(f"**Request type filter:** `{rule['condition_request_type']}`")
            else:
                st.markdown("**Request type filter:** General")

            if rule.get("actions"):
                st.markdown("**Actions:**")
                for i, action in enumerate(rule["actions"], 1):
                    st.markdown(f"{i}. {action}")

st.markdown("---")

# -----------------------------------------------------------------------
# Section 4: Escalation Paths
# -----------------------------------------------------------------------
st.markdown("## Escalation Paths")
if not paths:
    st.caption("No escalation paths configured.")
else:
    sorted_paths = sorted(
        paths,
        key=lambda p: PRIORITIES.index(p["applies_to_priority"]) if p["applies_to_priority"] in PRIORITIES else 99,
    )
    for path in sorted_paths:
        color = PRIORITY_COLORS.get(path["applies_to_priority"], "#888")
        pri_badge = _badge(path["applies_to_priority"], color)

        st.markdown(
            f'{pri_badge} <span style="color:#e0e0e0;">{path["name"]}</span>',
            unsafe_allow_html=True,
        )

        steps = sorted(path.get("steps", []), key=lambda s: s["step"])
        if steps:
            c = st.columns([0.5, 2, 2.5, 2.5])
            c[0].markdown("**Step**")
            c[1].markdown("**Time after breach**")
            c[2].markdown("**Action**")
            c[3].markdown("**Target**")
            for step in steps:
                time_label = "On breach" if step["time_hours"] == 0 else f"+{_fmt_hours(step['time_hours'])}"
                sc = st.columns([0.5, 2, 2.5, 2.5])
                sc[0].markdown(str(step["step"]))
                sc[1].markdown(time_label)
                sc[2].markdown(step["action_type"])
                sc[3].markdown(step["target_role"])
        else:
            st.caption("No steps defined.")
        st.markdown("")

st.markdown("---")

# -----------------------------------------------------------------------
# Validation Panel
# -----------------------------------------------------------------------
st.markdown("## Validation")

findings = validate(rt, sla, rules, paths)
errors = [f for f in findings if f["severity"] == "Error"]
warnings = [f for f in findings if f["severity"] == "Warning"]

if not findings:
    st.success("No issues found. Configuration is complete and consistent.")
else:
    if errors:
        st.error(f"{len(errors)} error{'s' if len(errors) != 1 else ''} found")
        for f in errors:
            st.markdown(
                f'<div style="background:#1a0505;border:1px solid #ff4444;border-radius:4px;'
                f'padding:10px;margin-bottom:8px;">'
                f'<span style="color:#ff4444;font-weight:bold;">[{f["code"]}]</span> '
                f'{f["message"]}</div>',
                unsafe_allow_html=True,
            )

    if warnings:
        st.warning(f"{len(warnings)} warning{'s' if len(warnings) != 1 else ''} found")
        for f in warnings:
            st.markdown(
                f'<div style="background:#1a1400;border:1px solid #ffcc00;border-radius:4px;'
                f'padding:10px;margin-bottom:8px;">'
                f'<span style="color:#ffcc00;font-weight:bold;">[{f["code"]}]</span> '
                f'{f["message"]}</div>',
                unsafe_allow_html=True,
            )

    st.caption(
        "Error: configuration will not behave as expected. "
        "Warning: configuration is incomplete but will function."
    )
