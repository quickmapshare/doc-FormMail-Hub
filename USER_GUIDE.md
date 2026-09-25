# FormMail Hub User Guide

## What FormMail Hub does

FormMail Hub is an external cloud email-processing and QR attendance platform for Google Forms and Google Sheets. Google add-ons act as ingestion and management bridges; email automation, rule evaluation, campaign dispatch, analytics, and attendance state are handled by the cloud engine.

> This guide describes only the documented product behavior. It does not add webhook, API, CRM, payment, or other capabilities that are not stated in `PRODUCT_RULES.md`.

## Getting started

1. Install the FormMail Hub add-on from the [Google Workspace Marketplace](https://workspace.google.com/marketplace/app/formmail_hub/409227874327).
2. Connect a Google Form using a supported Forms entry add-on, or connect a Google Sheet using the FormMail Hub Sheets add-on.
3. Configure and test Custom SMTP in the FormMail Hub interface.
4. After Custom SMTP is active, configure templates, rules, campaigns, and analytics.
5. Enable System Notifications if the Form Admin needs submission alerts, daily reports, or SMTP error alerts.

## Important feature boundaries

- Campaigns are available only from the FormMail Hub Google Sheets add-on while the spreadsheet is open.
- Built-in System SMTP is reserved for system alerts and reports. Custom SMTP is required for custom templates, respondent auto-responders, conditional routing, and campaigns.
- The first form editor who connects the form becomes the primary connector and has exclusive configuration rights for that form.
- Team Members can receive internal management notifications and can be authorized as event staff scanners. They are not required for the self-attendance workflow described below.
- FormMail Hub is an email receiving, processing, dispatching, analytics, and QR attendance engine. It does not provide webhooks or undocumented integrations.

## Templates and dynamic tags

Create an email template after Custom SMTP has been tested. Tags support `{Tag}`, `{{Tag}}`, and `${Tag}` forms. Common tags include:

- `{Question Title}`: the answer to a form question.
- `{Form title}`: the connected form title.
- `{All fields}`: a formatted summary of submitted fields.
- `{Linked form}`: a link to the live form.
- `{Unsubscribe link}`: form-scoped unsubscribe control for respondent and campaign emails.
- `{QR Code}`: a visual QR ticket containing a verification link.
- `{Verify Link}`: a direct camera-free check-in/check-out link.
- `{Check-in Scanner}` and `{Check-out Scanner}`: personalized seven-day scanner authorization links.
- `{Full Scanner}`: personalized dual-mode scanner authorization for check-in and check-out.

Use exact supported tag names. Do not invent tags or expect a tag to work outside its documented audience scope.

## Auto-responders and routing rules

Create a rule triggered by a form submission, choose the template, and configure the recipient or conditional routing. Multiple response fields can be evaluated together. Rules can send immediately, after a relative delay in seconds, minutes, hours, or days, or at a timezone-aware scheduled time.

Conditional routing uses Custom SMTP and remains unavailable until Custom SMTP is configured and tested.

## Campaigns

Campaigns are proactive bulk emails. Open the connected Google Sheet in the FormMail Hub add-on, create a campaign template, configure filters for the response rows, review the audience, and dispatch the campaign. Campaigns are not launched from the standalone Forms entry add-ons.

## QR attendance

A ticket email can include `{QR Code}` or `{Verify Link}`. Staff permissions are granted through personalized scanner links. The attendance engine prevents duplicate check-ins, requires an `IN` state before check-out, and keeps the attendance key with a rolling 30-day TTL. Successful check-in and check-out actions send an attendee receipt and a staff/admin audit email.

## Office PC self-attendance

1. Create an employee registration or attendance form and enable **Limit to 1 response**.
2. Connect the form to FormMail Hub.
3. Configure and test Custom SMTP.
4. Create a template containing `{Full Scanner}` followed by `{Verify Link}` and instructions for first-time authorization and daily use.
5. Create an auto-responder rule that sends this template to the submitter's `{Email}`.
6. The employee opens the email on the office PC and clicks `{Full Scanner}` once. The browser receives a seven-day rolling `scan_perms` authorization.
7. The employee uses `{Verify Link}` to check in on arrival and check out before leaving.

## Analytics, reports, and unsubscribe controls

Analytics track sent, failed, and opened email metrics in three modes: `system`, `automation`, and `campaign`. Daily summary reports are generated at 00:00 in each form's configured timezone. Respondent unsubscribe is form-specific; daily report unsubscribe is form-specific; SMTP error alert unsubscribe is user-level.

## Troubleshooting checklist

- **Templates, Rules, Campaigns, or Analytics are locked:** configure and test Custom SMTP first.
- **A campaign option is missing:** open the Google Sheet and use the FormMail Hub Sheets add-on.
- **A scanner link does not work:** use the personalized link in the email and verify that the browser authorization is still valid.
- **Check-out is rejected:** the ticket must currently be checked in (`IN`) before it can be checked out.
- **A tag is not replaced:** verify the exact supported tag spelling and enclosure format.

For support, visit https://formmail.vietutd.com/contact.
