# JSM Configurator

Design your Jira Service Management configuration before you build it — request types, SLA tiers, automation rules, and escalation paths, with Confluence-ready export.

---

## What it does

| Page | Description |
|------|-------------|
| Request Types | Define every ticket category users can submit, its fields, routing team, and visibility. |
| SLA Tiers | Set first-response, resolution, and escalation-threshold targets for P1 through P4. |
| Automation Rules | Build trigger-condition-action chains for routing, priority assignment, Slack alerts, and sub-task creation. |
| Escalation Paths | Define who gets notified at each step after an SLA is breached, with time-based triggers. |
| Preview | Read-only view of the full configuration with an inline validation panel. |
| Export | Download a Confluence-paste-ready Markdown runbook or a structured JSON config file. |

---

## Load Life360 Example

The **Load Life360 Example** button pre-fills a complete JSM configuration based on the actual setup built at Life360 for a ~900-person remote org over 6 years of production use. It includes:

- 6 request types covering access, hardware, onboarding, account, and remote access workflows
- 4 SLA tiers (P1 through P4) with response and resolution targets for 24/7 and business-hours coverage
- 6 automation rules for P1 alerting, access request routing, SLA breach escalation, new hire triage, Okta lockout fast-track, and stale ticket reminders
- 4 escalation paths with time-triggered step sequences from IT on-call up to CTO for P1

The example passes the built-in validator with zero errors and zero warnings.

---

## Export formats

**Markdown:** Formatted for Confluence. Paste into the Confluence editor using Insert > Markdown or the `/markdown` slash command. Tables, headers, and lists render correctly via that import path.

**JSON:** Structured config object with all four sections as nested arrays. This is not a direct Jira API import format. Use it as a reference when manually configuring your JSM project or as input to an internal provisioning script.

---

## Scope

This is a configuration design tool, not a Jira API integration. It does not connect to a live Jira instance. No API keys are required.

---

## Stack

- Python 3.11+
- Streamlit
- Plotly (SLA timeline and escalation path diagrams)

---

Built by [Oleg Strutsovski](https://linkedin.com/in/olegst) — IT Operations Manager
