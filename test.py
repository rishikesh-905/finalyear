# test.py
import os
import google.generativeai as genai

# 🔑 Set your API key
GEMINI_API_KEY = "AIzaSyBbK6ScO8yDyuAEzL0l4Xot-xu93gGT-uE"  # Replace with your own key
genai.configure(api_key=GEMINI_API_KEY)

# ✅ List available models for verification
print("Available models for your API key:")
models = genai.list_models()
for m in models:
    print(m.name)

# Use a text-generation model (not an embedding model)
model_name = "models/gemini-2.5-flash"  # choose a supported Gemini Flash model
model = genai.GenerativeModel(model_name)

# Prompt for testing
prompt = (
    "give a chicken dish"
)

# Generate recipe
try:
    response = model.generate_content(prompt)
    print("\nGenerated Recipe:\n")
    print(response.text)
except Exception as e:
    print("❌ Error while generating content:", e)
