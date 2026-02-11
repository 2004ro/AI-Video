import requests
import json
import urllib3

# Suppress SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_metadata(topic):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Create YouTube metadata for a video about "{topic}".
    Return a JSON object with the following fields:
    - title: A catchy, clickbait title (under 60 chars).
    - description: A short description (under 200 chars) that includes keywords.
    - tags: A comma-separated list of 10 relevant tags.
    Output ONLY valid JSON.
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Error generating metadata: {response.text}")
            return None
    except Exception as e:
        print(f"Exception generated metadata: {e}")
        return None

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "AI Video Generation"
    print(generate_metadata(topic))
