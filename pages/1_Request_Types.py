"""
Page 1: Request Types Designer

Define the ticket categories users can submit, including their fields,
routing, and visibility settings.
"""

import streamlit as st
import uuid

from data.request_type_schema import CATEGORIES, FIELD_TYPES, TEAMS, VISIBILITY_OPTIONS, empty_request_type, empty_field


# -----------------------------------------------------------------------
# Ensure session state keys exist (handles direct-page navigation)
# -----------------------------------------------------------------------
if "request_types" not in st.session_state:
    st.session_state.request_types = []
if "_rt_editing" not in st.session_state:
    st.session_state._rt_editing = None
if "_rt_adding" not in st.session_state:
    st.session_state._rt_adding = False


def _save_edit(rt_id, updated):
    """Replace the request type with the given id."""
    st.session_state.request_types = [
        updated if rt["id"] == rt_id else rt
        for rt in st.session_state.request_types
    ]
    st.session_state._rt_editing = None


def _delete(rt_id):
    st.session_state.request_types = [
        rt for rt in st.session_state.request_types if rt["id"] != rt_id
    ]
    if st.session_state._rt_editing == rt_id:
        st.session_state._rt_editing = None


def _render_field_editor(fields, prefix):
    """Render inline field editor. Returns updated fields list."""
    updated_fields = [f.copy() for f in fields]
    st.markdown("**Fields**")

    to_delete = []
    for i, field in enumerate(updated_fields):
        fc1, fc2, fc3, fc4 = st.columns([3, 2, 1, 0.5])
        updated_fields[i]["name"] = fc1.text_input(
            "Field name", value=field["name"], key=f"{prefix}_fname_{i}", label_visibility="collapsed"
        )
        updated_fields[i]["type"] = fc2.selectbox(
            "Type", FIELD_TYPES, index=FIELD_TYPES.index(field["type"]) if field["type"] in FIELD_TYPES else 0,
            key=f"{prefix}_ftype_{i}", label_visibility="collapsed"
        )
        updated_fields[i]["required"] = fc3.checkbox("Req", value=field["required"], key=f"{prefix}_freq_{i}")
        if fc4.button("X", key=f"{prefix}_fdel_{i}"):
            to_delete.append(i)

    for idx in reversed(to_delete):
        updated_fields.pop(idx)

    if st.button("+ Add field", key=f"{prefix}_addfield"):
        updated_fields.append(empty_field())

    return updated_fields


def _render_add_form():
    st.markdown("### Add Request Type")
    with st.form("add_rt_form", clear_on_submit=True):
        name = st.text_input("Name *")
        col1, col2, col3 = st.columns(3)
        category = col1.selectbox("Category", CATEGORIES)
        team = col2.selectbox("Assignee Team", TEAMS)
        visibility = col3.selectbox("Visibility", VISIBILITY_OPTIONS)
        st.caption("Fields can be added after saving.")
        submitted = st.form_submit_button("Add Request Type")
        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                new_rt = {
                    "id": str(uuid.uuid4()),
                    "name": name.strip(),
                    "category": category,
                    "fields": [],
                    "assignee_team": team,
                    "visibility": visibility,
                }
                st.session_state.request_types.append(new_rt)
                st.session_state._rt_adding = False
                st.rerun()


def _render_edit_form(rt):
    rt_id = rt["id"]
    st.markdown(f"### Editing: {rt['name']}")

    name = st.text_input("Name *", value=rt["name"], key=f"edit_name_{rt_id}")
    col1, col2, col3 = st.columns(3)
    cat_idx = CATEGORIES.index(rt["category"]) if rt["category"] in CATEGORIES else 0
    team_idx = TEAMS.index(rt["assignee_team"]) if rt["assignee_team"] in TEAMS else 0
    vis_idx = VISIBILITY_OPTIONS.index(rt["visibility"]) if rt["visibility"] in VISIBILITY_OPTIONS else 0
    category = col1.selectbox("Category", CATEGORIES, index=cat_idx, key=f"edit_cat_{rt_id}")
    team = col2.selectbox("Assignee Team", TEAMS, index=team_idx, key=f"edit_team_{rt_id}")
    visibility = col3.selectbox("Visibility", VISIBILITY_OPTIONS, index=vis_idx, key=f"edit_vis_{rt_id}")

    updated_fields = _render_field_editor(rt["fields"], prefix=f"edit_{rt_id}")

    bc1, bc2 = st.columns([1, 4])
    if bc1.button("Save", key=f"save_{rt_id}"):
        if not name.strip():
            st.error("Name is required.")
        else:
            updated = {
                "id": rt_id,
                "name": name.strip(),
                "category": category,
                "fields": updated_fields,
                "assignee_team": team,
                "visibility": visibility,
            }
            _save_edit(rt_id, updated)
            st.rerun()
    if bc2.button("Cancel", key=f"cancel_{rt_id}"):
        st.session_state._rt_editing = None
        st.rerun()


# -----------------------------------------------------------------------
# Category color map
# -----------------------------------------------------------------------
CATEGORY_COLORS = {
    "Access": "#00ff88",
    "Hardware": "#00aaff",
    "Software": "#aa88ff",
    "Onboarding": "#ffaa00",
    "Account": "#ff6688",
    "Other": "#888888",
}


def _category_badge(cat):
    color = CATEGORY_COLORS.get(cat, "#888888")
    return f'<span style="display:inline-block;background:#0d0d14;border:1px solid {color};color:{color};border-radius:3px;padding:2px 8px;font-size:11px;">{cat}</span>'


# -----------------------------------------------------------------------
# Page layout
# -----------------------------------------------------------------------
st.title("Request Types")
st.caption("Define the ticket categories users can submit, their fields, and routing.")
st.markdown("---")

request_types = st.session_state.request_types

if not request_types:
    st.info(
        "No request types configured. Click **Add Request Type** below or load the example config from the sidebar."
    )

# Edit form (shown at top if editing)
editing_id = st.session_state._rt_editing
if editing_id:
    rt_to_edit = next((rt for rt in request_types if rt["id"] == editing_id), None)
    if rt_to_edit:
        with st.container():
            _render_edit_form(rt_to_edit)
        st.markdown("---")

# Card grid - 3 columns
cols_per_row = 3
rows = [request_types[i : i + cols_per_row] for i in range(0, len(request_types), cols_per_row)]

for row in rows:
    cols = st.columns(cols_per_row)
    for col, rt in zip(cols, row):
        with col:
            cat_badge = _category_badge(rt["category"])
            st.markdown(
                f"""
                <div style="background:#0d0d14;border:1px solid #1a1a2e;border-radius:6px;padding:16px;margin-bottom:8px;">
                    <div style="font-size:14px;font-weight:600;color:#e0e0e0;margin-bottom:8px;">{rt['name']}</div>
                    <div style="margin-bottom:8px;">{cat_badge}</div>
                    <div style="font-size:12px;color:#888;margin-bottom:4px;">Team: <span style="color:#e0e0e0;">{rt['assignee_team']}</span></div>
                    <div style="font-size:12px;color:#888;margin-bottom:4px;">Visibility: <span style="color:#e0e0e0;">{rt['visibility']}</span></div>
                    <div style="font-size:12px;color:#888;">Fields: <span style="color:#e0e0e0;">{len(rt['fields'])}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if rt["fields"]:
                with st.expander(f"Fields ({len(rt['fields'])})", expanded=False):
                    for f in rt["fields"]:
                        req_label = "required" if f["required"] else "optional"
                        st.markdown(
                            f"- **{f['name']}** ({f['type']}, {req_label})"
                        )
            bcol1, bcol2 = st.columns(2)
            if bcol1.button("Edit", key=f"btn_edit_{rt['id']}", use_container_width=True):
                st.session_state._rt_editing = rt["id"]
                st.rerun()
            if bcol2.button("Remove", key=f"btn_del_{rt['id']}", use_container_width=True):
                _delete(rt["id"])
                st.rerun()

st.markdown("---")

# Add form
if st.session_state._rt_adding:
    _render_add_form()
else:
    if st.button("+ Add Request Type"):
        st.session_state._rt_adding = True
        st.rerun()
