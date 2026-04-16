"""
Page 2: SLA Tiers

Configure response, resolution, and escalation time targets for each priority level.
Includes a Plotly Gantt-style visualization of all tiers on a shared time axis.
"""

import streamlit as st
import uuid
import plotly.graph_objects as go

from data.sla_schema import PRIORITIES, COVERAGE_OPTIONS, empty_sla_tier


if "sla_tiers" not in st.session_state:
    st.session_state.sla_tiers = []
if "_sla_editing" not in st.session_state:
    st.session_state._sla_editing = None
if "_sla_adding" not in st.session_state:
    st.session_state._sla_adding = False


PRIORITY_COLORS = {
    "P1": "#ff4444",
    "P2": "#ffaa00",
    "P3": "#00aaff",
    "P4": "#00ff88",
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


def _sla_gantt(tiers):
    """Render a horizontal bar chart showing all SLA time segments."""
    if not tiers:
        return None

    sorted_tiers = sorted(tiers, key=lambda t: PRIORITIES.index(t["priority"]) if t["priority"] in PRIORITIES else 99)

    fig = go.Figure()
    y_labels = []

    for tier in sorted_tiers:
        priority = tier["priority"]
        color = PRIORITY_COLORS.get(priority, "#888")
        y = priority
        y_labels.append(y)

        # First response bar (0 to first_response_hours)
        fig.add_trace(go.Bar(
            name="First Response",
            y=[y],
            x=[tier["first_response_hours"]],
            base=[0],
            orientation="h",
            marker_color=color,
            opacity=0.9,
            text=_fmt_hours(tier["first_response_hours"]),
            textposition="inside",
            showlegend=False,
            hovertemplate=(
                f"<b>{priority} First Response</b><br>"
                f"Target: {_fmt_hours(tier['first_response_hours'])}<extra></extra>"
            ),
        ))

        # Resolution bar (first_response_hours to resolution_hours)
        resolution_span = tier["resolution_hours"] - tier["first_response_hours"]
        if resolution_span > 0:
            fig.add_trace(go.Bar(
                name="Resolution",
                y=[y],
                x=[resolution_span],
                base=[tier["first_response_hours"]],
                orientation="h",
                marker_color=color,
                opacity=0.4,
                text=_fmt_hours(tier["resolution_hours"]),
                textposition="inside",
                showlegend=False,
                hovertemplate=(
                    f"<b>{priority} Resolution</b><br>"
                    f"Target: {_fmt_hours(tier['resolution_hours'])}<extra></extra>"
                ),
            ))

        # Escalation threshold marker
        if tier["escalation_hours"] > 0:
            fig.add_shape(
                type="line",
                x0=tier["escalation_hours"],
                x1=tier["escalation_hours"],
                y0=sorted_tiers.index(tier) - 0.4,
                y1=sorted_tiers.index(tier) + 0.4,
                line=dict(color="#ff4444", width=2, dash="dot"),
            )

    fig.update_layout(
        barmode="stack",
        template="plotly_dark",
        paper_bgcolor="#050508",
        plot_bgcolor="#0d0d14",
        font=dict(family="IBM Plex Mono, monospace", color="#e0e0e0", size=12),
        xaxis=dict(
            title="Hours",
            gridcolor="#1a1a2e",
            zerolinecolor="#1a1a2e",
        ),
        yaxis=dict(
            gridcolor="#1a1a2e",
            autorange="reversed",
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        height=260,
        title=dict(
            text="SLA Time Targets (hours)  |  dashed red line = escalation threshold",
            font=dict(size=12, color="#888"),
        ),
    )

    return fig


def _render_edit_row(tier):
    tier_id = tier["id"]
    st.markdown(f"**Editing: {tier['priority']}**")

    col1, col2 = st.columns([3, 1])
    description = col1.text_input("Description", value=tier["description"], key=f"sla_desc_{tier_id}")
    pri_idx = PRIORITIES.index(tier["priority"]) if tier["priority"] in PRIORITIES else 0
    priority = col2.selectbox("Priority", PRIORITIES, index=pri_idx, key=f"sla_pri_{tier_id}")

    col3, col4, col5 = st.columns(3)
    first_response = col3.number_input(
        "First Response (hrs)", value=float(tier["first_response_hours"]),
        min_value=0.0, step=0.25, key=f"sla_fr_{tier_id}"
    )
    resolution = col4.number_input(
        "Resolution (hrs)", value=float(tier["resolution_hours"]),
        min_value=0.0, step=1.0, key=f"sla_res_{tier_id}"
    )
    escalation = col5.number_input(
        "Escalation threshold (hrs)", value=float(tier["escalation_hours"]),
        min_value=0.0, step=1.0, key=f"sla_esc_{tier_id}"
    )

    col6, col7 = st.columns(2)
    biz_hours = col6.checkbox("Business hours only", value=tier["business_hours_only"], key=f"sla_biz_{tier_id}")
    notification = col7.text_input(
        "Notification target on breach", value=tier["notification_target"], key=f"sla_notif_{tier_id}"
    )

    bc1, bc2 = st.columns([1, 4])
    if bc1.button("Save", key=f"sla_save_{tier_id}"):
        updated = {
            "id": tier_id,
            "priority": priority,
            "description": description,
            "first_response_hours": first_response,
            "resolution_hours": resolution,
            "escalation_hours": escalation,
            "business_hours_only": biz_hours,
            "notification_target": notification,
        }
        st.session_state.sla_tiers = [
            updated if t["id"] == tier_id else t for t in st.session_state.sla_tiers
        ]
        st.session_state._sla_editing = None
        st.rerun()
    if bc2.button("Cancel", key=f"sla_cancel_{tier_id}"):
        st.session_state._sla_editing = None
        st.rerun()


def _render_add_form():
    st.markdown("### Add SLA Tier")
    with st.form("add_sla_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 3])
        priority = col1.selectbox("Priority", PRIORITIES)
        description = col2.text_input("Description *")

        col3, col4, col5 = st.columns(3)
        first_response = col3.number_input("First Response (hrs)", value=1.0, min_value=0.0, step=0.25)
        resolution = col4.number_input("Resolution (hrs)", value=8.0, min_value=0.0, step=1.0)
        escalation = col5.number_input("Escalation threshold (hrs)", value=4.0, min_value=0.0, step=1.0)

        col6, col7 = st.columns(2)
        biz_hours = col6.checkbox("Business hours only")
        notification = col7.text_input("Notification target on breach")

        submitted = st.form_submit_button("Add SLA Tier")
        if submitted:
            if not description.strip():
                st.error("Description is required.")
            else:
                new_tier = {
                    "id": str(uuid.uuid4()),
                    "priority": priority,
                    "description": description.strip(),
                    "first_response_hours": first_response,
                    "resolution_hours": resolution,
                    "escalation_hours": escalation,
                    "business_hours_only": biz_hours,
                    "notification_target": notification,
                }
                st.session_state.sla_tiers.append(new_tier)
                st.session_state._sla_adding = False
                st.rerun()


# -----------------------------------------------------------------------
# Page layout
# -----------------------------------------------------------------------
st.title("SLA Tiers")
st.caption("Set response, resolution, and escalation time targets for each priority level.")
st.markdown("---")

tiers = st.session_state.sla_tiers

if not tiers:
    st.info("No SLA tiers configured. Add tiers below or load the example config from the sidebar.")

# Edit form
editing_id = st.session_state._sla_editing
if editing_id:
    tier_to_edit = next((t for t in tiers if t["id"] == editing_id), None)
    if tier_to_edit:
        with st.container():
            _render_edit_row(tier_to_edit)
        st.markdown("---")

# Comparison table
if tiers:
    sorted_tiers = sorted(
        tiers,
        key=lambda t: PRIORITIES.index(t["priority"]) if t["priority"] in PRIORITIES else 99,
    )

    st.markdown("### Tier Comparison")

    header_cols = st.columns([1, 3, 1.5, 1.5, 1.5, 1.5, 1.5])
    header_cols[0].markdown("**Priority**")
    header_cols[1].markdown("**Description**")
    header_cols[2].markdown("**First Response**")
    header_cols[3].markdown("**Resolution**")
    header_cols[4].markdown("**Escalation**")
    header_cols[5].markdown("**Coverage**")
    header_cols[6].markdown("**Actions**")
    st.markdown("---")

    for tier in sorted_tiers:
        color = PRIORITY_COLORS.get(tier["priority"], "#888")
        coverage = "Business hrs" if tier["business_hours_only"] else "24/7"
        row_cols = st.columns([1, 3, 1.5, 1.5, 1.5, 1.5, 1.5])

        row_cols[0].markdown(
            f'<span style="color:{color};font-weight:bold;">{tier["priority"]}</span>',
            unsafe_allow_html=True,
        )
        row_cols[1].markdown(tier["description"])
        row_cols[2].markdown(_fmt_hours(tier["first_response_hours"]))
        row_cols[3].markdown(_fmt_hours(tier["resolution_hours"]))
        row_cols[4].markdown(_fmt_hours(tier["escalation_hours"]))
        row_cols[5].markdown(coverage)

        act1, act2 = row_cols[6].columns(2)
        if act1.button("Edit", key=f"sla_btn_edit_{tier['id']}"):
            st.session_state._sla_editing = tier["id"]
            st.rerun()
        if act2.button("Del", key=f"sla_btn_del_{tier['id']}"):
            st.session_state.sla_tiers = [t for t in tiers if t["id"] != tier["id"]]
            st.rerun()

    st.markdown("---")

    # Gantt chart
    st.markdown("### SLA Timeline Visualization")
    fig = _sla_gantt(tiers)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    st.caption("Solid bars: time to first response (dark) and time to resolution (light). Dashed red line: escalation threshold.")

st.markdown("---")

# Add form
if st.session_state._sla_adding:
    _render_add_form()
else:
    if st.button("+ Add SLA Tier"):
        st.session_state._sla_adding = True
        st.rerun()
