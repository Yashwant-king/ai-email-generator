import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(api_key=HF_API_KEY)

models = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "google/gemma-2-2b-it",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-Nemo-Instruct-2407"
]

for model in models:
    print(f"Testing {model} using InferenceClient...")
    try:
        messages = [{"role": "user", "content": "Write a short email. Reply with JSON only: {'subject': '...', 'email': '...'}"}]
        # The new chat completion api might be available directly
        response = client.chat_completion(
            model=model,
            messages=messages,
            max_tokens=100
        )
        print("SUCCESS:", response.choices[0].message.content)
        break
    except Exception as e:
        print(f"FAILED: {e}")
