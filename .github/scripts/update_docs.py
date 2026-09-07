import os
import sys
import json
import glob
import re
from google import genai

print("========================================")
print("🚀 AI MULTI-PAGE DOCS BUILDER & EXPANDER v2.5 (USER-CENTRIC HELP CENTER ENGINE)")

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash") 
print(f"🤖 Gemini Model Engine: {MODEL_NAME}")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ LỖI: Chưa tìm thấy GEMINI_API_KEY trong Repo Secrets!")
    sys.exit(1)

client = genai.Client(api_key=api_key)
code_diff = os.environ.get("CODE_DIFF", "")
docs_dir = "src/content/docs"
rules_file = "PRODUCT_RULES.md"

product_rules = """# PRODUCT RULES & ABSOLUTE TRUTHS (GROUND TRUTH)

## Core Architecture & Platform Philosophy
1. Independent Cloud Platform Engine: FormMail Hub operates on a powerful, independent external cloud backend platform specifically built to overcome Google Workspace's native execution limits, quotas, and trigger constraints.
2. Entry Points / Data Ingestion Bridges: All Google add-ons—the 3 Google Forms entry add-ons ("Form Confirmation Emails", "Form to Email", "Form Notifications SMTP") and the 1 Google Sheets add-on ("FormMail Hub")—act strictly as data ingestion bridges/entry points that push submission events and configuration data to the FormMail Hub cloud platform.
3. Full-Featured Google Sheets Management Client: The "FormMail Hub" Google Sheets add-on acts as the primary full-featured management client for the ecosystem. Because a single Google Spreadsheet can host multiple Form Responses tabs, connecting via the Sheets add-on uses only 1 connection slot while scaling across multiple forms, and provides the interface to launch proactive bulk email Campaigns processed by our cloud platform engine.

## Role & Permissions
4. Team Member & Staff Scanner Scope: Team members are added so the Admin can select who receives internal management email notifications and who is authorized to act as event staff scanners. Team members DO NOT have edit or configuration permissions.
5. Primary Connector / Admin Role: Only the first user among the form's editors who connects that form to FormMail Hub is granted exclusive rights to configure settings, templates, and triggers for that form.

## Campaign Engine & Workflow
6. Campaign Availability: Bulk sending (Campaigns) is ONLY available when launched from the Google Sheets add-on.
7. Campaign Creation & Dispatch Workflow: To send a proactive campaign to form respondents, the Admin creates a campaign template, configures filtering rules to target specific respondents in the responses Google Sheet, and enables the rule as an active campaign. Then, within the FormMail Hub Google Sheets add-on interface on the responses sheet, the Admin switches to the Campaign view, selects the synchronized campaign name, and clicks the 'Dispatch' button to initiate the bulk email dispatch.

## SMTP & Transport Scope
8. Custom SMTP Requirement & UI Lock State: Admins MUST configure and test custom SMTP settings before unlocking Templates, Rules, Campaigns, or Analytics. Until custom SMTP is active, these feature tabs remain strictly locked in the UI.
9. Built-in System SMTP & System Notifications Scope: Built-in System SMTP is STRICTLY restricted to sending system alerts (submission notifications, daily activity reports, and SMTP connection error alerts) to the Form Admin and selected Team Members. System SMTP CANNOT be used for custom templates, rule-based notifications, or respondent auto-responders.

## Analytics, Daily Reporting & Multi-Mode Tracking Scope
10. Daily Multi-Mode Metric Tracking: All email transactions—including successfully sent emails (`emails_sent`), failed emails (`emails_failed`), and opened emails (`emails_opened`)—are tracked and logged per Form on a daily basis, strictly categorized across three distinct execution modes:
    - `system`: Automated operational alerts, daily reports, and system notifications.
    - `automation`: Submission-triggered auto-responders and rule-based emails.
    - `campaign`: Proactive bulk emails dispatched from the Google Sheets add-on.
11. Per-Form Daily Summary Reports & Unsubscribe Control: At the start of a new day (00:00 according to each form's configured timezone), the system automatically generates and dispatches a Daily Summary Report email via System SMTP to the Form Admin for each active Form, summarizing the previous day's email statistics. Admins can independently unsubscribe from daily reports for specific non-critical forms via the embedded unsubscribe link, stopping reports strictly for that form while keeping reports active for others.
12. Form Dashboard Analytics Interface: The dashboard corresponding to each active Form displays real-time and historical aggregated statistics showing total emails sent successfully, total email errors, and total email opens, fully segmented by execution mode (`system`, `automation`, and `campaign`).

## Rule Engine, Dynamic Content, QR Code, Attendance & Unsubscribe Scope
13. Multi-Condition Routing Logic: Rules support evaluating multiple form response fields simultaneously to trigger targeted custom templates and route emails to specific recipients or internal teams.
14. Configurable Delivery Delay: Rules support an optional delay parameter, enabling Admins to specify custom wait intervals in seconds, minutes, hours, or days when configuring submission-triggered or conditional rules. The cloud engine queues and dispatches the email automatically once the specified duration elapses.
15. Dynamic Tags Strict Accuracy & Isolation: Dynamic template tags are handled by templateParser.js using single-pass scanning. Supported enclosure formats are {Tag}, {{Tag}}, and ${Tag}. The valid built-in system tags are strictly: {Form title}, {Linked form}, {All fields}, {Unsubscribe link}, {QR Code}, {Verify Link}, {Check-in Scanner}, {Check-out Scanner}, and {Full Scanner}, alongside any dynamic form question field title.
16. Stateless QR Code Ticket Mechanics & Camera-Free Check-in: Admins can insert the {QR Code} dynamic tag (renders visual QR code with embedded link) or standalone {Verify Link} dynamic tag (renders a direct clickable verification URL /qr-verify?t=...) into custom email templates (usable in Auto-responders and Campaign emails). These blocks are populated in both Respondent tickets and Staff/Team notification emails. Authorized Users or Staff can perform check-in either by scanning the QR code with their camera or by clicking the direct verification link ({Verify Link}) inside their email without requiring a camera scanner.
17. Personalized Scanner & Device Authentication Links: When routing emails, the platform generates personalized, cryptographically signed Authorization Links ({Check-in Scanner}, {Check-out Scanner}, {Full Scanner}). Each link contains an HMAC-SHA256 signed payload encoding form ID, user identity, authorized action mode (checkin, checkout, or both), and a 7-day expiration token (/qr-auth?t=...). Clicking the link instantly authorizes the user's device browser (setting a secure cookie valid for 7 days) for seamless browser-based scanning or self-attendance without requiring password logins. **Browser Session Isolation Note**: Because authorization relies on a secure cookie set during link activation, opening the link in one browser (e.g., in-app email viewer) will NOT authorize a different browser (e.g., default desktop browser or standalone camera scanner). Users must copy and paste the Auth link directly into the exact browser application used for daily verification.
18. Stateful Attendance Engine & 30-Day Rolling TTL: When an authorized user or staff member accesses the verification link, /api/qr/action verifies device permissions (scan_perms or self_perms) and updates the ticket's explicit state (IN or OUT) under Redis key checkin:{form_id}:{refCode}. Single-ticket restrictions per respondent are enforced natively at the form entry point by enabling "Limit to 1 response" in Google Forms Settings, while the backend engine uses `checkin:{form_id}:{refCode}` as the canonical source of truth for each ticket. Every state change extends the record's TTL to 30 days (2,592,000 seconds) without deleting data. It enforces strict concurrency and status transitions:
    - Check-in: Rejects duplicate check-ins with a 409 Conflict status if the ticket status is already IN. Sets status to IN, logs operator/timestamp, and refreshes key TTL to 30 days.
    - Check-out: Validates that the ticket is currently in IN state before updating status to OUT. Logs operator/timestamp and refreshes key TTL to 30 days instead of deleting the Redis key.
19. Automated Dual Real-Time Attendance Receipts: Upon every successful Check-in or Check-out event, the engine dispatches two independent, real-time email notifications:
    - Attendee Attendance Email: Dispatched to the ticket holder confirming their updated status (Checked In / Checked Out), complete with Event Name, Reference ID, Location (if applicable), and UTC timestamp.
    - Staff/Admin Audit Log Email: Dispatched directly to the operator/user (and CC'd to the Form Owner) recording an audit trail containing attendee identity, ticket reference code, operator identity, and scan timestamp.
20. Internal Automated Self-Service Attendance Model: Organizations can implement internal employee attendance tracking without manually registering Team Members for every submitter. By placing {Full Scanner} followed by {Verify Link} in the auto-responder template sent directly to form submitters, any employee who completes the form receives both authorization and execution links. Employees authorize their office PC browser once via {Full Scanner} and subsequently perform daily Check-in/Check-out via {Verify Link} on that same browser.
21. Unsubscribe Mechanics & Granular Scopes: The system handles unsubscribe requests via Cloud Backend tracking endpoints across 3 strict scopes:
    - Form-Specific Respondent Unsubscribe: Admins can insert {Unsubscribe link} into custom email templates (Auto-responders and Campaign emails). Clicking this link unsubscribes the respondent's email address strictly from future emails related to that specific Form.
    - Form-Specific System Daily Report Unsubscribe: Daily summary report emails sent to Admins/Team Members include an unsubscribe link scoped strictly to that specific Form (stopping daily reports for that single form).
    - User-Level SMTP Error Alert Unsubscribe: SMTP error alert emails sent to the Admin include an unsubscribe link scoped to the User level (stopping all SMTP connection failure notifications across all forms managed by that user account).

## Step-by-Step Implementation: Office PC Kiosk & Automated Self-Attendance System
Organizations can set up direct self-service attendance for employees on their office computers using click-to-verify links without requiring manual team member pre-registration, physical QR codes, or camera scanners.

### Step 1: Configure Google Form
1. Open Google Forms and create the employee registration/attendance form.
2. In Settings, enable "Limit to 1 response" (ensures each employee holds a single unique reference ticket code).
3. Connect the form to FormMail Hub via the Google Forms add-on or Google Sheets add-on.

### Step 2: Configure Custom SMTP
1. In FormMail Hub UI, configure and test Custom SMTP settings (unlocks Templates & Rules tabs).

### Step 3: Create Self-Attendance Template (Must Be Created First)
1. Go to Templates -> Create a new template.
2. Build the email body with the mandatory dynamic tags in sequence:
   - {Full Scanner}: Grants check-in/check-out permissions to the employee's office PC browser on first click.
   - {Verify Link}: Direct link used by the employee to trigger daily Check-in and Check-out actions.
3. Add clear step-by-step instructions in the email body:
   - Step 1: Click the {Full Scanner} link once to authorize this browser device.
   - Step 2: Use the {Verify Link} (or bookmark it) daily to perform Check-in upon arrival and Check-out upon departure.

### Step 4: Configure Email Auto-responder Rule
1. Go to Rules -> Create an Auto-responder Rule triggered on form submission.
2. Set condition: When a form submission occurs, send the template created in Step 3 directly to the form submitter ({Email}).
   *(Note: Adding employees as Team Members is no longer required for self-attendance, as authorization is dynamically generated and sent to the submitter via {Full Scanner}).*

### Step 5: Employee Office PC One-Time Authorization
1. Employee submits the form and receives the confirmation email on their office computer.
2. Employee opens the email in their main browser and clicks the {Full Scanner} link once.
3. System grants device permission and sets a 7-day rolling authorization cookie (scan_perms).

### Step 6: Daily Attendance Execution Workflow
1. On working days, employee opens their authorized office PC browser.
2. Arrival: Employee clicks {Verify Link} in their email (or saved bookmark) to perform Check-in.
3. Departure: Employee clicks {Verify Link} prior to leaving to perform Check-out.
4. Backend verifies authorization (scan_perms / self_perms), updates ticket state (`checkin:{form_id}:{refCode}`), and refreshes Redis TTL to 30 days.

### Step 7: Automated Dual Real-Time Receipts
Upon every check-in/check-out click:
- Employee Receipt: Dispatched immediately to the employee confirming status change (Checked In / Checked Out) with UTC timestamp and location.
- Admin Audit Trail: Dispatched immediately to the employee and CC'd to the Form Admin for compliance and attendance logs.

## Frequently Asked Questions (Website Q&A Page Engine)

Q: How do I send an email notification every time a new form submission is received?
A: This is the simplest and most essential feature for Form Admins. Go to System Notifications in the FormMail Hub interface, enable notifications, check the Admin and desired Team Members to receive alerts, and click Save. Every new submission will instantly trigger an internal email notification sent via System SMTP to the designated recipients.

Q: How can I route submissions to different team members based on specific response conditions?
A: Create custom Email Templates and set up multi-condition Routing Rules based on the respondent's form answers. Because conditional routing uses custom templates and external recipients, you must first configure and test your custom SMTP settings. Emails will then be dispatched under your custom sender domain/identity.

Q: How do I send custom confirmation emails and instructions directly to the form respondent?
A: Create a custom Email Template containing your instructions and dynamic tags (e.g., {All fields}). Next, create an Auto-responder Rule triggered on submission, and set the target recipient field to the dynamic email tag submitted by the respondent (e.g., {Email}).

Q: Can I set a delay for emails triggered by form submission rules?
A: Yes. When setting up Auto-responder or conditional routing rules, you can configure an optional delivery delay. Admins can specify custom delay durations in seconds, minutes, hours, or days to schedule timed follow-up emails automatically.

Q: Can I proactively send bulk email notifications or campaigns to all form respondents?
A: Yes. Bulk email dispatches (Campaigns) are launched exclusively via the FormMail Hub Google Sheets add-on while your Google Sheet is open. Create a campaign template, configure targeting rules, and set the rule to Campaign mode. In the Sheets sidebar, switch to the Campaign view, select your active campaign, and click Dispatch to execute the bulk email campaign via the cloud platform.

Q: Is the QR Code and Link Check-in feature easy to set up and operate?
A: Yes, setup is straightforward and requires no complex hardware:
1. Dispatch authorization links ({Check-in Scanner}, {Check-out Scanner}, or {Full Scanner}) to staff or respondents to activate scanner permissions directly on their web browser.
2. Include a {QR Code} or direct clickable {Verify Link} in the respondent's confirmation email.
3. Upon arrival, staff scan the QR code with their browser or respondents click the {Verify Link}. Real-time confirmation receipts and audit logs are automatically emailed to the respondent, Form Admin, and designated team members.

Q: What are the main practical applications for the Check-in system?
A: The Check-in feature can be applied across several operational workflows:
- Event ticketing and entry access control.
- Workplace and academic classroom attendance tracking.
- Equipment, asset, or library book loan and return management.

Q: What performance analytics and reports does FormMail Hub provide?
A: FormMail Hub tracks daily and cumulative performance stats for every form, categorized into three distinct execution modes: system (alerts/reports), automation (auto-responders/rules), and campaign (bulk dispatches). Additionally, an automated Daily Summary Report is emailed to the Form Admin at 00:00 every day summarizing the previous day's metrics.

Q: How can Form Admins and respondents manage email preferences and prevent unwanted emails?
A: FormMail Hub provides precise, multi-tiered subscription control:
- Respondents: Custom emails can include the {Unsubscribe link} tag. Clicking this link allows respondents to unsubscribe from or re-subscribe to future automated emails strictly for that specific Form (form-level control).
- Form Admins & Staff: System emails include distinct management links:
  - Daily Summary Reports contain form-specific unsubscribe links (stops daily reports for that single form).
  - System error alerts contain user-level unsubscribe links (stops SMTP failure alerts across all forms managed under that account).

## Feature Boundaries & Anti-Hallucination Rules
22. Email & QR Attendance Scope (NO WEBHOOKS): FormMail Hub operates strictly as an email receiving, processing, dispatching, and QR attendance tracking engine based on admin-defined rules. It DOES NOT support webhooks, HTTP POST forwarding, external API calls, or third-party integrations (such as Slack, Microsoft Teams, Discord, Zapier, CRMs, or custom endpoints).
23. Strict Code-First Reality: Documentation must ONLY reflect existing, verified functionality present in the provided source code and PRODUCT_RULES.md. Writers MUST NOT invent, extrapolate, or draft guides for theoretical features, future roadmaps, or non-existent integrations.

## Official Links & Resources
24. Google Workspace Marketplace Listing: https://workspace.google.com/marketplace/app/formmail_hub/409227874327
25. Privacy Policy: https://formmail.vietutd.com/privacy-policy
26. Terms of Service: https://formmail.vietutd.com/terms-of-service
27. Live Demo Form: https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform
28. Support & Contact: https://formmail.vietutd.com/contact
"""
with open(rules_file, "w", encoding="utf-8") as f:
    f.write(product_rules)

# 2. ĐỌC TÀI LIỆU ĐÃ XUẤT BẢN
existing_docs = {}
if os.path.exists(docs_dir):
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".mdx") or file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_docs[file_path] = f.read()

# 3. THUẬT TOÁN QUÉT MÃ NGUỒN THÔNG MINH
source_files_content = {}
keywords = ['qr', 'checkin', 'checkout', 'template', 'campaign', 'smtp', 'team', 'auth']

all_source_files = []
for root, dirs, files in os.walk("src"):
    if "content/docs" in root:
        continue
    for file in files:
        if file.endswith(('.astro', '.tsx', '.jsx', '.ts', '.js', '.py', '.gs')):
            all_source_files.append(os.path.join(root, file))

priority_sources = [f for f in all_source_files if any(k in f.lower() for k in keywords)]
other_sources = [f for f in all_source_files if f not in priority_sources]

selected_sources = (priority_sources[:8] + other_sources[:4])

for s_file in selected_sources:
    try:
        with open(s_file, "r", encoding="utf-8") as f:
            source_files_content[s_file] = f.read()[:4000]
    except Exception:
        pass

diff_context = code_diff if code_diff else "NO RECENT CODE DIFF."

# 4. PROMPT CẬP NHẬT TRANG CHỦ & TÀI LIỆU DÀNH CHO NGƯỜI DÙNG (FORM ADMIN & DECISION MAKERS)
prompt = f"""
You are an expert Help Center Author & Customer Success Strategist for 'FormMail Hub'.
Your primary mission is to maintain and expand the user-facing documentation suite for **Form Admins, Event Coordinators, HR Managers, and Business Decision-Makers** searching for Google Forms/Sheets automation solutions.

TARGET AUDIENCE & TONALITY GUIDELINES (STRICT COMPLIANCE REQUIRED):
1. **Target Audience**: Non-technical Form Admins, Event Hosts, Office Managers, and Business Users. DO NOT write technical documentation meant for internal software engineers or backend developers.
2. **Tone & Style**: Welcoming, professional, clear, and solution-driven (similar to Stripe, Notion, or HubSpot Help Centers). Focus heavily on **What this feature does for you**, **Step-by-step UI setup instructions**, and **Business Value**.
3. **Hide Backend Jargon & Implementation Details**:
   - Translate internal code mechanics into plain, benefit-driven language.
   - NEVER mention internal source file names (e.g. `templateParser.js`), internal API routes (e.g. `/api/qr/action`), backend keys (`Redis`, `checkin:{form_id}:{refCode}`), or HTTP status codes (`409 Conflict`).
   - Explain security/tech concepts simply: e.g., instead of "HMAC-SHA256 signed payload", write "secure 1-click authorization link"; instead of "Redis TTL 30 days", write "automatically saved in real-time and securely retained for 30 days".
4. **Focus on UI & Practical Workflows**: Clearly describe buttons, tabs, dropdowns, and step-by-step actions inside the Google Forms add-on, Google Sheets add-on, and FormMail Hub web dashboard interface.

ABSOLUTE PRODUCT RULES (GROUND TRUTH - NEVER VIOLATE THESE):
{product_rules}

SAMPLED CODE & API IMPLEMENTATION (Use strictly to understand UI/feature behavior; DO NOT quote raw code files in user guides):
{json.dumps(source_files_content, indent=2)}

RAW CODE DIFF (IF ANY):
{diff_context}

CURRENT PUBLISHED DOCUMENTATION FILES:
{json.dumps(existing_docs, indent=2)}

DOCUMENTATION EXPANSION & HOMEPAGE ARCHITECTURE INSTRUCTIONS:

TASK 0 (MANDATORY USER-FRIENDLY HOMEPAGE MAINTENANCE - `src/content/docs/index.mdx`):
- YOU MUST ALWAYS UPDATE or REVIEW `src/content/docs/index.mdx` to serve as a clean, engaging Portal for Form Admins and prospective users.
- **Visual Structure**: Modern, clean, and inspiring using Starlight / MDX components (`Card`, `CardGrid`, callouts).
- **Value Proposition**: Clearly highlight how FormMail Hub solves Google Forms execution limits, enables seamless QR/Link event ticketing, powers office self-attendance, sends bulk email campaigns from Google Sheets, and manages custom SMTP.
- **Quick Navigation**: Provide intuitive cards leading to practical guides (`/tutorials/qr-event-checkin-guide`, `/guides/smtp-setup`, `/guides/campaigns`, etc.) and official resources.

TASK 1 (PROACTIVE USER-CENTRIC TUTORIAL & GUIDE CREATION):
Analyze documentation gaps. Create or expand step-by-step user guides under `src/content/docs/tutorials/` or `src/content/docs/guides/` for practical workflows (e.g., Event Check-in Ticketing, Office PC Kiosk Attendance, Custom SMTP Configuration, Bulk Campaigns).

TASK 2 (USER ACCESSIBILITY & READABILITY STANDARDS):
Use clear numbered steps, visual callouts (`> **Tip:**`, `> **Note:**`), code blocks for dynamic tags (e.g., `{QR Code}`, `{Verify Link}`, `{Full Scanner}`), and FAQ/Troubleshooting sections.

TASK 3 (STRICT LINK WEAVING & GROUND TRUTH COMPLIANCE):
- Contextually weave official links in created/updated docs (Marketplace Listing, Live Demo Form, Support, Privacy Policy, Terms of Service).
- Ensure 100% adherence to Ground Truths (e.g. No Webhooks, Bulk Campaigns only available in Google Sheets).
- If ALL docs including `src/content/docs/index.mdx` are completely up-to-date, visually appealing, non-technical, and 100% aligned with ground truths, return: `@@@NO_UPDATES_NEEDED@@@`.

STRICT FORMAT DELIMITERS (DO NOT USE JSON):

@@@FILE_PATH: src/content/docs/index.mdx
@@@CONTENT:
---
title: FormMail Hub Help Center & Knowledge Base
description: The complete guide to automated email notifications, QR ticket attendance tracking, and bulk campaigns for Google Forms & Sheets.
template: splash
hero:
  tagline: Enterprise-grade email automation & QR attendance tracking for Google Forms & Sheets.
  actions:
    - text: Get Started Guide
      link: /tutorials/qr-event-checkin-guide/
      icon: right-arrow
    - text: Try Live Demo Form
      link: https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform
      icon: external
      variant: minimal
---

import {{ Card, CardGrid }} from '@astrojs/starlight/components';

## Why Choose FormMail Hub?

<CardGrid stack>
  <Card title="Independent Cloud Power" icon="rocket">
    Bypasses native Google Workspace limits to reliably process high-volume email workflows and submission triggers in real time.
  </Card>
  <Card title="App-Free QR & Link Check-in" icon="approve-check">
    Equip event staff or employees with secure 1-click scanner links ({{Check-in Scanner}}) for camera or browser verification without logins.
  </Card>
  <Card title="Dual Real-Time Receipts" icon="email">
    Automatically dispatches attendance confirmation emails to respondents while sending instant audit logs to staff and managers.
  </Card>
  <Card title="Google Sheets Campaign Hub" icon="document">
    Launch targeted bulk email campaigns directly from your responses spreadsheet using customizable filters and templates.
  </Card>
</CardGrid>

(Additional rich markdown content, guides index, and official links...)
@@@END_FILE
"""

try:
    print("⏳ Đang gửi dữ liệu cho AI phân tích, thiết kế Trang Chủ & hoàn thiện bài viết...")
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    cleaned_text = response.text.strip()
    docs_to_update = []
    blocks = cleaned_text.split("@@@FILE_PATH:")
    
    for block in blocks:
        if not block.strip():
            continue
            
        if "@@@CONTENT:" in block and "@@@END_FILE" in block:
            try:
                path_part, rest = block.split("@@@CONTENT:", 1)
                file_path = path_part.strip()
                content = rest.split("@@@END_FILE")[0].strip()
                
                docs_to_update.append({
                    "file_path": file_path,
                    "content": content
                })
            except Exception as ex:
                print(f"⚠️ Bỏ qua block do lỗi phân tách: {ex}")
                continue

    if not docs_to_update:
        if "@@@NO_UPDATES_NEEDED@@@" in cleaned_text:
            print("✅ AI BÁO CÁO: Trang chủ và toàn bộ tài liệu đã đạt chuẩn sáng tạo, trực quan và khớp 100% Ground Truth.")
            sys.exit(0)
        else:
            print("❌ LỖI: AI không trả về block nội dung hợp lệ nào.")
            print(cleaned_text)
            sys.exit(1)

    # 5. GHI FILE VÀ CẬP NHẬT
    for item in docs_to_update:
        file_path = item.get("file_path")
        content = item.get("content")
        
        if file_path == "PRODUCT_RULES.md":
            target_path = "PRODUCT_RULES.md"
        else:
            if not file_path.startswith("src/content/docs"):
                file_path = file_path.lstrip("/") 
                target_path = os.path.join("src/content/docs", file_path)
            else:
                target_path = file_path

        os.makedirs(os.path.dirname(target_path) if os.path.dirname(target_path) else ".", exist_ok=True)
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
            
        print(f"✅ Đã ghi nhận/Cập nhật file: {target_path}")

except Exception as e:
    print(f"❌ LỖI khi thực thi script: {e}")
    sys.exit(1)
