
import google.generativeai as genai
import os

api_key = "AIzaSyBckeYbBT0L9vA3EyRK0stPK3NPKcyYCHI"
genai.configure(api_key=api_key)

try:
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
