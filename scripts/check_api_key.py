import os

def check_api_key():
    key = os.getenv('GROQ_API_KEY')
    if key:
        print(f"API Key is set: {key}")
    else:
        print("API Key is not set.")

check_api_key()
