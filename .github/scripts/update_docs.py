import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

file_path = "src/content/docs/index.mdx"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        current_mdx = f.read()
except FileNotFoundError:
    current_mdx = ""

prompt = f"""
You are a professional technical writer and developer advocate for FormMail Hub.
Your task is to update the documentation in the index.mdx file.

CRITICAL REQUIREMENTS:
1. ALL OUTPUT MUST BE STRICTLY IN ENGLISH.
2. Maintain the Astro/Starlight Frontmatter (YAML at the top) and Starlight components intact (<CardGrid>, <Card>, etc.).
3. Keep the custom HTML badge "Available on Workspace Marketplace" with its `not-content` wrapper unchanged.
4. Refine feature descriptions, headlines, and value propositions based on the project scope.

Current file content:
{current_mdx}

Return ONLY the complete updated MDX file content. Do not wrap the response in markdown code blocks like ```mdx or ```.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

cleaned_text = response.text.strip()
if cleaned_text.startswith("```"):
    cleaned_text = cleaned_text.split("\n", 1)[1]
if cleaned_text.endswith("```"):
    cleaned_text = cleaned_text.rsplit("\n", 1)[0]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(cleaned_text.strip())
