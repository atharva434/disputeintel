import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai

# Load Env
load_dotenv(find_dotenv(), override=True)
api_key = os.getenv("GOOGLE_API_KEY")

print(f"Checking Key: {api_key[:5]}... (Len: {len(api_key)})" if api_key else "No Key Found")

if not api_key:
    print("Error: No GOOGLE_API_KEY found in .env")
    exit(1)

genai.configure(api_key=api_key)


print("\n--- Listing ALL Available Models ---")
try:
    for m in genai.list_models():
        print(f"Model: {m.name}")
        print(f"   - Methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")
