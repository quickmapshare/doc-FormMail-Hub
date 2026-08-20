---
title: FormMail Hub - Complete User & Administration Guide
description: Comprehensive guide for Google Forms email automation, custom SMTP setup, team routing, QR attendance tracking, staff scanner management, campaign dispatches, and quota expansion with FormMail Hub.
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

## 2. Roles & Permissions Architecture

FormMail Hub maintains strict permission boundaries between administrators and team members:

- **Primary Connector / Admin Role:** Only the **first user among the form's editors who connects that form to FormMail Hub** is granted exclusive rights to configure settings, templates, rules, custom SMTP, and triggers for that form. Co-editors do not gain configuration access.
- **Team Member & Event Staff Scanner Scope:** Team members are added so the Admin can select who receives email notifications upon form submission and who is authorized to act as event staff scanners. Team members **DO NOT** have edit or configuration permissions.

---

## 3. Delivery Infrastructure & Custom SMTP Requirement

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

## 4. Auto-Responders, Conditional Rules & Dynamic Tags

Once custom SMTP settings are configured and tested by the Admin to unlock feature tabs:

### Dynamic Tag Personalization
Templates parse submission fields into dynamic tags supporting `{Tag}`, `{{Tag}}`, and `${Tag}` enclosure formats using single-pass scanning in `templateParser.js`.

#### Supported System & Field Tags
- **Valid Built-in System Tags:** Strictly `{Form title}`, `{All Fields}`, `{Linked Form}`, `{Unsubscribe Link}`, `{QR Code}`, `{Check-in Scanner}`, `{Check-out Scanner}`, and `{Full Scanner}`.
- **Dynamic Question Field Tags:** Any exact form question title (e.g., `{First Name}`, `{Email Address}`).
- **Security Isolation:** Scanner authorization tags (`{Check-in Scanner}`, `{Check-out Scanner}`, `{Full Scanner}`) are populated strictly in staff/team emails and automatically stripped from respondent emails.

### Multi-Condition Routing Logic
Rules support evaluating multiple form response fields simultaneously to trigger targeted custom templates and route emails to specific recipients or internal teams based on exact conditions.

---

## 5. Event Ticketing, Staff Scanning & Attendance Engine

FormMail Hub includes an integrated QR ticketing and attendance tracking system.

### Stateless QR Code Tickets
Admins can insert `{QR Code}` into auto-responders and campaign templates. The cloud platform engine generates a secure, stateless QR code ticket signed with HMAC-SHA256. Scanning the QR code directs to `/qr-verify` for real-time verification of ticket authenticity, submission timestamp, respondent details, and reference code without database overhead.

### Personalized Staff Scanner Links
When routing notifications to Team Members, the platform generates personalized, cryptographically signed Authorization Links (`{Check-in Scanner}`, `{Check-out Scanner}`, `{Full Scanner}`).
- **Zero-Login Token:** Link includes an HMAC-SHA256 signed payload encoding form ID, staff email identity, mode (`checkin`, `checkout`, `both`), and a 24-hour expiration token (`/qr-auth?t=...`).
- **Instant Authorization:** Clicking the link sets a secure cookie on the staff member's device for browser-based scanning without password logins.

### Atomic State Engine & Redis Locks
When authorized staff scan a QR code, `/api/qr/action` verifies permissions and executes atomic Check-in or Check-out against Redis key `checkin:{form_id}:{refCode}` (24-hour TTL).
- **Check-in:** Rejects duplicate scans with a `409 Conflict` status if already checked in.
- **Check-out:** Validates checked-in status before releasing attendance state.

### Automated Dual Real-Time Attendance Receipts
Upon every successful scan, two real-time email receipts are dispatched:
1. **Attendee Attendance Email:** Dispatched to ticket holder with updated status (Checked In / Checked Out), Event Name, Ref ID, and UTC timestamp.
2. **Staff Activity Log Email:** Dispatched directly to the scanning Staff member (and CC'd to Form Owner) recording an audit trail containing attendee identity, ticket reference code, staff email identity, and scan timestamp.

---

## 6. Broadcast Campaigns & Lead List Management

Proactive bulk email marketing to form respondents is powered exclusively by the **FormMail Hub Google Sheets add-on**.

### Campaign Availability
Bulk sending (Campaigns) is **ONLY** available when launched from the **FormMail Hub Google Sheets add-on**.

### Campaign Creation & Dispatch Workflow
To send a proactive campaign to form respondents, the Admin follows this exact workflow:

1. **Create Campaign Template:** The Admin creates a campaign template.
2. **Configure Filtering Rules:** The Admin configures filtering rules to target specific respondents in the responses Google Sheet™.
3. **Enable Active Campaign Rule:** The Admin enables the rule as an active campaign.
4. **Switch to Campaign View:** Within the FormMail Hub Google Sheets add-on interface on the responses sheet, the Admin switches to the **Campaign** view.
5. **Select Synchronized Campaign:** The Admin selects the synchronized campaign name.
6. **Initiate Dispatch:** The Admin clicks the **'Dispatch'** button to initiate the bulk email dispatch.

---

## 7. Official Resources, Compliance & Support

- **App Marketplace:** [Google Workspace Marketplace Listing](https://workspace.google.com/marketplace/app/formmail_hub/409227874327)
- **Live Demo:** Test workflows on the official [Live Demo Form](https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform)
- **Technical Support:** Submit inquiries via [Support & Contact](https://formmail.vietutd.com/contact)
- **Legal Agreements:** Review our [Privacy Policy](https://formmail.vietutd.com/privacy-policy) and [Terms of Service](https://formmail.vietutd.com/terms-of-service)

---

*Google Forms™, Google Sheets™, and Gmail™ are trademarks of Google LLC.*