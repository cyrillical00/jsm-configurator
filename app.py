"""
JSM Configurator - Main entry point.

Design your Jira Service Management configuration before you build it.
"""

import streamlit as st
import uuid

# -- page config must be first Streamlit call --
st.set_page_config(
    page_title="JSM Configurator",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

from data.defaults import load_sample_example


# -----------------------------------------------------------------------
# Custom CSS: dark theme, IBM Plex Mono, green accents
# -----------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Mono', monospace !important;
        background-color: #050508;
        color: #e0e0e0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0d0d14;
        border-right: 1px solid #1a1a2e;
    }

    /* Primary buttons */
    div.stButton > button[kind="primary"],
    div.stButton > button:first-child {
        background-color: #050508;
        color: #00ff88;
        border: 1px solid #00ff88;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
    }
    div.stButton > button:hover {
        background-color: #00ff8815;
        border-color: #00ff88;
    }

    /* Cards */
    div[data-testid="stVerticalBlock"] > div.element-container {
        border-radius: 4px;
    }

    /* Metric labels */
    div[data-testid="metric-container"] label {
        color: #00ff88 !important;
        font-size: 11px !important;
    }

    /* Headers */
    h1, h2, h3 {
        font-family: 'IBM Plex Mono', monospace !important;
        color: #00ff88;
    }

    /* Table header */
    thead tr th {
        background-color: #0d0d14 !important;
        color: #00ff88 !important;
    }

    /* Expander */
    div[data-testid="stExpander"] {
        border: 1px solid #1a1a2e;
        border-radius: 4px;
    }

    /* Form border */
    div[data-testid="stForm"] {
        border: 1px solid #1a1a2e;
        border-radius: 4px;
        padding: 12px;
    }

    /* Selectbox, text input */
    div[data-baseweb="select"] > div,
    input[type="text"] {
        background-color: #0d0d14 !important;
        color: #e0e0e0 !important;
        border-color: #1a1a2e !important;
    }

    /* Tag / badge-like labels */
    .tag {
        display: inline-block;
        background: #0d0d14;
        border: 1px solid #00ff88;
        color: #00ff88;
        border-radius: 3px;
        padding: 2px 8px;
        font-size: 11px;
        margin: 2px;
        font-family: 'IBM Plex Mono', monospace;
    }
    .tag-gray {
        border-color: #444;
        color: #888;
    }
    .tag-red {
        border-color: #ff4444;
        color: #ff4444;
    }
    .tag-yellow {
        border-color: #ffcc00;
        color: #ffcc00;
    }

    /* Divider */
    hr {
        border-color: #1a1a2e;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------
# Session state initialization
# -----------------------------------------------------------------------
def _init_state():
    defaults = {
        "request_types": [],
        "sla_tiers": [],
        "automation_rules": [],
        "escalation_paths": [],
        "org_name": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()


# -----------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------
with st.sidebar:
    st.markdown("## JSM Configurator")
    st.markdown("---")

    st.markdown(
        "Design your Jira Service Management setup before you build it. "
        "Configure request types, SLA tiers, automation rules, and escalation paths."
    )

    st.markdown("---")

    st.markdown("**Organization**")
    st.session_state.org_name = st.text_input(
        "Org name (for export header)",
        value=st.session_state.get("org_name", ""),
        label_visibility="collapsed",
        placeholder="e.g. Apex Labs",
        key="org_name_input",
    )

    st.markdown("---")

    st.markdown("**Demo**")
    if st.button("Load Example Config", use_container_width=True):
        example = load_sample_example()
        st.session_state.request_types = example["request_types"]
        st.session_state.sla_tiers = example["sla_tiers"]
        st.session_state.automation_rules = example["automation_rules"]
        st.session_state.escalation_paths = example["escalation_paths"]
        st.session_state.org_name = "Apex Labs"
        st.success("Example config loaded.")
        st.rerun()

    if st.button("Clear All", use_container_width=True):
        st.session_state.request_types = []
        st.session_state.sla_tiers = []
        st.session_state.automation_rules = []
        st.session_state.escalation_paths = []
        st.session_state.org_name = ""
        st.rerun()

    st.markdown("---")

    # Summary counters
    rt_count = len(st.session_state.request_types)
    sla_count = len(st.session_state.sla_tiers)
    rule_count = len(st.session_state.automation_rules)
    esc_count = len(st.session_state.escalation_paths)

    col1, col2 = st.columns(2)
    col1.metric("Request Types", rt_count)
    col2.metric("SLA Tiers", sla_count)
    col3, col4 = st.columns(2)
    col3.metric("Rules", rule_count)
    col4.metric("Esc. Paths", esc_count)

    st.markdown("---")
    st.markdown(
        "<span style='color:#444; font-size:11px;'>Not connected to a live JSM instance.</span>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------
# Home / landing content
# -----------------------------------------------------------------------
st.title("JSM Configurator")
st.markdown(
    "Design your Jira Service Management configuration before you build it. "
    "Use the sidebar to load the example config or start from scratch. "
    "Navigate the pages in the left sidebar to configure each area."
)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**Page 1**")
    st.markdown("Request Types")
    st.markdown("Define the ticket categories users can submit, their fields, and routing.")
with col2:
    st.markdown("**Page 2**")
    st.markdown("SLA Tiers")
    st.markdown("Set response, resolution, and escalation targets for each priority level.")
with col3:
    st.markdown("**Page 3**")
    st.markdown("Automation Rules")
    st.markdown("Build trigger-condition-action chains for routing, alerting, and triage.")
with col4:
    st.markdown("**Page 4**")
    st.markdown("Escalation Paths")
    st.markdown("Define who gets notified and when after an SLA is breached.")

st.markdown("---")

col5, col6 = st.columns(2)
with col5:
    st.markdown("**Page 5**")
    st.markdown("Preview")
    st.markdown("Full read-only view of your configuration with validation results.")
with col6:
    st.markdown("**Page 6**")
    st.markdown("Export")
    st.markdown("Download a Confluence-paste-ready Markdown runbook or structured JSON config.")

st.markdown("---")

if rt_count == 0 and sla_count == 0:
    st.info(
        "No configuration loaded. Click **Load Example Config** in the sidebar "
        "to see a complete 900-person remote org setup, or use the pages above to build your own."
    )
