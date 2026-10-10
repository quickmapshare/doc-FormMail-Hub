"""
Đề xuất cập nhật tài liệu FormMail Hub từ diff mã nguồn (v4, chế độ đề xuất).

Thay đổi so với v3 (2026-10-10):
- Không còn viết lại trang chủ và tạo trang mới mỗi lần chạy (nguyên nhân sinh nội dung trùng lặp, bị Google gỡ index).
- Chỉ sửa các trang ĐÃ CÓ khi diff thực sự làm chúng sai. Không có diff thì không làm gì.
- Luật sản phẩm đọc từ PRODUCT_RULES.md (sửa file đó là đủ), script không ghi đè file này nữa.
- Kết quả được mở thành Pull Request để người duyệt (xem .github/workflows/ai-docs-update.yml), không push thẳng lên main.
"""
import os
import sys

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")
DOCS_DIR = "src/content/docs"
RULES_FILE = "PRODUCT_RULES.md"
NO_UPDATES = "@@@NO_UPDATES_NEEDED@@@"

print(f"🤖 Docs updater v4 (đề xuất PR) · model {MODEL_NAME}")

code_diff = os.environ.get("CODE_DIFF", "").strip()
if not code_diff:
    print("ℹ️ Không có code diff, không cần cập nhật tài liệu.")
    sys.exit(0)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ Thiếu GEMINI_API_KEY trong Repo Secrets.")
    sys.exit(1)

with open(RULES_FILE, encoding="utf-8") as f:
    product_rules = f.read()

existing_docs = {}
for root, _dirs, files in os.walk(DOCS_DIR):
    for name in sorted(files):
        if name.endswith((".md", ".mdx")):
            path = os.path.join(root, name).replace(os.sep, "/")
            with open(path, encoding="utf-8") as f:
                existing_docs[path] = f.read()

docs_block = "\n\n".join(
    f"===== FILE: {path} =====\n{content}" for path, content in existing_docs.items()
)

prompt = f"""You maintain the user documentation of FormMail Hub (a Google Forms / Google Sheets email add-on).
A developer just changed the product source code. Your only job: decide whether this change makes any EXISTING page
wrong or incomplete, and if so, propose the smallest edit that fixes it.

HARD RULES
1. Edit existing files only. The allowed paths are exactly the FILE paths listed below. Never create, rename or delete files.
2. Most code changes (refactors, bug fixes, internal tooling, styling) need no documentation change. In that case answer only: {NO_UPDATES}
3. Change only the sentences affected by the diff. Keep everything else in the file byte-for-byte identical, including the frontmatter.
4. Every statement must be supported by PRODUCT_RULES.md or by the diff. Never guess. Never add marketing language.
5. Write for Form Admins: plain English, short sentences, UI names as the user sees them. No file names, API paths, database keys or code.
6. Do not copy secrets, keys, passwords, email addresses or URLs from the diff into the docs.

PRODUCT_RULES.md (ground truth):
{product_rules}

CODE DIFF (may be truncated):
{code_diff}

CURRENT DOCUMENTATION:
{docs_block}

OUTPUT FORMAT
Either exactly {NO_UPDATES}
or, for each file you change, the COMPLETE new file content:
@@@FILE_PATH: <one of the listed paths>
@@@CONTENT:
<full file content>
@@@END_FILE
"""

from google import genai  # import muộn: không có diff thì không cần thư viện

client = genai.Client(api_key=api_key)
print("⏳ Đang gửi diff cho AI đánh giá...")
try:
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    text = (response.text or "").strip()
except Exception as e:
    print(f"❌ Lỗi gọi Gemini: {e}")
    sys.exit(1)

if text.startswith(NO_UPDATES) or (NO_UPDATES in text and "@@@FILE_PATH:" not in text):
    print("✅ AI: diff này không làm tài liệu sai, không cần sửa.")
    sys.exit(0)

changed = 0
for block in text.split("@@@FILE_PATH:")[1:]:
    if "@@@CONTENT:" not in block or "@@@END_FILE" not in block:
        print("⚠️ Bỏ qua một block sai định dạng.")
        continue
    path_part, rest = block.split("@@@CONTENT:", 1)
    path = path_part.strip().lstrip("/")
    content = rest.split("@@@END_FILE", 1)[0].strip() + "\n"

    if path not in existing_docs:
        print(f"⚠️ Bỏ qua {path}: không phải trang đã có (bot không được tạo trang mới).")
        continue
    parts = content.split("---", 2)
    if not content.startswith("---") or len(parts) < 3 or "title:" not in parts[1]:
        print(f"⚠️ Bỏ qua {path}: mất frontmatter/title.")
        continue
    old = existing_docs[path]
    if len(content) < 0.5 * len(old):
        print(f"⚠️ Bỏ qua {path}: nội dung mới ngắn hơn một nửa bản cũ, có thể bị cắt.")
        continue
    if content == old:
        continue

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    changed += 1
    print(f"✏️ Đề xuất sửa: {path}")

if changed == 0:
    print("ℹ️ Không có thay đổi hợp lệ nào được ghi.")
else:
    print(f"✅ Đã ghi {changed} file. Workflow sẽ mở Pull Request để duyệt.")
