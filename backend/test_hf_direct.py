import requests
import os
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

def test_model(model_id):
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}
    prompt = "Write a short email for a job application."
    
    print(f"Testing direct endpoint for {model_id}...")
    try:
        resp = requests.post(API_URL, headers=headers, json={"inputs": prompt, "parameters": {"max_new_tokens": 50}}, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"SUCCESS: {resp.json()}")
            return True
        else:
            print(f"ERROR: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    return False

models_to_test = [
    "mistralai/Mistral-7B-Instruct-v0.2",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "google/gemma-7b-it",
    "google/gemma-2-2b-it",
    "HuggingFaceH4/zephyr-7b-beta",
    "meta-llama/Llama-3.2-1B-Instruct"
]

for m in models_to_test:
    if test_model(m):
        break
