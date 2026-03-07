import requests
import os
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

urls = [
    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3/v1/chat/completions",
    "https://api-inference.huggingface.co/v1/chat/completions",
    "https://router.huggingface.co/v1/chat/completions",
    "https://router.huggingface.co/hf-inference/v1/chat/completions"
]

for url in urls:
    print(f"Testing {url}...")
    try:
        resp = requests.post(url, headers=headers, json={
            "model": "mistralai/Mistral-7B-Instruct-v0.3",
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 10
        }, timeout=5)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("SUCCESS!")
            print(resp.json())
            break
        else:
            print(resp.text)
    except Exception as e:
        print(f"Error: {e}")
