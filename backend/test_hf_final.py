import requests
import os
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

models = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3"
]

urls = [
    "https://api-inference.huggingface.co/v1/chat/completions",
    "https://router.huggingface.co/v1/chat/completions"
]

for url in urls:
    for model in models:
        print(f"Testing {url} with {model}...")
        try:
            resp = requests.post(url, headers=headers, json={
                "model": model,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 10
            }, timeout=10)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("SUCCESS!")
                print(resp.json()['choices'][0]['message']['content'])
                exit(0)
            else:
                print(resp.text)
        except Exception as e:
            print(f"Error: {e}")
