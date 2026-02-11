import requests
import urllib3

# Suppress SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_script(topic):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system", 
                "content": "You are a professional YouTube Shorts scriptwriter. Create engaging, high-retention scripts."
            },
            {
                "role": "user", 
                "content": f"Write a YouTube Shorts script about {topic}. The script MUST be at least 45 seconds long when spoken (about 150-200 words). Make it punchy, educational, and exciting. Start with a hook and end with a call to action."
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data, verify=False)
    
    if response.status_code != 200:
        print("Error:", response.text)
        return None

    return response.json()["choices"][0]["message"]["content"]
