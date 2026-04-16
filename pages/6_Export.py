"""
Page 6: Export

Generate a Confluence-paste-ready Markdown runbook or a structured JSON config.

NOTE: JSON output is NOT a direct Jira API import format. It is a human-readable
design document in structured form. See the exporter module for details.
"""

import streamlit as st
from datetime import datetime

from engine.exporter import export_markdown, export_json
from engine.validator import validate


if "request_types" not in st.session_state:
    st.session_state.request_types = []
if "sla_tiers" not in st.session_state:
    st.session_state.sla_tiers = []
if "automation_rules" not in st.session_state:
    st.session_state.automation_rules = []
if "escalation_paths" not in st.session_state:
    st.session_state.escalation_paths = []


rt = st.session_state.request_types
sla = st.session_state.sla_tiers
rules = st.session_state.automation_rules
paths = st.session_state.escalation_paths
org_name = st.session_state.get("org_name", "")

# -----------------------------------------------------------------------
# Page layout
# -----------------------------------------------------------------------
st.title("Export")
st.caption("Download your configuration as a Confluence-paste-ready Markdown runbook or structured JSON.")
st.markdown("---")

if not rt and not sla and not rules and not paths:
    st.info("Nothing configured yet. Load the Life360 example from the sidebar or use the pages to build your configuration.")
    st.stop()

# Validation gate
findings = validate(rt, sla, rules, paths)
errors = [f for f in findings if f["severity"] == "Error"]
if errors:
    st.error(
        f"Your configuration has {len(errors)} error{'s' if len(errors) != 1 else ''}. "
        "Fix them on the Preview page before exporting."
    )
    for f in errors:
        st.markdown(f"- **[{f['code']}]** {f['message']}")
    st.markdown("---")

# Org name override
col1, _ = st.columns([2, 3])
org_input = col1.text_input(
    "Organization name for export header",
    value=org_name or "My Organization",
    key="export_org_name",
)

st.markdown("---")

# -----------------------------------------------------------------------
# Markdown export
# -----------------------------------------------------------------------
st.markdown("### Markdown Runbook")
st.markdown(
    "Standard Markdown formatted for Confluence. Paste using the Confluence editor's "
    "**Insert > Markdown** option (or the `/markdown` slash command). "
    "Tables, headers, and lists render correctly via that import path."
)

md_content = export_markdown(rt, sla, rules, paths, org_name=org_input)

st.text_area(
    "Markdown preview",
    value=md_content,
    height=320,
    label_visibility="collapsed",
)

date_str = datetime.now().strftime("%Y%m%d")
safe_org = org_input.strip().replace(" ", "_").lower() if org_input.strip() else "config"
md_filename = f"jsm_runbook_{safe_org}_{date_str}.md"

st.download_button(
    label="Download Markdown",
    data=md_content,
    file_name=md_filename,
    mime="text/markdown",
)

st.markdown("---")

# -----------------------------------------------------------------------
# JSON export
# -----------------------------------------------------------------------
st.markdown("### JSON Config")
st.markdown(
    "Structured JSON with all four configuration sections. "
    "**This is not a direct Jira API import format.** "
    "Use it as a reference document when manually configuring your JSM project, "
    "or pass it to an internal provisioning script."
)

json_content = export_json(rt, sla, rules, paths, org_name=org_input)

st.text_area(
    "JSON preview",
    value=json_content,
    height=320,
    label_visibility="collapsed",
)

json_filename = f"jsm_config_{safe_org}_{date_str}.json"

st.download_button(
    label="Download JSON",
    data=json_content,
    file_name=json_filename,
    mime="application/json",
)

st.markdown("---")
st.caption(
    "This tool is a configuration design aid. "
    "It does not connect to a live Jira instance."
)
