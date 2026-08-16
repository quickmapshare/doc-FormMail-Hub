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

# Xác định xem AI đang chạy do có code mới hay chạy định kỳ
diff_context = code_diff if code_diff else "NO RECENT CODE CHANGES. Perform a routine documentation audit and expansion based on the current files."

prompt = f"""
You are an expert technical writer and documentation architect for 'FormMail Hub'.
Your task is to analyze the source code changes and dramatically expand the documentation.

RAW CODE DIFF FROM SOURCE REPOSITORY:
{diff_context}

CURRENT DOCUMENTATION FILES:
{json.dumps(existing_docs, indent=2)}

STRICT REQUIREMENTS:
1. ALL OUTPUT MUST BE STRICTLY IN ENGLISH.
2. PROACTIVE EXPANSION: Evaluate the CURRENT DOCUMENTATION FILES. Find a feature, UI element, or workflow that is currently missing or not explained in detail.
3. ONE PAGE PER UPDATE: Identify ONE missing topic and WRITE A DETAILED GUIDE about it. Describe its purpose, how users interact with it, and its benefits.
4. DECISION LOGIC: Based on your expansion, decide whether to dramatically UPDATE an existing file OR CREATE a completely NEW file for this feature.
5. FRONTMATTER: Every file MUST have valid Frontmatter YAML at the top.
6. JSON OUTPUT ONLY: You must return a valid JSON array. DO NOT wrap it in ```json.
7. ESCAPING RULES: You MUST escape all newlines as \\n and double quotes as \\" inside the JSON string values. DO NOT output actual raw line breaks inside the string.

JSON STRUCTURE FORMAT:
[
  {{
    "file_path": "src/content/docs/guides/missing-feature.mdx",
    "content": "---\\ntitle: Example\\ndescription: Example feature\\n---\\n\\nFull Markdown content goes here..."
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
        # THÊM strict=False: Cho phép Python đọc được các dấu xuống dòng "thực tế" nếu AI quên escape
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
            
        if not file_path.startswith("src/content/docs"):
            file_path = os.path.join("src/content/docs", os.path.basename(file_path))

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
            
        print(f"✅ Đã ghi/cập nhật thành công file: {file_path}")

except Exception as e:
    print(f"❌ LỖI khi thực thi kịch bản: {e}")
    sys.exit(1)
