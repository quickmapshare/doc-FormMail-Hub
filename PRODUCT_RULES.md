# PRODUCT RULES & ABSOLUTE TRUTHS (GROUND TRUTH)

## Role & Permissions
1. Team Member Logic: Team members are ONLY added so the Admin can select who receives email notifications. Team members DO NOT have edit or configuration permissions.
2. Primary Connector / Admin Role: Only the first user among the form's editors who connects that form to FormMail Hub is granted exclusive rights to configure settings, templates, and triggers for that form.

## Architecture & Features
1. Ecosystem: FormMail Hub connects from 3 Google Forms add-ons ("Form Confirmation Emails", "Form to Email", "Form Notifications SMTP").
2. Full-Featured Application: The Google Sheets add-on named "FormMail Hub" is the full-featured application of the ecosystem.
3. Campaign Availability: Bulk sending (Campaigns) is ONLY available when launched from the Google Sheets add-on.
4. Campaign Creation & Dispatch Workflow: To send a proactive campaign to form respondents, the Admin creates a campaign template, configures filtering rules to target specific respondents in the responses Google Sheet, and enables the rule as an active campaign. Then, within the FormMail Hub Google Sheets add-on interface on the responses sheet, the Admin switches to the Campaign view, selects the synchronized campaign name, and clicks the 'Dispatch' button to initiate the bulk email dispatch.
5. Custom SMTP Requirement: Admins MUST configure custom SMTP settings before creating email templates, rules, campaigns, or accessing analytics, as these features require sending emails under the Admin's own email identity.
6. Built-in System Notifications: System Notifications is an out-of-the-box feature powered by the system's internal SMTP. It sends default-templated submission alerts to the Form Admin and selected Team Members without requiring custom SMTP setup.
7. Form Quota Expansion via Google Sheets: Connecting a spreadsheet via the 'FormMail Hub' Google Sheets add-on enables scaling beyond the standard 20-form limit, because a single spreadsheet can contain multiple Form Responses tabs while using only one active connection.
