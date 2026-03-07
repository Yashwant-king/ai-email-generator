import requests
import os
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

urls = [
    "https://router.huggingface.co/hf-inference/models/meta-llama/Llama-3.2-3B-Instruct/v1/chat/completions",
    "https://router.huggingface.co/hf-inference/models/meta-llama/Meta-Llama-3-8B-Instruct/v1/chat/completions",
    "https://router.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
    "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.3",
    "https://router.huggingface.co/v1/chat/completions" # with model param
]

headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}

for u in urls:
    print(f"Testing {u}")
    try:
        if "v1/chat/completions" in u:
            payload = {
                "model": "meta-llama/Llama-2-7b-chat-hf", 
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 10
            }
            if "hf-inference/models/" in u:
                del payload["model"] # URL already specifies it, maybe? actually let's just leave it
        else:
            payload = {"inputs": "hi"}
            
        resp = requests.post(u, headers=headers, json=payload, timeout=5)
        print(resp.status_code, resp.text)
    except Exception as e:
        print(f"Error: {e}")
