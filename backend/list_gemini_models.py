#!/usr/bin/env python3
"""List available Gemini models."""
import google.generativeai as genai
import os

# Configure API key
api_key = os.getenv("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_HERE")
genai.configure(api_key=api_key)

print("Available Gemini models:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model: {model.name}")
        print(f"  Display name: {model.display_name}")
        print(f"  Description: {model.description}")
        print()
