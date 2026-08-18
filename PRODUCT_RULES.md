# PRODUCT RULES & ABSOLUTE TRUTHS (GROUND TRUTH)

## Core Architecture & Platform Philosophy

1. **Independent Cloud Platform Engine:** FormMail Hub operates on a powerful, independent external cloud backend platform specifically built to overcome Google Workspace's native execution limits, quotas, and trigger constraints.
2. **Entry Points / Data Ingestion Bridges:** All Google add-ons—the 3 Google Forms entry add-ons ("Form Confirmation Emails", "Form to Email", "Form Notifications SMTP") and the 1 Google Sheets add-on ("FormMail Hub")—act strictly as data ingestion bridges/entry points that push submission events and configuration data to the FormMail Hub cloud platform.
3. **Full-Featured Google Sheets Management Client:** The "FormMail Hub" Google Sheets add-on acts as the primary full-featured management client for the ecosystem. Because a single Google Spreadsheet can host multiple Form Responses tabs, connecting via the Sheets add-on uses only 1 connection slot while scaling across multiple forms, and provides the interface to launch proactive bulk email Campaigns processed by our cloud platform engine.

## Role & Permissions

4. **Team Member Logic:** Team members are ONLY added so the Admin can select who receives email notifications. Team members DO NOT have edit or configuration permissions.
5. **Primary Connector / Admin Role:** Only the first user among the form's editors who connects that form to FormMail Hub is granted exclusive rights to configure settings, templates, and triggers for that form.

## Campaign Engine & Workflow

6. **Campaign Availability:** Bulk sending (Campaigns) is ONLY available when launched from the Google Sheets add-on.
7. **Campaign Creation & Dispatch Workflow:** To send a proactive campaign to form respondents, the Admin creates a campaign template, configures filtering rules to target specific respondents in the responses Google Sheet, and enables the rule as an active campaign. Then, within the FormMail Hub Google Sheets add-on interface on the responses sheet, the Admin switches to the Campaign view, selects the synchronized campaign name, and clicks the 'Dispatch' button to initiate the bulk email dispatch.

## SMTP & Transport Scope

8. **Custom SMTP Requirement & UI Lock State:** Admins MUST configure and test custom SMTP settings before unlocking Templates, Rules, Campaigns, or Analytics. Until custom SMTP is active, these feature tabs remain strictly locked in the UI.
9. **Built-in System SMTP Scope:** Built-in System SMTP is STRICTLY restricted to sending default-templated submission alerts to the Form Admin and selected Team Members (serving as a live demo and conserving Admin SMTP quota). System SMTP CANNOT be used for custom templates, rule-based notifications, or respondent auto-responders.

## Rule Engine & Dynamic Content

10. **Multi-Condition Routing Logic:** Rules support evaluating multiple form response fields simultaneously to trigger targeted custom templates and route emails to specific recipients or internal teams.
11. **Dynamic Tags Strict Accuracy:** Dynamic template tags are handled by `templateParser.js` using single-pass scanning. Supported enclosure formats are `{Tag}`, `{{Tag}}`, and `${Tag}`. The valid built-in system tags are strictly: `{Form Name}`, `{All Fields}`, `{Linked Form}`, and `{Unsubscribe Link}`, alongside any dynamic form question field title. Writers MUST NOT invent unverified system tags.

## Feature Boundaries & Anti-Hallucination Rules

12. **Email-Only Scope (NO WEBHOOKS):** FormMail Hub operates strictly as an email receiving, processing, and dispatching engine based on admin-defined rules. It DOES NOT support webhooks, HTTP POST forwarding, external API calls, or third-party integrations (such as Slack, Microsoft Teams, Discord, Zapier, CRMs, or custom endpoints).
13. **Strict Code-First Reality:** Documentation must ONLY reflect existing, verified functionality present in the provided source code and `PRODUCT_RULES.md`. Writers MUST NOT invent, extrapolate, or draft guides for theoretical features, future roadmaps, or non-existent integrations.

## Official Links & Resources

14. **Google Workspace Marketplace Listing:** [https://workspace.google.com/marketplace/app/formmail_hub/409227874327](https://workspace.google.com/marketplace/app/formmail_hub/409227874327)
15. **Privacy Policy:** [https://formmail.vietutd.com/privacy-policy](https://formmail.vietutd.com/privacy-policy)
16. **Terms of Service:** [https://formmail.vietutd.com/terms-of-service](https://formmail.vietutd.com/terms-of-service)
17. **Live Demo Form:** [https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform](https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform)
18. **Support & Contact:** [https://formmail.vietutd.com/contact](https://formmail.vietutd.com/contact)
