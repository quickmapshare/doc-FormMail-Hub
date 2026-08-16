import os
import sys
import json
from google import genai

print("========================================")
print("🚀 AI MULTI-PAGE DOCS BUILDER & EXPANDER")

MODEL_NAME = "gemini-1.5-flash"
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

prompt = f"""
You are an expert technical writer and documentation architect for 'FormMail Hub'.
Your task is to analyze the source code changes and dramatically expand the documentation.

RAW CODE DIFF FROM SOURCE REPOSITORY:
{code_diff}

CURRENT DOCUMENTATION FILES:
{json.dumps(existing_docs, indent=2)}

STRICT REQUIREMENTS:
1. ALL OUTPUT MUST BE STRICTLY IN ENGLISH.
2. PROACTIVE EXPANSION: Evaluate the CURRENT DOCUMENTATION FILES. If the documentation is sparse, basic, or lacks detailed sections, DO NOT just stop at describing the small code diff.
3. ONE PAGE PER UPDATE: Look at the context of the diff or general app logic, identify ONE main user interface page, component, or core feature, and WRITE A DETAILED GUIDE about it. Describe its purpose, how users interact with it, and its benefits.
4. DECISION LOGIC: Based on your expansion, decide whether to dramatically UPDATE an existing file (e.g., 'index.mdx') OR CREATE a completely NEW file for this feature (e.g., 'src/content/docs/features/new-ui-page.mdx'). 
5. FRONTMATTER: Every file MUST have valid Frontmatter YAML at the top (title, description). Do not change existing frontmatter or custom badges on 'index.mdx'.
6. JSON OUTPUT ONLY: You must return a valid JSON array containing the files to write. Do not wrap the JSON in Markdown code blocks like ```json. Return pure JSON.

JSON STRUCTURE FORMAT:
[
  {{
    "file_path": "src/content/docs/your-file-name.mdx",
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
    
    try:
        docs_to_update = json.loads(cleaned_text)
    except json.JSONDecodeError:
        print("❌ LỖI: AI không trả về đúng chuẩn JSON. Dữ liệu thô:")
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
