import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.environ.get("API_KEY")
ENDPOINT = os.environ.get("ENDPOINT")

def call_gemini_api(messages):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        "model": "gemini-1.5-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512
    }
    response = requests.post(ENDPOINT, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']
