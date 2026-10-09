---
title: FormMail Hub - Complete User & Administration Guide
description: Comprehensive guide for Google Forms email automation, custom SMTP setup, team routing, delayed delivery, scheduled dispatch, QR attendance tracking, staff scanner management, campaign dispatches, and quota expansion with FormMail Hub.
---

Welcome to the official **FormMail Hub** user and administration guide. FormMail Hub transforms standard Google Forms™ into an enterprise-grade customer communications, lead engagement, event ticketing, and email automation platform.

To get started immediately, install the add-on from the [Google Workspace Marketplace Listing](https://workspace.google.com/marketplace/app/formmail_hub/409227874327) or test submission workflows on our [Live Demo Form](https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform).

---

## 1. Ecosystem & Application Architecture

FormMail Hub operates via an independent external cloud platform engine coupled with Google Workspace data ingestion bridges.

```
+-----------------------------------------------------------------------------------+
|                        DATA INGESTION BRIDGES (GOOGLE ADD-ONS)                     |
|  +---------------------------+  +-------------------+  +-----------------------+  |
|  | Form Confirmation Emails  |  |   Form to Email   |  | Form Notifications    |  |
|  |     (Forms Add-on)        |  |  (Forms Add-on)   |  |    SMTP (Forms)       |  |
|  +---------------------------+  +-------------------+  +-----------------------+  |
|  +-----------------------------------------------------------------------------+  |
|  |                 FormMail Hub for Google Sheets™ (Add-on)                    |  |
|  |                (Primary Management Client / Campaign Launchpad)            |  |
|  +-----------------------------------------------------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           | Pushes Submission Events & Config Data
                                           v
+-----------------------------------------------------------------------------------+
|                   INDEPENDENT CLOUD PLATFORM ENGINE (EXTERNAL)                    |
|       (High-Performance Event Processing, Rule Evaluation & SMTP Engine)          |
+-----------------------------------------------------------------------------------+
```

### Architecture Overview
- **Independent Cloud Platform Engine:** FormMail Hub operates on a powerful, independent external cloud backend platform specifically built to overcome Google Workspace's native execution limits, quotas, and trigger constraints.
- **Data Ingestion Bridges:** All 3 Google Forms entry add-ons (*Form Confirmation Emails*, *Form to Email*, *Form Notifications SMTP*) and the 1 Google Sheets add-on (*FormMail Hub*) act strictly as data ingestion bridges/entry points that push submission events and configuration data to the FormMail Hub cloud platform.
- **Full-Featured Google Sheets Management Client:** The **"FormMail Hub" Google Sheets add-on** acts as the primary full-featured management client. Because a single Google Spreadsheet can host multiple Form Responses tabs, connecting via the Sheets add-on uses only 1 connection slot while scaling across multiple forms, and provides the interface to launch proactive bulk email Campaigns processed by our cloud platform engine.

---

## 2. Quickstart: Verifying Your Form Connection & First Test Submission

When you connect a new form to FormMail Hub, you can instantly verify that submission event delivery is working before sharing your form publicly.

```
[ Form Connected via Add-on ]
             |
             v
[ Open Dashboard -> Notifications ]
             |
             v
[ Banner: "Waiting for your first submission" ]
             |
     +-------+-------+
     |               |
     v               v
[ Click 'Open form' ] [ Click 'Refresh' ]
     |
     v
[ Submit Sample Response ]
     |
     v
[ System SMTP Delivers Submission Alert to Admin Inbox ]
     |
     v
[ Banner Automatically Dismisses (~1 min) ]
```

### The "Waiting for your first submission" Prompt
When a connected form has not yet received any form submissions, FormMail Hub displays an onboarding notification banner in the administrative dashboard:

> **Waiting for your first submission**  
> *"Your form is connected. Submit one test response yourself to see notifications in action — it shows up here within about a minute."*

### Step-by-Step First Submission Test:
1. **Open FormMail Hub:** Launch the add-on sidebar in Google Forms™ or Google Sheets™ and click **"Go Beyond"** or **"Open Dashboard"**.
2. **Review Notifications View:** Navigate to **System Notifications**.
3. **Click 'Open form':** Click the **"Open form"** button located directly inside the notification banner to launch your live Google Form in a new browser tab.
4. **Submit a Test Response:** Complete the form fields with sample test data and click **Submit**.
5. **Verify Your Inbox:** Built-in System SMTP immediately delivers a submission notification email to the Form Admin inbox with the submitted responses.
6. **Automatic Confirmation:** Return to your FormMail Hub dashboard. Click **"Refresh"** (or wait approximately one minute); the prompt automatically disappears as soon as your first submission is detected, confirming your integration is live and operating smoothly.

---

## 3. Roles & Permissions Architecture

FormMail Hub maintains strict permission boundaries between administrators and team members:

- **Primary Connector / Admin Role:** Only the **first user among the form's editors who connects that form to FormMail Hub** is granted exclusive rights to configure settings, templates, rules, custom SMTP, and triggers for that form. Co-editors do not gain configuration access.
- **Team Member & Event Staff Scanner Scope:** Team members are added so the Admin can select who receives email notifications upon form submission and who is authorized to act as event staff scanners. Team members **DO NOT** have edit or configuration permissions.

---

## 4. Delivery Infrastructure & Custom SMTP Requirement

FormMail Hub separates internal administrative alerts from client-facing custom outreach:

```
+-----------------------------------------------------------------------------------+
|                        FORMMAIL HUB DELIVERY INFRASTRUCTURE                       |
+-----------------------------------------------------------------------------------+
                                  |                      |
          +-----------------------+                      +-----------------------+
          |                                                              |
          v                                                              v
+-----------------------------------+                          +-----------------------------------+
|    BUILT-IN SYSTEM SMTP RELAY     |                          | USER-CONFIGURED CUSTOM SMTP       |
+-----------------------------------+                          +-----------------------------------+
| - RESTRICTED strictly to system   |                          | - MANDATORY setup & test BEFORE   |
|   alerts (submission alerts,      |                          |   unlocking Templates, Rules,     |
|   daily reports, SMTP error alerts)|                          |   Campaigns, or Analytics         |
|   to Admin & Team Members         |                          | - Feature tabs strictly locked in |
| - Cannot send custom templates or |                          |   UI until Custom SMTP active     |
|   respondent auto-responders      |                          | - Custom templates & responders   |
+-----------------------------------+                          +-----------------------------------+
```

### Built-in System SMTP Scope
Built-in System SMTP is **STRICTLY** restricted to sending system alerts (submission notifications, daily activity reports, and SMTP connection error alerts) to the Form Admin and selected Team Members. System SMTP **CANNOT** be used for custom templates, rule-based notifications, or respondent auto-responders.

### Mandatory Custom SMTP Requirement & UI Lock State
Admins **MUST** configure and test custom SMTP settings before unlocking Templates, Rules, Campaigns, or Analytics. Until custom SMTP is active, these feature tabs remain strictly locked in the UI.

#### Supported Custom SMTP Providers
- **Free Gmail™ / Google Workspace:** Send using a 16-character Google App Password.
- **Amazon SES:** Scale to 10,000+ emails/day with enterprise deliverability.
- **SendGrid / Mailgun / Postmark:** Transactional email relays.
- **Custom Corporate Relays:** Connect directly to `smtp.yourdomain.com`.

---

## 5. Auto-Responders, Conditional Rules, Delayed Delivery & Dynamic Tags

Once custom SMTP settings are configured and tested by the Admin to unlock feature tabs:

### Dynamic Tag Personalization
Templates parse submission fields into dynamic tags supporting `{Tag}`, `{{Tag}}`, and `${Tag}` enclosure formats.

#### Supported System & Field Tags
- **Valid Built-in System Tags:** Strictly `{Form title}`, `{Linked form}`, `{All fields}`, `{Unsubscribe link}`, `{QR Code}`, `{Verify Link}`, `{Check-in Scanner}`, `{Check-out Scanner}`, and `{Full Scanner}`.
- **Dynamic Question Field Tags:** Any exact form question title (e.g., `{First Name}`, `{Email Address}`).
- **Security Isolation:** Scanner authorization tags (`{Check-in Scanner}`, `{Check-out Scanner}`, `{Full Scanner}`) are populated strictly in staff/team emails and automatically stripped from respondent emails.

### Multi-Condition Routing, Delayed Delivery & Scheduled Dispatch
- **Multi-Condition Logic:** Rules support evaluating multiple form response fields simultaneously to trigger targeted custom templates and route emails to specific recipients or internal teams.
- **Configurable Delivery Delay & Scheduled Dispatch:** Configure flexible timed delivery options. Admins can specify relative delay intervals in **Seconds**, **Minutes**, **Hours**, or **Days**, or set a fixed date and time (**Scheduled mode**). In scheduled mode, the cloud platform automatically converts local datetime using your Form's configured timezone into UTC for delayed execution, and safely skips execution if the scheduled timestamp has already passed at the time of submission.
- **Mandatory Recipient Selection:** To guarantee deliverability, rules require at least one designated recipient (either a selected team member or a mapped customer email field).

---

## 6. Event Ticketing, Staff Scanning & Attendance Engine

FormMail Hub includes an integrated QR ticketing and attendance tracking system.

### Digital QR Code Tickets & Camera-Free Verification
Admins can insert `{QR Code}` or `{Verify Link}` into auto-responders and campaign templates. The cloud platform engine generates a secure digital QR code ticket. Scanning the QR code or clicking the verification link opens the live verification screen for real-time verification of ticket authenticity, submission timestamp, respondent details, and reference code.

### Personalized Staff Scanner Links & Live Status Screen
When routing notifications to Team Members, the platform generates personalized, secure authorization links (`{Check-in Scanner}`, `{Check-out Scanner}`, `{Full Scanner}`).
- **Zero-Login Token:** Link provides browser authorization valid for **7 days** without requiring password logins.
- **Live Attendance Status Badge:** Upon scanning, staff see a dynamic status badge (`🟢 Status: Checked-In`, `🚪 Status: Checked-Out`, or `⚪ Status: Not Checked-In Yet`) with timestamps automatically converted to the device's local timezone. Clicking Check-In or Check-Out updates the status badge state immediately on screen.

> **Browser Session Isolation Note:** Because authorization relies on a secure browser session set during link activation, opening the link in one browser (e.g., in-app email viewer) will NOT authorize a different browser (e.g., default mobile browser or standalone camera scanner). Staff must copy and paste the authorization link directly into the exact browser application used for scanning QR codes.

### Real-Time Attendance State Engine & 30-Day Retention
When authorized staff scan a QR code or access the verification link, the platform verifies permissions and updates ticket status (`IN` or `OUT`). Every state change maintains the record with **30 days** of rolling data retention:
- **Check-in:** Prevents duplicate check-ins if the attendee is already marked as checked in (`IN`). Sets status to `IN`, logs operator email and timestamp, and refreshes the 30-day retention period.
- **Check-out:** Validates that the ticket is currently in `IN` status before updating status to `OUT`. Logs operator email and timestamp, and refreshes the 30-day retention period without deleting historical data.

### Automated Dual Real-Time Attendance Receipts
Upon every successful scan, two real-time email receipts are dispatched:
1. **Attendee Attendance Email:** Dispatched to ticket holder with updated status (Checked In / Checked Out), Event Name, Reference ID, and UTC timestamp.
2. **Staff Activity Log Email:** Dispatched directly to the scanning Staff member (and CC'd to Form Owner) recording an audit trail containing attendee identity, ticket reference code, staff email identity, and scan timestamp.

---

## 7. Broadcast Campaigns & Lead List Management

Proactive bulk email marketing to form respondents is powered exclusively by the **FormMail Hub Google Sheets add-on**.

### Campaign Availability
Bulk sending (Campaigns) is **ONLY** available when launched from the **FormMail Hub Google Sheets add-on**.

### Campaign Creation & Dispatch Workflow
To send a proactive campaign to form respondents, follow this exact workflow:

1. **Create Campaign Template:** Create a campaign template under Email Templates.
2. **Configure Filtering Rules:** Configure filtering rules to target specific respondents in the responses Google Sheet™.
3. **Enable Active Campaign Rule:** Enable the rule as an active campaign.
4. **Switch to Campaign View:** Within the FormMail Hub Google Sheets add-on interface on the responses sheet, switch to the **Campaign** view.
5. **Select Synchronized Campaign:** Select the synchronized campaign name from the list.
6. **Initiate Dispatch:** Click the **'Dispatch'** button to initiate the bulk email dispatch processed by the cloud engine.

---

## 8. Granular Subscription Management & Unsubscribe Scopes

FormMail Hub manages unsubscribes across 3 distinct scopes:
- **Form-Specific Respondent Unsubscribe:** Inserting `{Unsubscribe link}` in custom templates and campaigns unsubscribes respondents strictly from future emails related to that specific Form.
- **Form-Specific System Daily Report Unsubscribe:** Unsubscribe links in daily summary reports stop report emails strictly for that specific Form.
- **User-Level SMTP Error Alert Unsubscribe:** Unsubscribe links in SMTP failure alerts stop error notification emails across all forms managed by that user account.

---

## 9. Official Resources, Compliance & Support

- **App Marketplace:** [Google Workspace Marketplace Listing](https://workspace.google.com/marketplace/app/formmail_hub/409227874327)
- **Live Demo:** Test workflows on the official [Live Demo Form](https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform)
- **Technical Support:** Submit inquiries via [Support & Contact](https://formmail.vietutd.com/contact)
- **Legal Agreements:** Review our [Privacy Policy](https://formmail.vietutd.com/privacy-policy) and [Terms of Service](https://formmail.vietutd.com/terms-of-service)

---

*Google Forms™, Google Sheets™, and Gmail™ are trademarks of Google LLC.*