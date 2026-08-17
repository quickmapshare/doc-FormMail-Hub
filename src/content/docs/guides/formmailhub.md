---
title: FormMail Hub - Complete User & Administration Guide
description: Comprehensive guide for Google Forms email automation, custom SMTP setup, team routing, campaign dispatches, and quota expansion with FormMail Hub.
---

Welcome to the official **FormMail Hub** user and administration guide. FormMail Hub transforms standard Google Forms™ into an enterprise-grade customer communications, lead engagement, and email automation platform.

Access the central documentation portal anytime at [https://doc.formmailhub.com/](https://doc.formmailhub.com/).

---

## 1. Ecosystem & Application Architecture

FormMail Hub operates as an integrated multi-addon suite across Google Workspace, bringing powerful communication capabilities to Google Forms™ and Google Sheets™.

```
+-----------------------------------------------------------------------------------+
|                             GOOGLE FORMS ENTRY POINTS                             |
|  +---------------------------+  +-------------------+  +-----------------------+  |
|  | Form Confirmation Emails  |  |   Form to Email   |  | Form Notifications    |  |
|  |        (Add-on)           |  |     (Add-on)      |  |     SMTP (Add-on)     |  |
|  +---------------------------+  +-------------------+  +-----------------------+  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                             CORE APPLICATION HUB                                  |
|                     FormMail Hub for Google Sheets™ Add-on                        |
|                  (Full-Featured Application & Storage Layer)                      |
+-----------------------------------------------------------------------------------+
```

### Connected Add-ons
- **3 Google Forms Add-ons:** Connect directly into the platform to streamline setup:
  1. *Form Confirmation Emails*
  2. *Form to Email*
  3. *Form Notifications SMTP*
- **Full-Featured Core Application ("FormMail Hub" Google Sheets Add-on):** The central management application. Bulk broadcasting (Campaigns), full analytics, and list indexing are exclusively powered from the Google Sheets core add-on interface.

### Form Quota Expansion via Google Sheets
Standard configurations restrict form limits. Connecting a spreadsheet via the **'FormMail Hub' Google Sheets add-on** enables scaling beyond the standard 20-form limit. Because a single spreadsheet can contain multiple Form Responses tabs while using only one active connection, you can manage and scale notifications across numerous forms effortlessly.

---

## 2. Roles & Permissions Architecture

FormMail Hub maintains strict permission boundaries between administrators and team members:

- **Primary Connector / Admin Role:** Only the **first user among the form's editors who connects that form to FormMail Hub** is granted exclusive rights to configure settings, templates, rules, custom SMTP, and triggers for that form. Co-editors do not gain configuration access.
- **Team Member Role:** Team members are **ONLY** added so the Admin can select who receives email notifications upon form submission. Team members **DO NOT** have edit or configuration permissions.

---

## 3. Delivery Infrastructure & Custom SMTP Requirement

FormMail Hub provides a clear separation between out-of-the-box alerts and custom outreach:

```
+-----------------------------------------------------------------------------------+
|                        FORMMAIL HUB DELIVERY INFRASTRUCTURE                       |
+-----------------------------------------------------------------------------------+
                                  |                      |
          +-----------------------+                      +-----------------------+
          |                                                              |
          v                                                              v
+-----------------------------------+                          +-----------------------------------+
|    BUILT-IN SYSTEM NOTIFICATIONS  |                          | USER-CONFIGURED CUSTOM SMTP       |
+-----------------------------------+                          +-----------------------------------+
| - Out-of-the-box feature          |                          | - MANDATORY requirement before    |
| - Uses system internal SMTP       |                          |   creating templates, rules,      |
| - Sends default submission alerts |                          |   campaigns, or viewing analytics |
| - Targets Admin & Team Members    |                          | - Sends under Admin's identity    |
| - Consumes 0% personal SMTP quota |                          | - Scalable to 10,000+ msgs/day    |
+-----------------------------------+                          +-----------------------------------+
```

### Built-in System Notifications (Out-of-the-Box)
System Notifications work right out of the box powered by FormMail Hub's internal SMTP. It delivers default-templated submission alerts directly to the Form Admin and selected Team Members without requiring custom SMTP setup.

### Mandatory Custom SMTP Requirement
Admins **MUST** configure custom SMTP settings before creating email templates, rules, campaigns, or accessing analytics. These features send custom communications under the Admin's own email identity and require verified SMTP transport.

#### Supported Custom SMTP Providers
- **Free Gmail™ / Google Workspace:** Up to 500 emails/day using a 16-character Google App Password.
- **Amazon SES:** Scale to 10,000+ emails/day with enterprise deliverability.
- **SendGrid / Mailgun / Postmark:** API/SMTP relays with advanced tracking.
- **Custom Corporate Relays:** Connect directly to `smtp.yourdomain.com`.

---

## 4. Setting Up Auto-Responders & Conditional Rules

Once Custom SMTP is configured by the Admin, custom email automation and rules can be established:

### Dynamic Tag Personalization
Templates parse submission fields into dynamic tags wrapped in curly braces (`{Tag Name}`):
- `{Question Title}`: Inserts exact answers provided by respondents.
- `{Form Summary}`: Generates an inline HTML table of all submitted response fields.
- `{Submission Date}`: Localized timestamp of the response.
- `{Unsubscribe link}`: Generates a mandatory opt-out URL for campaign compliance.

### Smart Conditional Logic Routing
Route custom email templates based on specific submission field criteria (e.g., `If "Department" Equals "Sales"` -> Route to `sales@yourdomain.com` using Custom SMTP).

---

## 5. Broadcast Campaigns & Lead List Management

Proactive bulk email marketing to form respondents is powered by the **FormMail Hub Google Sheets add-on**.

### Campaign Availability & Requirement
Bulk sending (Campaigns) is **ONLY** available when launched from the **FormMail Hub Google Sheets add-on**. It is intentionally disabled within Google Forms entry add-ons.

### Campaign Creation & Dispatch Workflow
To send a proactive campaign to form respondents, follow this exact step-by-step workflow:

1. **Create Campaign Template:** The Admin creates a campaign template containing desired content and mandatory compliance tags (`{Unsubscribe link}`).
2. **Configure Filtering Rules:** The Admin configures filtering rules to target specific respondents in the responses Google Sheet™ (e.g., date ranges, response field choices).
3. **Enable Active Campaign Rule:** The Admin enables the rule as an active campaign.
4. **Open Google Sheets Core Add-on:** Within the backing responses Google Sheet™, the Admin launches the **FormMail Hub** add-on and switches to the **Campaign** view.
5. **Select Synchronized Campaign:** Select the synchronized campaign name from the list.
6. **Initiate Dispatch:** Click the **'Dispatch'** button to initiate the bulk email dispatch.

---

## 6. Audit Logging & Compliance

- **Suppression Management:** When a contact unsubscribes via `{Unsubscribe link}`, their record is flagged as `SUPPRESSED` and automatically excluded from future campaign dispatches.
- **Audit Diagnostics:** View delivery status (`DELIVERED`, `BOUNCED_HARD`, `FAILED_SMTP_AUTH`, `OPT_OUT_SKIPPED`) in real-time diagnostic logs.

---

*Google Forms™, Google Sheets™, and Gmail™ are trademarks of Google LLC.*