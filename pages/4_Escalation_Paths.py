"""
Page 4: Escalation Paths

Define who gets notified and when after an SLA is breached.
Steps are visualized as a Plotly flow diagram with time-labeled nodes.
"""

import streamlit as st
import uuid
import plotly.graph_objects as go

from data.escalation_schema import ACTION_TYPES, ROLE_OPTIONS, empty_escalation_path, empty_step
from data.sla_schema import PRIORITIES


if "escalation_paths" not in st.session_state:
    st.session_state.escalation_paths = []
if "_esc_editing" not in st.session_state:
    st.session_state._esc_editing = None
if "_esc_adding" not in st.session_state:
    st.session_state._esc_adding = False


PRIORITY_COLORS = {
    "P1": "#ff4444",
    "P2": "#ffaa00",
    "P3": "#00aaff",
    "P4": "#00ff88",
}


def _fmt_hours(h: float) -> str:
    if h == 0:
        return "On breach"
    total_minutes = int(h * 60)
    if total_minutes < 60:
        return f"+{total_minutes} min"
    hours = total_minutes // 60
    minutes = total_minutes % 60
    if minutes == 0:
        return f"+{hours} hr" if hours == 1 else f"+{hours} hrs"
    return f"+{hours} hr {minutes} min"


def _escalation_flow_chart(path):
    """Build a Plotly horizontal flow chart for a single escalation path."""
    steps = sorted(path.get("steps", []), key=lambda s: s["step"])
    if not steps:
        return None

    color = PRIORITY_COLORS.get(path["applies_to_priority"], "#888")
    n = len(steps)

    # Node x positions: evenly spaced
    x_positions = [i / max(n - 1, 1) for i in range(n)]
    y_position = 0.5

    node_x = x_positions
    node_y = [y_position] * n

    # Build hover text and labels
    node_text = []
    node_hover = []
    for step in steps:
        time_label = _fmt_hours(step["time_hours"])
        node_text.append(f"{time_label}<br>{step['target_role']}")
        node_hover.append(
            f"Step {step['step']}<br>"
            f"Time: {time_label}<br>"
            f"Action: {step['action_type']}<br>"
            f"Target: {step['target_role']}"
        )

    fig = go.Figure()

    # Arrow lines between nodes
    for i in range(n - 1):
        fig.add_annotation(
            x=x_positions[i + 1],
            y=y_position,
            ax=x_positions[i],
            ay=y_position,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=2,
            arrowcolor=color,
        )

    # Nodes
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(
            size=60,
            color="#0d0d14",
            line=dict(color=color, width=2),
            symbol="square",
        ),
        text=node_text,
        textposition="middle center",
        textfont=dict(family="IBM Plex Mono, monospace", size=10, color="#e0e0e0"),
        hovertext=node_hover,
        hoverinfo="text",
    ))

    # Action type labels below nodes
    for i, step in enumerate(steps):
        fig.add_annotation(
            x=x_positions[i],
            y=y_position - 0.28,
            text=step["action_type"],
            showarrow=False,
            font=dict(size=9, color="#888", family="IBM Plex Mono, monospace"),
            xref="x",
            yref="y",
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#050508",
        plot_bgcolor="#0d0d14",
        font=dict(family="IBM Plex Mono, monospace", color="#e0e0e0"),
        xaxis=dict(visible=False, range=[-0.15, 1.15]),
        yaxis=dict(visible=False, range=[0.0, 1.0]),
        margin=dict(l=10, r=10, t=10, b=10),
        height=180,
        showlegend=False,
    )

    return fig


def _render_steps_editor(steps, prefix):
    """Render editable step list. Returns updated list."""
    updated = [s.copy() for s in steps]
    to_delete = []

    if updated:
        sc0, sc1, sc2, sc3, sc4 = st.columns([0.5, 1.5, 2.5, 2.5, 0.5])
        sc0.markdown("**Step**")
        sc1.markdown("**Time (hrs after breach)**")
        sc2.markdown("**Action**")
        sc3.markdown("**Target Role**")

        for i, step in enumerate(updated):
            c0, c1, c2, c3, c4 = st.columns([0.5, 1.5, 2.5, 2.5, 0.5])
            c0.markdown(f"**{step['step']}**")
            updated[i]["time_hours"] = c1.number_input(
                "hrs", value=float(step["time_hours"]),
                min_value=0.0, step=0.5,
                key=f"{prefix}_time_{i}", label_visibility="collapsed"
            )
            act_idx = ACTION_TYPES.index(step["action_type"]) if step["action_type"] in ACTION_TYPES else 0
            updated[i]["action_type"] = c2.selectbox(
                "action", ACTION_TYPES, index=act_idx,
                key=f"{prefix}_act_{i}", label_visibility="collapsed"
            )
            role_idx = ROLE_OPTIONS.index(step["target_role"]) if step["target_role"] in ROLE_OPTIONS else 0
            updated[i]["target_role"] = c3.selectbox(
                "role", ROLE_OPTIONS, index=role_idx,
                key=f"{prefix}_role_{i}", label_visibility="collapsed"
            )
            if c4.button("X", key=f"{prefix}_del_{i}"):
                to_delete.append(i)

    for idx in reversed(to_delete):
        updated.pop(idx)

    if st.button("+ Add step", key=f"{prefix}_addstep"):
        next_num = max((s["step"] for s in updated), default=0) + 1
        updated.append(empty_step(next_num))

    return updated


def _render_edit_form(path):
    path_id = path["id"]
    st.markdown(f"**Editing: {path['name']}**")

    col1, col2 = st.columns(2)
    name = col1.text_input("Path name *", value=path["name"], key=f"esc_name_{path_id}")
    pri_idx = PRIORITIES.index(path["applies_to_priority"]) if path["applies_to_priority"] in PRIORITIES else 0
    priority = col2.selectbox("Applies to priority", PRIORITIES, index=pri_idx, key=f"esc_pri_{path_id}")

    updated_steps = _render_steps_editor(path["steps"], prefix=f"esc_{path_id}")

    bc1, bc2 = st.columns([1, 4])
    if bc1.button("Save", key=f"esc_save_{path_id}"):
        if not name.strip():
            st.error("Name is required.")
        else:
            updated = {
                "id": path_id,
                "name": name.strip(),
                "applies_to_priority": priority,
                "steps": updated_steps,
            }
            st.session_state.escalation_paths = [
                updated if p["id"] == path_id else p
                for p in st.session_state.escalation_paths
            ]
            st.session_state._esc_editing = None
            st.rerun()
    if bc2.button("Cancel", key=f"esc_cancel_{path_id}"):
        st.session_state._esc_editing = None
        st.rerun()


def _render_add_form():
    st.markdown("### Add Escalation Path")
    with st.form("add_esc_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Path name *")
        priority = col2.selectbox("Applies to priority", PRIORITIES)
        st.caption("Steps can be added after saving.")
        submitted = st.form_submit_button("Add Escalation Path")
        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                new_path = {
                    "id": str(uuid.uuid4()),
                    "name": name.strip(),
                    "applies_to_priority": priority,
                    "steps": [],
                }
                st.session_state.escalation_paths.append(new_path)
                st.session_state._esc_adding = False
                st.rerun()


# -----------------------------------------------------------------------
# Page layout
# -----------------------------------------------------------------------
st.title("Escalation Paths")
st.caption("Define who gets notified and when after an SLA is breached.")
st.markdown("---")

paths = st.session_state.escalation_paths

if not paths:
    st.info(
        "No escalation paths configured. Add paths below or load the example config from the sidebar."
    )

# Edit form
editing_id = st.session_state._esc_editing
if editing_id:
    path_to_edit = next((p for p in paths if p["id"] == editing_id), None)
    if path_to_edit:
        with st.container():
            _render_edit_form(path_to_edit)
        st.markdown("---")

# Sorted by priority
sorted_paths = sorted(
    paths,
    key=lambda p: PRIORITIES.index(p["applies_to_priority"]) if p["applies_to_priority"] in PRIORITIES else 99,
)

for path in sorted_paths:
    color = PRIORITY_COLORS.get(path["applies_to_priority"], "#888")
    priority_badge = (
        f'<span style="color:{color};font-weight:bold;background:#0d0d14;'
        f'border:1px solid {color};border-radius:3px;padding:1px 8px;margin-right:8px;">'
        f'{path["applies_to_priority"]}</span>'
    )

    st.markdown(
        f'{priority_badge}<span style="font-size:14px;color:#e0e0e0;">{path["name"]}</span>',
        unsafe_allow_html=True,
    )

    steps = sorted(path.get("steps", []), key=lambda s: s["step"])
    if steps:
        # Flow diagram
        fig = _escalation_flow_chart(path)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # Steps table (compact)
        cols = st.columns([0.5, 2, 2.5, 2.5])
        cols[0].markdown("**Step**")
        cols[1].markdown("**Time**")
        cols[2].markdown("**Action**")
        cols[3].markdown("**Target**")
        for step in steps:
            c = st.columns([0.5, 2, 2.5, 2.5])
            c[0].markdown(str(step["step"]))
            c[1].markdown(_fmt_hours(step["time_hours"]))
            c[2].markdown(step["action_type"])
            c[3].markdown(step["target_role"])
    else:
        st.caption("No steps defined for this path.")

    act1, act2 = st.columns([1, 6])
    if act1.button("Edit", key=f"esc_btn_edit_{path['id']}"):
        st.session_state._esc_editing = path["id"]
        st.rerun()
    if act2.button("Remove", key=f"esc_btn_del_{path['id']}"):
        st.session_state.escalation_paths = [
            p for p in st.session_state.escalation_paths if p["id"] != path["id"]
        ]
        st.rerun()

    st.markdown("---")

if st.session_state._esc_adding:
    _render_add_form()
else:
    if st.button("+ Add Escalation Path"):
        st.session_state._esc_adding = True
        st.rerun()
