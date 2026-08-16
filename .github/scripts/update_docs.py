import os
import sys
import json
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

existing_docs = {}
if os.path.exists(docs_dir):
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".mdx") or file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_docs[file_path] = f.read()

diff_context = code_diff if code_diff else "NO RECENT CODE CHANGES. Perform a routine documentation audit and expansion based on the current files."

prompt = f"""
You are an expert technical writer and documentation architect for 'FormMail Hub'.
Your task is to analyze the source code changes and dramatically expand the documentation.

RAW CODE DIFF FROM SOURCE REPOSITORY:
{diff_context}

CURRENT DOCUMENTATION FILES:
{json.dumps(existing_docs, indent=2)}

CRITICAL PRODUCT ARCHITECTURE (ALWAYS KEEP IN MIND):
1. Integration Ecosystem: FormMail Hub can connect from 3 different Google Forms add-ons: "Form Confirmation Emails", "Form to Email", and "Form Notifications SMTP".
2. The Core App: The Google Sheets add-on named "FormMail Hub" is the main character (core application) of the ecosystem.
3. Campaign Feature Logic: The "Campaign" (bulk sending) feature is ONLY enabled and accessible when the dashboard is launched from the Google Sheets add-on. It is NOT available when launched from the Forms add-ons. Reason: Bulk sending requires the responses list data which is stored in the Google Sheet. Always clarify this limitation when documenting the dashboard or campaign features.

STRICT REQUIREMENTS:
1. ALL OUTPUT MUST BE STRICTLY IN ENGLISH.
2. PROACTIVE EXPANSION & AUDIT: Evaluate the CURRENT DOCUMENTATION FILES. Find a feature, technical specification, UI element, or workflow that is missing or under-documented.
3. CONTENT CATEGORIZATION (CRITICAL): Decide what type of documentation is needed:
   - GUIDES (Path: src/content/docs/guides/): Step-by-step tutorials, UI walkthroughs, best practices, and "How-to" workflows.
   - REFERENCE (Path: src/content/docs/reference/): Technical specifications, API details, configuration options, lists of dynamic variable tags, error codes, limits/quotas, or troubleshooting glossaries.
4. ONE TOPIC PER UPDATE: Identify ONE missing topic. Write a highly detailed, comprehensive markdown page for it. Route it to the correct directory (guides/ or reference/) based on the categorization above. You may UPDATE an existing file or CREATE a new one.
5. FRONTMATTER: Every file MUST have valid Frontmatter YAML at the top (title, description).
6. JSON OUTPUT ONLY: You must return a valid JSON array. DO NOT wrap it in ```json.
7. ESCAPING RULES (CRITICAL): 
   - You MUST return perfectly valid JSON.
   - Escape newlines as \\n and double quotes as \\" inside strings. 
   - DO NOT use invalid JSON escapes like `\\|`. 
   - If you write a Markdown table, simply use the standard pipe character `|`. DO NOT escape pipes.

JSON STRUCTURE FORMAT:
[
  {{
    "file_path": "src/content/docs/reference/dynamic-tags.mdx",
    "content": "---\\ntitle: Dynamic Tags Reference\\ndescription: Comprehensive list of all supported dynamic variables and syntax.\\n---\\n\\nFull Markdown content goes here..."
  }}
]
"""

try:
    print("⏳ Đang gửi dữ liệu cho AI phân tích và tự động viết bài...")
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    cleaned_text = response.text.strip()
    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.split("\n", 1)[1]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text.rsplit("\n", 1)[0]
    if cleaned_text.startswith("json\n"):
        cleaned_text = cleaned_text[5:]
    
    try:
        docs_to_update = json.loads(cleaned_text, strict=False)
    except json.JSONDecodeError as e:
        print(f"❌ LỖI: AI không trả về đúng chuẩn JSON. Chi tiết lỗi: {e}")
        print("Dữ liệu thô:")
        print(cleaned_text)
        sys.exit(1)

    for item in docs_to_update:
        file_path = item.get("file_path")
        content = item.get("content")
        
        if not file_path or not content:
            continue
            
        # SỬA LỖI ĐƯỜNG DẪN: Giữ nguyên cấu trúc thư mục con (guides/ hoặc reference/) nếu AI trả thiếu src/content/docs
        if not file_path.startswith("src/content/docs"):
            file_path = file_path.lstrip("/") # Xóa dấu / ở đầu nếu có
            file_path = os.path.join("src/content/docs", file_path)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
            
        print(f"✅ Đã ghi/cập nhật thành công file: {file_path}")

except Exception as e:
    print(f"❌ LỖI khi thực thi kịch bản: {e}")
    sys.exit(1)
