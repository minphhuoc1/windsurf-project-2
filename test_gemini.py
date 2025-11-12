import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
assert api_key, "Missing GEMINI_API_KEY in .env"

# Cấu hình Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")  # nhanh, rẻ; có thể đổi sang 1.5-pro nếu muốn

# Prompt test: viết email xin nghỉ phép
prompt = """You are an assistant that writes concise, professional business emails in English.
Write a short, polite leave request email for one day off next Monday.
Output format:
Subject: ...
Body:
..."""

resp = model.generate_content(prompt)
print(resp.text.strip())
