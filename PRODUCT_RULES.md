# PRODUCT RULES & ABSOLUTE TRUTHS (GROUND TRUTH)

## Role & Permissions
1. Team Member Logic: Team members are ONLY added so the Admin can select who receives email notifications. Team members DO NOT have edit or configuration permissions.
2. Primary Connector / Admin Role: Only the first user among the form's editors who connects that form to FormMail Hub is granted exclusive rights to configure settings, templates, and triggers for that form.

## Architecture & Ecosystem
3. Ecosystem: FormMail Hub connects from 3 Google Forms add-ons ("Form Confirmation Emails", "Form to Email", "Form Notifications SMTP").
4. Full-Featured Application: The Google Sheets add-on named "FormMail Hub" is the full-featured application of the ecosystem.
5. Form Quota Expansion via Google Sheets: Connecting a spreadsheet via the 'FormMail Hub' Google Sheets add-on enables scaling beyond the standard 20-form limit, because a single spreadsheet can contain multiple Form Responses tabs while using only one active connection.

## Campaign Engine
6. Campaign Availability: Bulk sending (Campaigns) is ONLY available when launched from the Google Sheets add-on.
7. Campaign Creation & Dispatch Workflow: To send a proactive campaign to form respondents, the Admin creates a campaign template, configures filtering rules to target specific respondents in the responses Google Sheet, and enables the rule as an active campaign. Then, within the FormMail Hub Google Sheets add-on interface on the responses sheet, the Admin switches to the Campaign view, selects the synchronized campaign name, and clicks the 'Dispatch' button to initiate the bulk email dispatch.

## SMTP & Email Sending Logic
8. Custom SMTP Requirement & UI Lock State: Admins MUST configure and successfully test custom SMTP settings before unlocking Templates, Rules, Campaigns, or Analytics. Until custom SMTP is active, these feature tabs strictly remain locked in the UI to prevent broken workflows.
9. Built-in System SMTP Scope: Built-in System SMTP is an out-of-the-box feature restricted STRICTLY to sending default-templated submission alerts to the Form Admin and selected Team Members (serving as a live demo and conserving Admin SMTP quota). System SMTP CANNOT be used for custom templates, rule-based notifications, or respondent auto-responders.

## Rule Engine & Dynamic Content
10. Multi-Condition Routing Logic: Rules support evaluating multiple form response fields simultaneously (multi-field matching) to trigger targeted custom templates and route emails to specific recipients or internal teams.
11. Dynamic Tags Strict Accuracy: Dynamic template tags are strictly handled by the codebase parser. Only dynamic question field tags (e.g., `{Question Title}`) and `{Form Title}` are valid default tags. Writers MUST NOT invent or assume unverified system tags (such as `{Form Summary}`, `{Response ID}`, `{Submission Date}`, `{Submitter Email}`, etc.).

## Feature Boundaries & Anti-Hallucination Rules
12. Email-Only Scope (NO WEBHOOKS): FormMail Hub operates strictly as an email receiving, processing, and dispatching engine based on admin-defined rules. It DOES NOT support webhooks, HTTP POST forwarding, external API calls, or third-party integrations (such as Slack, Microsoft Teams, Discord, Zapier, CRMs, or custom endpoints).
13. Strict Code-First Reality: Documentation must ONLY reflect existing, verified functionality present in the provided source code and PRODUCT_RULES.md. Writers MUST NOT invent, extrapolate, or draft guides for theoretical features, future roadmaps, or non-existent integrations.
