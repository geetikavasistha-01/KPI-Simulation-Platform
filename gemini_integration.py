import requests

API_KEY = 'AIzaSyDM33mSfg-QENvSGyS4Y1MOvWdiGsP5MZI'
ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'


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