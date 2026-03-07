import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(api_key=HF_API_KEY)

hf_models = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-Nemo-Instruct-2407",
    "HuggingFaceH4/zephyr-7b-beta",
]

for model_id in hf_models:
    try:
        print(f"Trying HF Fallback with {model_id}...")
        prompt = f"Write a professional email for HR. Audience: HR. Tone: Urgent. Purpose: Job App. Key Points: hire me. Return ONLY a raw JSON strictly matching this format without any markdown or text: {{\"subject\": \"...\", \"email\": \"...\"}}"
        messages = [{"role": "user", "content": prompt}]
        
        response = client.chat_completion(
            model=model_id,
            messages=messages,
            max_tokens=500,
            temperature=0.5
        )
        
        content = response.choices[0].message.content
        print(f"RAW CONTENT from {model_id}:\n{repr(content)}\n")
    except Exception as e:
        print(f"ERROR on {model_id}: {e}")
