import os
import sys
import json
import glob
from google import genai

print("========================================")
print("🚀 AI MULTI-PAGE DOCS BUILDER & EXPANDER")

MODEL_NAME = "gemini-3.6-flash" 
print(f"🤖 Gemini model: {MODEL_NAME}")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ LỖI: Chưa tìm thấy GEMINI_API_KEY trong Repo Secrets!")
    sys.exit(1)

client = genai.Client(api_key=api_key)
code_diff = os.environ.get("CODE_DIFF", "")
docs_dir = "src/content/docs"
rules_file = "PRODUCT_RULES.md"

# 1. ĐỌC HOẶC KHỞI TẠO FILE GROUND TRUTH
product_rules = ""
if os.path.exists(rules_file):
    with open(rules_file, "r", encoding="utf-8") as f:
        product_rules = f.read()
else:
    print(f"⚠️ Chưa tìm thấy {rules_file}, đang khởi tạo...")
    product_rules = """# PRODUCT RULES & ABSOLUTE TRUTHS

1. Team Member Logic: Team members are ONLY added so the Admin can select who receives email notifications. Team members DO NOT have edit or configuration permissions.
2. Primary Connector / Admin Role: Only the first user among the form's editors who connects that form to FormMail Hub is granted exclusive rights to configure settings, templates, and triggers for that form.
3. Ecosystem: FormMail Hub connects from 3 Google Forms add-ons ("Form Confirmation Emails", "Form to Email", "Form Notifications SMTP").
4. Full-Featured Application: The Google Sheets add-on named "FormMail Hub" is the full-featured application of the ecosystem.
5. Campaign Availability: Bulk sending (Campaigns) is ONLY available when launched from the Google Sheets add-on.
6. Campaign Creation & Dispatch Workflow: To send a proactive campaign to form respondents, the Admin creates a campaign template, configures filtering rules to target specific respondents in the responses Google Sheet, and enables the rule as an active campaign. Then, within the FormMail Hub Google Sheets add-on interface on the responses sheet, the Admin switches to the Campaign view, selects the synchronized campaign name, and clicks the 'Dispatch' button to initiate the bulk email dispatch.
7. Custom SMTP Requirement: Admins MUST configure custom SMTP settings before creating email templates, rules, campaigns, or accessing analytics, as these features require sending emails under the Admin's own email identity.
8. Built-in System Notifications: System Notifications is an out-of-the-box feature powered by the system's internal SMTP. It sends default-templated submission alerts to the Form Admin and selected Team Members without requiring custom SMTP setup.
9. Form Quota Expansion via Google Sheets: Connecting a spreadsheet via the 'FormMail Hub' Google Sheets add-on enables scaling beyond the standard 20-form limit, because a single spreadsheet can contain multiple Form Responses tabs while using only one active connection.
10. Email-Only Scope (NO WEBHOOKS): FormMail Hub ONLY receives/processes Google Forms submissions and dispatches emails via rules. It DOES NOT support webhooks, HTTP POST calls, or 3rd-party integrations (Slack, Teams, Discord, Zapier). NEVER document unverified webhook or integration features.
11. Dynamic Tags Strict Accuracy: Only dynamic field name tags `{Question Title}` and `{Form Title}` are valid unless explicitly parsed in backend code. DO NOT invent tags like `{Form Summary}`, `{Response ID}`, `{Submission Date}`, or `{Submitter Email}`.
"""
    with open(rules_file, "w", encoding="utf-8") as f:
        f.write(product_rules)

# 2. ĐỌC TÀI LIỆU ĐÃ XUẤT BẢN (NẾU CÓ)
existing_docs = {}
if os.path.exists(docs_dir):
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".mdx") or file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_docs[file_path] = f.read()

# 3. CHIẾN LƯỢC CHỌN MÃ NGUỒN CÓ GIỚI HẠN (TRÁNH QUÁ TẢI PROMPT)
source_files_content = {}
ui_extensions = ('.astro', '.tsx', '.jsx', '.html', '.svelte', '.vue')
backend_extensions = ('.ts', '.js', '.py', '.gs')

all_source_files = []
for root, dirs, files in os.walk("src"):
    if "content/docs" in root:
        continue
    for file in files:
        if file.endswith(ui_extensions) or file.endswith(backend_extensions):
            all_source_files.append(os.path.join(root, file))

ui_sample = [f for f in all_source_files if f.endswith(ui_extensions)][:2]
backend_sample = [f for f in all_source_files if f.endswith(backend_extensions)][:2]
selected_sources = ui_sample + backend_sample

for s_file in selected_sources:
    try:
        with open(s_file, "r", encoding="utf-8") as f:
            source_files_content[s_file] = f.read()[:3000]
    except Exception as e:
        pass

diff_context = code_diff if code_diff else "NO RECENT CODE DIFF. Focus on sampled source files or published docs audit."

# 4. TẠO PROMPT
prompt = f"""
You are an expert technical writer and documentation architect for 'FormMail Hub'.

ABSOLUTE PRODUCT RULES (GROUND TRUTH - NEVER VIOLATE THESE):
{product_rules}

SAMPLED SOURCE CODE FILES FOR THIS SESSION (UI + BACKEND):
{json.dumps(source_files_content, indent=2)}

RAW CODE DIFF (IF ANY):
{diff_context}

CURRENT PUBLISHED DOCUMENTATION FILES:
{json.dumps(existing_docs, indent=2)}

INSTRUCTIONS & WORKFLOW PRIORITY:

PRIORITY 1 (NEW FEATURE DISCOVERY):
- Examine the SAMPLED SOURCE CODE FILES and RAW CODE DIFF.
- If you find ANY verified, absolute feature logic/rule that is missing from 'PRODUCT RULES', UPDATE `PRODUCT_RULES.md` first.
- Write or expand the corresponding documentation file in `src/content/docs/guides/` or `src/content/docs/reference/`.

PRIORITY 2 (DOCS AUDIT & CORRECTION):
- If the source code reveals no new un-documented features, AUDIT the existing published docs in `CURRENT PUBLISHED DOCUMENTATION FILES`.
- If a published doc violates `PRODUCT RULES` or contains unverified features, REWRITE and REJECT the inaccurate sections to align strictly with `PRODUCT RULES`.
- IF ALL PUBLISHED DOCS ARE 100% ACCURATE AND NO FILES NEED UPDATING, include the token `@@@NO_UPDATES_NEEDED@@@` in your output.

STRICT REQUIREMENTS:
1. ALL OUTPUT MUST BE STRICTLY IN ENGLISH.
2. FRONTMATTER: Docs must have valid YAML (title, description).
3. DO NOT USE JSON OUTPUT FORMAT! Use the exact custom delimiters shown below when updating files.

FORMAT TEMPLATE TO FOLLOW WHEN UPDATING FILES:

@@@FILE_PATH: PRODUCT_RULES.md
@@@CONTENT:
(Updated content of PRODUCT_RULES.md if a new truth was found)
@@@END_FILE

@@@FILE_PATH: src/content/docs/guides/team-management.mdx
@@@CONTENT:
---
title: Corrected Guide Title
description: Accurate description here
---
Your markdown content here...
@@@END_FILE
"""

try:
    print("⏳ Đang gửi dữ liệu cho AI phân tích...")
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

    # XỬ LÝ TRƯỜNG HỢP AI AUDIT THẤY MỌI THỨ ĐÃ CHUẨN (KHÔNG CẦN SỬA FILE NÀO)
    if not docs_to_update:
        if "@@@NO_UPDATES_NEEDED@@@" in cleaned_text or "Audit" in cleaned_text or "Compliant" in cleaned_text:
            print("✅ AI BÁO CÁO: Tất cả tài liệu hiện tại đã khớp 100% với PRODUCT_RULES.md. Không cần cập nhật file.")
            print("\n--- BÁO CÁO KIỂM TRA TỪ AI ---")
            print(cleaned_text)
            print("--------------------------------\n")
            sys.exit(0) # Thoát thành công (exit code 0)
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
            
        print(f"✅ Đã cập nhật: {target_path}")

except Exception as e:
    print(f"❌ LỖI khi thực thi script: {e}")
    sys.exit(1)
