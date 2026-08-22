# PRODUCT RULES & ABSOLUTE TRUTHS (GROUND TRUTH)

## Core Architecture & Platform Philosophy
1. Independent Cloud Platform Engine: FormMail Hub operates on a powerful, independent external cloud backend platform specifically built to overcome Google Workspace's native execution limits, quotas, and trigger constraints.
2. Entry Points / Data Ingestion Bridges: All Google add-ons—the 3 Google Forms entry add-ons ("Form Confirmation Emails", "Form to Email", "Form Notifications SMTP") and the 1 Google Sheets add-on ("FormMail Hub")—act strictly as data ingestion bridges/entry points that push submission events and configuration data to the FormMail Hub cloud platform.
3. Full-Featured Google Sheets Management Client: The "FormMail Hub" Google Sheets add-on acts as the primary full-featured management client for the ecosystem. Because a single Google Spreadsheet can host multiple Form Responses tabs, connecting via the Sheets add-on uses only 1 connection slot while scaling across multiple forms, and provides the interface to launch proactive bulk email Campaigns processed by our cloud platform engine.

## Role & Permissions
4. Team Member & Staff Scanner Scope: Team members are added so the Admin can select who receives email notifications and who is authorized to act as event staff scanners. Team members DO NOT have edit or configuration permissions.
5. Primary Connector / Admin Role: Only the first user among the form's editors who connects that form to FormMail Hub is granted exclusive rights to configure settings, templates, and triggers for that form.

## Campaign Engine & Workflow
6. Campaign Availability: Bulk sending (Campaigns) is ONLY available when launched from the Google Sheets add-on.
7. Campaign Creation & Dispatch Workflow: To send a proactive campaign to form respondents, the Admin creates a campaign template, configures filtering rules to target specific respondents in the responses Google Sheet, and enables the rule as an active campaign. Then, within the FormMail Hub Google Sheets add-on interface on the responses sheet, the Admin switches to the Campaign view, selects the synchronized campaign name, and clicks the 'Dispatch' button to initiate the bulk email dispatch.

## SMTP & Transport Scope
8. Custom SMTP Requirement & UI Lock State: Admins MUST configure and test custom SMTP settings before unlocking Templates, Rules, Campaigns, or Analytics. Until custom SMTP is active, these feature tabs remain strictly locked in the UI.
9. Built-in System SMTP & System Notifications Scope: Built-in System SMTP is STRICTLY restricted to sending system alerts (submission notifications, daily activity reports, and SMTP connection error alerts) to the Form Admin and selected Team Members. System SMTP CANNOT be used for custom templates, rule-based notifications, or respondent auto-responders.

## Rule Engine, Dynamic Content, QR Code, Attendance & Unsubscribe Scope
10. Multi-Condition Routing Logic: Rules support evaluating multiple form response fields simultaneously to trigger targeted custom templates and route emails to specific recipients or internal teams.
11. Dynamic Tags Strict Accuracy & Isolation: Dynamic template tags are handled by templateParser.js using single-pass scanning. Supported enclosure formats are {Tag}, {{Tag}}, and ${Tag}. The valid built-in system tags are strictly: {Form title}, {All Fields}, {Linked Form}, {Unsubscribe Link}, {QR Code}, {Verify Link}, {Check-in Scanner}, {Check-out Scanner}, and {Full Scanner}, alongside any dynamic form question field title. Scanner links are populated strictly in staff/team emails and stripped from respondent emails to guarantee security isolation.
12. Stateless QR Code Ticket Mechanics & Camera-Free Staff Check-in: Admins can insert the {QR Code} dynamic tag (renders visual QR code with embedded link) or standalone {Verify Link} dynamic tag (renders a direct clickable verification URL /qr-verify?t=...) into custom email templates (usable in Auto-responders and Campaign emails). These blocks are populated in both Respondent tickets and Staff/Team Member notification emails. Authorized Staff members can perform attendee check-in either by scanning the QR code with their authorized device camera or by clicking the manual verification link ({Verify Link}) directly inside their notification email without requiring a camera scanner.
13. Personalized Staff Scanner Authentication & Zero-Login Links: When routing notifications to Team Members, the platform generates personalized, cryptographically signed Authorization Links ({Check-in Scanner}, {Check-out Scanner}, {Full Scanner}). Each link contains an HMAC-SHA256 signed payload encoding form ID, staff email identity, authorized action mode (checkin, checkout, or both), and a 7-day expiration token (/qr-auth?t=...). Clicking the link instantly authorizes the staff member's device (setting a secure cookie valid for 7 days) for seamless browser-based scanning or self-attendance without requiring password logins. **Browser Session Isolation Note**: Because authorization relies on a secure cookie set during link activation, opening the link in one browser (e.g., in-app email viewer) will NOT authorize a different browser (e.g., default desktop/mobile browser or standalone camera scanner). Staff must copy and paste the Auth link directly into the exact browser application used for scanning or verification.
14. Stateful Attendance Engine & 30-Day Rolling TTL: When an authorized staff member scans a respondent's QR code or accesses the verification link, /api/qr/action verifies device permissions and updates the ticket's explicit state (IN or OUT) under Redis key checkin:{form_id}:{refCode}. Single-ticket restrictions per respondent are enforced natively at the form entry point by enabling "Limit to 1 response" in Google Forms Settings, while the backend engine uses `checkin:{form_id}:{refCode}` as the canonical source of truth for each ticket. Every state change extends the record's TTL to 30 days (2,592,000 seconds) without deleting data. It enforces strict concurrency and status transitions:
    - Check-in: Rejects duplicate check-ins with a 409 Conflict status if the ticket status is already IN. Sets status to IN, logs check-in operator/timestamp, and refreshes key TTL to 30 days.
    - Check-out: Validates that the ticket is currently in IN state before updating status to OUT. Logs check-out operator/timestamp and refreshes key TTL to 30 days instead of deleting the Redis key.
15. Automated Dual Real-Time Attendance Receipts: Upon every successful Check-in or Check-out event, the engine dispatches two independent, real-time email notifications:
    - Attendee Attendance Email: Dispatched to the ticket holder confirming their updated status (Checked In / Checked Out), complete with Event Name, Reference ID, and UTC timestamp.
    - Staff Activity Log Email: Dispatched directly to the scanning Staff member (and CC'd to the Form Owner) recording an audit trail containing attendee identity, ticket reference code, staff email identity, and scan timestamp.
16. Internal Staff Self-Service Attendance Model: Organizations can implement internal employee attendance tracking by combining Team Member authorization with direct verification links: All employees are added as Team Members. When an employee submits the form, if their submitter email matches their registered Team Member email, the platform sends a single notification containing both their scanner auth link ({Full Scanner}) and direct ticket verification link ({Verify Link}). Upon arrival or departure, employees click their direct verification link directly on their authorized office PC browser. The platform processes the state change and executes Rule 15—sending an instant attendance receipt to the employee while dispatching an activity audit log email (CC'd to the Form Admin) for organizational management and coordination.
17. Unsubscribe Mechanics & Granular Scopes: The system handles unsubscribe requests via Cloud Backend tracking endpoints across 3 strict scopes:
    - Form-Specific Respondent Unsubscribe: Admins can insert {Unsubscribe Link} into custom email templates (Auto-responders and Campaign emails). Clicking this link unsubscribes the respondent's email address strictly from future emails related to that specific Form.
    - Form-Specific System Daily Report Unsubscribe: Daily summary report emails sent to Admins/Team Members include an unsubscribe link scoped strictly to that specific Form (stopping daily reports for that form only).
    - User-Level SMTP Error Alert Unsubscribe: SMTP error alert emails sent to the Admin include an unsubscribe link scoped to the User level (stopping all SMTP connection failure notifications across all forms managed by that user account).

## Step-by-Step Implementation: Office PC Kiosk & Automated Self-Attendance System
Organizations can set up direct self-service attendance for employees on their office computers using click-to-verify links without requiring physical QR codes or camera scanners.

### Step 1: Configure Google Form & Add Team Members
1. Open Google Forms and create the employee registration/attendance form.
2. In Settings, enable "Limit to 1 response" (ensures each employee holds a unique reference ticket code).
3. Connect the form to FormMail Hub via the Google Forms add-on or Google Sheets add-on.
4. In FormMail Hub UI, add all participating employees as Team Members.

### Step 2: Configure Custom SMTP
1. In FormMail Hub UI, configure and test Custom SMTP settings (unlocks Templates & Rules tabs).

### Step 3: Create Self-Attendance Template (Must Be Created First)
1. Go to Templates -> Create a new template (do NOT insert {QR Code}; insert ONLY {Verify Link} and {Full Scanner}).
2. Build the email body with the mandatory dynamic tags:
   - {Full Scanner}: Grants check-in/check-out permissions to the employee's office browser.
   - {Verify Link}: Direct link used by the employee to trigger Check-in and Check-out actions.

### Step 4: Configure Email Matching Rule
1. Go to Rules -> Create an Auto-responder Rule triggered on form submission.
2. Set condition: When a form submission occurs, IF submitter email matches Team Member email, route and send the template created in Step 3 to that Team Member.
   *(Note: There is no template for general submitters. Only matching Team Members receive the email containing both {Full Scanner} and {Verify Link}).*

### Step 5: Employee Office PC Authorization
1. Employee receives the notification email on their office computer.
2. Employee clicks the {Full Scanner} link directly inside the email on their main browser to authorize their device.
3. System sets an authorization cookie valid for 7 days for convenient, seamless daily attendance.

### Step 6: Daily Attendance Execution Workflow
1. On working days, employee opens their office PC browser.
2. Arrival: Employee clicks {Verify Link} in their email (or saved bookmark) to perform Check-in.
3. Departure: Employee clicks {Verify Link} prior to leaving to perform Check-out.
4. Backend updates ticket state (`checkin:{form_id}:{refCode}`) and refreshes Redis TTL to 30 days.

### Step 7: Automated Dual Audit Receipts
Upon every check-in/check-out click:
- Employee Receipt: Dispatched immediately confirming status change (IN/OUT) with timestamp.
- Admin Audit Trail: Dispatched immediately to the Team Member / employee and CC'd to Form Admin for compliance monitoring.

## Feature Boundaries & Anti-Hallucination Rules
18. Email & QR Attendance Scope (NO WEBHOOKS): FormMail Hub operates strictly as an email receiving, processing, dispatching, and QR attendance tracking engine based on admin-defined rules. It DOES NOT support webhooks, HTTP POST forwarding, external API calls, or third-party integrations (such as Slack, Microsoft Teams, Discord, Zapier, CRMs, or custom endpoints).
19. Strict Code-First Reality: Documentation must ONLY reflect existing, verified functionality present in the provided source code and PRODUCT_RULES.md. Writers MUST NOT invent, extrapolate, or draft guides for theoretical features, future roadmaps, or non-existent integrations.

## Official Links & Resources
20. Google Workspace Marketplace Listing: https://workspace.google.com/marketplace/app/formmail_hub/409227874327
21. Privacy Policy: https://formmail.vietutd.com/privacy-policy
22. Terms of Service: https://formmail.vietutd.com/terms-of-service
23. Live Demo Form: https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform
24. Support & Contact: https://formmail.vietutd.com/contact
