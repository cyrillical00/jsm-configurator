"""
Page 3: Automation Rules

Build trigger-condition-action chains that fire automatically in JSM.
Each rule has a trigger, an optional condition, one or more actions, and an active flag.
"""

import streamlit as st
import uuid

from data.automation_schema import TRIGGER_OPTIONS, empty_automation_rule


if "automation_rules" not in st.session_state:
    st.session_state.automation_rules = []
if "request_types" not in st.session_state:
    st.session_state.request_types = []
if "_rule_editing" not in st.session_state:
    st.session_state._rule_editing = None
if "_rule_adding" not in st.session_state:
    st.session_state._rule_adding = False


TRIGGER_ICONS = {
    "New issue created": "NEW",
    "Issue transitioned": "TXN",
    "SLA breached": "SLA",
    "Field changed": "FLD",
    "Scheduled": "SCH",
}


def _get_rt_names():
    return [""] + [rt["name"] for rt in st.session_state.request_types]


def _render_actions_editor(actions, prefix):
    """Render editable list of action strings. Returns updated list."""
    updated = list(actions)
    to_delete = []

    for i, action in enumerate(updated):
        ac1, ac2 = st.columns([9, 1])
        updated[i] = ac1.text_input(
            f"Action {i + 1}", value=action, key=f"{prefix}_action_{i}", label_visibility="collapsed"
        )
        if ac2.button("X", key=f"{prefix}_action_del_{i}"):
            to_delete.append(i)

    for idx in reversed(to_delete):
        updated.pop(idx)

    if st.button("+ Add action", key=f"{prefix}_add_action"):
        updated.append("")

    return updated


def _render_edit_form(rule):
    rule_id = rule["id"]
    st.markdown(f"**Editing: {rule['name']}**")

    col1, col2 = st.columns([3, 1])
    name = col1.text_input("Name *", value=rule["name"], key=f"rule_name_{rule_id}")
    active = col2.checkbox("Active", value=rule["active"], key=f"rule_active_{rule_id}")

    tri_idx = TRIGGER_OPTIONS.index(rule["trigger"]) if rule["trigger"] in TRIGGER_OPTIONS else 0
    trigger = st.selectbox("Trigger", TRIGGER_OPTIONS, index=tri_idx, key=f"rule_trigger_{rule_id}")

    col3, col4 = st.columns(2)
    condition = col3.text_input(
        "Condition (optional free-text description)",
        value=rule.get("condition", ""),
        key=f"rule_cond_{rule_id}",
    )
    rt_names = _get_rt_names()
    rt_val = rule.get("condition_request_type", "")
    rt_idx = rt_names.index(rt_val) if rt_val in rt_names else 0
    condition_rt = col4.selectbox(
        "Request type filter (leave blank for general rule)",
        rt_names,
        index=rt_idx,
        key=f"rule_crt_{rule_id}",
    )

    description = st.text_area(
        "Description", value=rule.get("description", ""), key=f"rule_desc_{rule_id}"
    )

    st.markdown("**Actions**")
    updated_actions = _render_actions_editor(rule["actions"], prefix=f"edit_{rule_id}")

    bc1, bc2 = st.columns([1, 4])
    if bc1.button("Save", key=f"rule_save_{rule_id}"):
        if not name.strip():
            st.error("Name is required.")
        else:
            updated = {
                "id": rule_id,
                "name": name.strip(),
                "trigger": trigger,
                "condition": condition,
                "condition_request_type": condition_rt,
                "actions": [a for a in updated_actions if a.strip()],
                "active": active,
                "description": description,
            }
            st.session_state.automation_rules = [
                updated if r["id"] == rule_id else r
                for r in st.session_state.automation_rules
            ]
            st.session_state._rule_editing = None
            st.rerun()
    if bc2.button("Cancel", key=f"rule_cancel_{rule_id}"):
        st.session_state._rule_editing = None
        st.rerun()


def _render_add_form():
    st.markdown("### Add Automation Rule")
    with st.form("add_rule_form"):
        col1, col2 = st.columns([3, 1])
        name = col1.text_input("Name *")
        active = col2.checkbox("Active", value=True)

        trigger = st.selectbox("Trigger", TRIGGER_OPTIONS)

        col3, col4 = st.columns(2)
        condition = col3.text_input("Condition (optional)")
        rt_names = _get_rt_names()
        condition_rt = col4.selectbox("Request type filter (blank = general)", rt_names)

        description = st.text_area("Description")
        actions_raw = st.text_area(
            "Actions (one per line)",
            placeholder="Assign to IT Ops\nPost to #it-alerts Slack",
        )

        submitted = st.form_submit_button("Add Rule")
        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                actions = [a.strip() for a in actions_raw.split("\n") if a.strip()]
                new_rule = {
                    "id": str(uuid.uuid4()),
                    "name": name.strip(),
                    "trigger": trigger,
                    "condition": condition,
                    "condition_request_type": condition_rt,
                    "actions": actions,
                    "active": active,
                    "description": description,
                }
                st.session_state.automation_rules.append(new_rule)
                st.session_state._rule_adding = False
                st.rerun()


# -----------------------------------------------------------------------
# Page layout
# -----------------------------------------------------------------------
st.title("Automation Rules")
st.caption("Build trigger-condition-action chains for routing, alerting, and triage.")
st.markdown("---")

rules = st.session_state.automation_rules

if not rules:
    st.info(
        "No automation rules configured. Add rules below or load the example config from the sidebar."
    )

# Edit form
editing_id = st.session_state._rule_editing
if editing_id:
    rule_to_edit = next((r for r in rules if r["id"] == editing_id), None)
    if rule_to_edit:
        with st.container():
            _render_edit_form(rule_to_edit)
        st.markdown("---")

# Rules table with expandable rows
if rules:
    for rule in rules:
        status_color = "#00ff88" if rule["active"] else "#444"
        trigger_tag = TRIGGER_ICONS.get(rule["trigger"], "---")
        status_label = "ACTIVE" if rule["active"] else "OFF"

        header = (
            f'<span style="color:{status_color};font-size:11px;font-weight:bold;'
            f'background:#0d0d14;border:1px solid {status_color};border-radius:3px;'
            f'padding:1px 6px;margin-right:8px;">{status_label}</span>'
            f'<span style="color:#888;font-size:11px;background:#0d0d14;border:1px solid #333;'
            f'border-radius:3px;padding:1px 6px;margin-right:8px;">{trigger_tag}</span>'
            f'<span style="font-size:13px;color:#e0e0e0;">{rule["name"]}</span>'
        )

        with st.expander(rule["name"], expanded=False):
            st.markdown(header, unsafe_allow_html=True)
            st.markdown("")

            if rule.get("description"):
                st.markdown(f"_{rule['description']}_")
                st.markdown("")

            col1, col2 = st.columns(2)
            col1.markdown(f"**Trigger:** {rule['trigger']}")
            if rule.get("condition"):
                col2.markdown(f"**Condition:** {rule['condition']}")
            if rule.get("condition_request_type"):
                st.markdown(
                    f"**Request type filter:** `{rule['condition_request_type']}`"
                )
            else:
                st.markdown("**Request type filter:** General (applies to all request types)")

            if rule.get("actions"):
                st.markdown("**Actions:**")
                for i, action in enumerate(rule["actions"], 1):
                    st.markdown(f"{i}. {action}")

            st.markdown("")
            act1, act2 = st.columns([1, 6])
            if act1.button("Edit", key=f"rule_btn_edit_{rule['id']}"):
                st.session_state._rule_editing = rule["id"]
                st.rerun()
            if act2.button("Remove", key=f"rule_btn_del_{rule['id']}"):
                st.session_state.automation_rules = [
                    r for r in st.session_state.automation_rules if r["id"] != rule["id"]
                ]
                st.rerun()

st.markdown("---")

if st.session_state._rule_adding:
    _render_add_form()
else:
    if st.button("+ Add Automation Rule"):
        st.session_state._rule_adding = True
        st.rerun()
