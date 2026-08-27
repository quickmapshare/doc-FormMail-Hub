import os
import sys
import json
import glob
import re
from google import genai

print("========================================")
print("🚀 AI MULTI-PAGE DOCS BUILDER & EXPANDER v2.5 (WITH CREATIVE HOMEPAGE ENGINE)")

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
14. Dynamic Tags Strict Accuracy & Isolation: Dynamic template tags are handled by templateParser.js using single-pass scanning. Supported enclosure formats are {Tag}, {{Tag}}, and ${Tag}. The valid built-in system tags are strictly: {Form title}, {Linked form}, {All fields}, {Unsubscribe link}, {QR Code}, {Verify Link}, {Check-in Scanner}, {Check-out Scanner}, and {Full Scanner}, alongside any dynamic form question field title.
15. Stateless QR Code Ticket Mechanics & Camera-Free Check-in: Admins can insert the {QR Code} dynamic tag (renders visual QR code with embedded link) or standalone {Verify Link} dynamic tag (renders a direct clickable verification URL /qr-verify?t=...) into custom email templates (usable in Auto-responders and Campaign emails). These blocks are populated in both Respondent tickets and Staff/Team notification emails. Authorized Users or Staff can perform check-in either by scanning the QR code with their camera or by clicking the direct verification link ({Verify Link}) inside their email without requiring a camera scanner.
16. Personalized Scanner & Device Authentication Links: When routing emails, the platform generates personalized, cryptographically signed Authorization Links ({Check-in Scanner}, {Check-out Scanner}, {Full Scanner}). Each link contains an HMAC-SHA256 signed payload encoding form ID, user identity, authorized action mode (checkin, checkout, or both), and a 7-day expiration token (/qr-auth?t=...). Clicking the link instantly authorizes the user's device browser (setting a secure cookie valid for 7 days) for seamless browser-based scanning or self-attendance without requiring password logins. **Browser Session Isolation Note**: Because authorization relies on a secure cookie set during link activation, opening the link in one browser (e.g., in-app email viewer) will NOT authorize a different browser (e.g., default desktop browser or standalone camera scanner). Users must copy and paste the Auth link directly into the exact browser application used for daily verification.
17. Stateful Attendance Engine & 30-Day Rolling TTL: When an authorized user or staff member accesses the verification link, /api/qr/action verifies device permissions (scan_perms or self_perms) and updates the ticket's explicit state (IN or OUT) under Redis key checkin:{form_id}:{refCode}. Single-ticket restrictions per respondent are enforced natively at the form entry point by enabling "Limit to 1 response" in Google Forms Settings, while the backend engine uses `checkin:{form_id}:{refCode}` as the canonical source of truth for each ticket. Every state change extends the record's TTL to 30 days (2,592,000 seconds) without deleting data. It enforces strict concurrency and status transitions:
    - Check-in: Rejects duplicate check-ins with a 409 Conflict status if the ticket status is already IN. Sets status to IN, logs operator/timestamp, and refreshes key TTL to 30 days.
    - Check-out: Validates that the ticket is currently in IN state before updating status to OUT. Logs operator/timestamp and refreshes key TTL to 30 days instead of deleting the Redis key.
18. Automated Dual Real-Time Attendance Receipts: Upon every successful Check-in or Check-out event, the engine dispatches two independent, real-time email notifications:
    - Attendee Attendance Email: Dispatched to the ticket holder confirming their updated status (Checked In / Checked Out), complete with Event Name, Reference ID, Location (if applicable), and UTC timestamp.
    - Staff/Admin Audit Log Email: Dispatched directly to the operator/user (and CC'd to the Form Owner) recording an audit trail containing attendee identity, ticket reference code, operator identity, and scan timestamp.
19. Internal Automated Self-Service Attendance Model: Organizations can implement internal employee attendance tracking without manually registering Team Members for every submitter. By placing {Full Scanner} followed by {Verify Link} in the auto-responder template sent directly to form submitters, any employee who completes the form receives both authorization and execution links. Employees authorize their office PC browser once via {Full Scanner} and subsequently perform daily Check-in/Check-out via {Verify Link} on that same browser.
20. Unsubscribe Mechanics & Granular Scopes: The system handles unsubscribe requests via Cloud Backend tracking endpoints across 3 strict scopes:
    - Form-Specific Respondent Unsubscribe: Admins can insert {Unsubscribe link} into custom email templates (Auto-responders and Campaign emails). Clicking this link unsubscribes the respondent's email address strictly from future emails related to that specific Form.
    - Form-Specific System Daily Report Unsubscribe: Daily summary report emails sent to Admins/Team Members include an unsubscribe link scoped strictly to that specific Form (stopping daily reports for that form only).
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

## Feature Boundaries & Anti-Hallucination Rules
21. Email & QR Attendance Scope (NO WEBHOOKS): FormMail Hub operates strictly as an email receiving, processing, dispatching, and QR attendance tracking engine based on admin-defined rules. It DOES NOT support webhooks, HTTP POST forwarding, external API calls, or third-party integrations (such as Slack, Microsoft Teams, Discord, Zapier, CRMs, or custom endpoints).
22. Strict Code-First Reality: Documentation must ONLY reflect existing, verified functionality present in the provided source code and PRODUCT_RULES.md. Writers MUST NOT invent, extrapolate, or draft guides for theoretical features, future roadmaps, or non-existent integrations.

## Official Links & Resources
23. Google Workspace Marketplace Listing: https://workspace.google.com/marketplace/app/formmail_hub/409227874327
24. Privacy Policy: https://formmail.vietutd.com/privacy-policy
25. Terms of Service: https://formmail.vietutd.com/terms-of-service
26. Live Demo Form: https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform
27. Support & Contact: https://formmail.vietutd.com/contact
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

# 4. PROMPT CẬP NHẬT TRANG CHỦ SÁNG TẠO VÀ BÁM SÁT 24 RULES
prompt = f"""
You are an elite Technical Author & User Experience Strategist for 'FormMail Hub'.
Your goal is to maintain the documentation suite, ensuring it is 100% compliant with Ground Truths while delivering an engaging, professional, and accessible experience for non-technical users.

ABSOLUTE PRODUCT RULES (GROUND TRUTH - NEVER VIOLATE THESE):
{product_rules}

SAMPLED CODE & API IMPLEMENTATION:
{json.dumps(source_files_content, indent=2)}

RAW CODE DIFF (IF ANY):
{diff_context}

CURRENT PUBLISHED DOCUMENTATION FILES:
{json.dumps(existing_docs, indent=2)}

DOCUMENTATION EXPANSION & HOMEPAGE ARCHITECTURE INSTRUCTIONS:

TASK 0 (MANDATORY CREATIVE HOMEPAGE MAINTENANCE - `src/content/docs/index.mdx`):
- YOU MUST ALWAYS UPDATE or REVIEW `src/content/docs/index.mdx` to reflect the latest platform capabilities according to the 24 Ground Truths.
- **Creative & Visual Structure**: Make the homepage modern, clean, and inspiring. Use Starlight / MDX components if applicable (or standard MDX elements: Hero section, Card / CardGrid components, callouts, and key feature highlights).
- **Core Narrative**: Highlight FormMail Hub's architecture—Independent Cloud Platform Engine bypassing Google limits, 4 Google Ingestion Bridges (3 Forms Add-ons + 1 Sheets Client), Zero-Login QR Scanner Auth, Dual Attendance Receipts, Bulk Campaign Engine, Custom SMTP, and Unsubscribe Scopes.
- **Quick Links**: Provide clear entry points/cards leading to tutorials (`/tutorials/qr-event-checkin-guide`, `/guides/smtp-setup`, `/guides/campaigns`, etc.) and official links (Marketplace, Demo Form, Support).

TASK 1 (PROACTIVE USER-CENTRIC TUTORIAL & GUIDE CREATION):
Analyze documentation gaps. Create or expand guides under `src/content/docs/tutorials/` or `src/content/docs/guides/` for key user workflows (QR Ticketing, Attendance receipts, Campaigns, SMTP setup).

TASK 2 (USER ACCESSIBILITY & READABILITY STANDARDS):
Use step-by-step numbered steps, standard Markdown callouts (`> **Tip:**`, `> **Warning:**`), code cards for tags (e.g. `{{Check-in Scanner}}`), and FAQs/Troubleshooting tables.

TASK 3 (STRICT LINK WEAVING & GROUND TRUTH COMPLIANCE):
- Contextually weave official links in created/updated docs (Marketplace, Demo Form, Support, Privacy, Terms).
- If ALL docs including `src/content/docs/index.mdx` are completely up-to-date, visually appealing, creative, and 100% aligned with ground truths, return: `@@@NO_UPDATES_NEEDED@@@`.

STRICT FORMAT DELIMITERS (DO NOT USE JSON):

@@@FILE_PATH: src/content/docs/index.mdx
@@@CONTENT:
---
title: FormMail Hub Documentation & Knowledge Base
description: The complete guide to automated email notifications, QR ticket attendance tracking, and bulk campaigns for Google Forms & Sheets.
template: splash
hero:
  tagline: Enterprise-grade cloud notification & attendance engine for Google Forms & Sheets.
  actions:
    - text: Get Started
      link: /tutorials/qr-event-checkin-guide/
      icon: right-arrow
    - text: Try Live Demo
      link: https://docs.google.com/forms/d/e/1FAIpQLSc2lkYREd5ePz521uYfBDeumOOoPKeBP87i1aSpwokHdFMIHw/viewform
      icon: external
      variant: minimal
---

import {{ Card, CardGrid }} from '@astrojs/starlight/components';

## Key Ecosystem Features

<CardGrid stack>
  <Card title="Independent Cloud Engine" icon="rocket">
    Bypasses native Google Workspace execution limits and trigger constraints with real-time external queue processing.
  </Card>
  <Card title="Zero-Login QR Scanner" icon="approve-check">
    Equip staff with HMAC-SHA256 signed links ({{Check-in Scanner}}) for instant camera or manual browser check-ins without login friction.
  </Card>
  <Card title="Dual Real-Time Receipts" icon="email">
    Automatically dispatches status confirmation emails to attendees and detailed audit logs to event staff upon every check-in/out.
  </Card>
  <Card title="Google Sheets Campaign Hub" icon="document">
    Launch targeted bulk email campaigns directly from your responses sheet using customizable filters and templates.
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
