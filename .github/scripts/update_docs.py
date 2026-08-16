import os
import sys
from google import genai

print("========================================")
print("🚀 UPDATE DOCS SCRIPT")

# Khai báo model ở đây để dùng chung
MODEL_NAME = "gemini-2.5-flash"
print(f"🤖 Gemini model: {MODEL_NAME}")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ LỖI: Chưa tìm thấy GEMINI_API_KEY trong Repo Secrets!")
    sys.exit(1)

client = genai.Client(api_key=api_key)
code_diff = os.environ.get("CODE_DIFF", "")
file_path = "src/content/docs/index.mdx"

if not os.path.exists(file_path):
    print(f"❌ LỖI: Không tìm thấy file {file_path}")
    sys.exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    current_mdx = f.read()

prompt = f"""
You are an expert technical writer for FormMail Hub documentation.
Analyze the following source code diff (changes made in the app repository) and update the documentation accordingly.

RAW CODE DIFF FROM SOURCE REPOSITORY:
{code_diff}

CURRENT DOCUMENTATION (index.mdx):
{current_mdx}

STRICT REQUIREMENTS:
1. ALL OUTPUT MUST BE STRICTLY IN ENGLISH.
2. Analyze the code diff to understand what feature was added, modified, or removed.
3. Update or append descriptions, features, or details in index.mdx based on these code changes.
4. DO NOT change Frontmatter YAML (at top) or custom HTML badge ("Available on Workspace Marketplace").
5. Return ONLY the raw MDX content without any wrapper like ```mdx.
"""

try:
    # Sử dụng biến MODEL_NAME đã khai báo ở trên
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    cleaned_text = response.text.strip()
    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.split("\n", 1)[1]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text.rsplit("\n", 1)[0]

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text.strip())
    print("✅ Cập nhật thành công file index.mdx bằng Gemini AI!")

except Exception as e:
    print(f"❌ LỖI khi gọi Gemini API: {e}")
    sys.exit(1)
