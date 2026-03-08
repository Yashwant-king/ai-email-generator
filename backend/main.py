import os
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import sqlite3
from typing import List
from datetime import datetime
from huggingface_hub import InferenceClient

# Initialize SQLite database
DB_PATH = "emails.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purpose TEXT,
            tone TEXT,
            audience TEXT,
            points TEXT,
            subject TEXT,
            email_body TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Load environment
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run DB initialization on startup
init_db()

# Request Model
class EmailQuery(BaseModel):
    purpose: str
    tone: str
    audience: str
    points: str


def generate_with_hf(query: EmailQuery):
    """Generate email using Hugging Face Inference API"""
    if not HF_API_KEY:
        raise Exception("Hugging Face API key not configured")

    client = InferenceClient(api_key=HF_API_KEY)

    # Models confirmed available on HF free tier
    hf_models = [
        "Qwen/Qwen2.5-72B-Instruct",
        "meta-llama/Llama-3.1-8B-Instruct",
        "microsoft/Phi-3.5-mini-instruct",
    ]

    prompt = (
        f"Write a professional email.\n"
        f"Purpose: {query.purpose}\n"
        f"Tone: {query.tone}\n"
        f"Audience: {query.audience}\n"
        f"Key Points: {query.points}\n\n"
        f"Return ONLY a JSON object with two keys: 'subject' and 'email'. "
        f"No extra text, no markdown, just the JSON."
    )

    last_error = None
    for model_id in hf_models:
        try:
            print(f"Trying HF model: {model_id}...")
            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=model_id,
                messages=messages,
                max_tokens=700,
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()

            # Try to parse JSON from response
            try:
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    clean_json = json_match.group(0).replace('```json', '').replace('```', '')
                    return json.loads(clean_json)
            except Exception:
                pass

            # Fallback: extract subject/body from plain text
            subject = "AI Generated Email"
            body = content
            lines = content.split('\n')
            for i, line in enumerate(lines[:5]):
                if line.lower().startswith('subject:'):
                    subject = line[8:].strip().replace('**', '')
                    body = '\n'.join(lines[i+1:]).strip()
                    break

            return {"subject": subject, "email": body}

        except Exception as e:
            last_error = f"{model_id}: {e}"
            print(f"HF model {model_id} failed: {e}")
            continue

    raise Exception(f"All models failed. Last error: {last_error}")


def save_to_db(query: EmailQuery, result: dict):
    """Save generated email to SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO history (purpose, tone, audience, points, subject, email_body)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (query.purpose, query.tone, query.audience, query.points,
              result.get("subject", ""), result.get("email", "")))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB save error: {e}")


@app.post("/api/generate-email")
async def generate_email(query: EmailQuery):
    if not query.purpose or not query.audience or not query.points:
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        result = generate_with_hf(query)
        save_to_db(query, result)
        return result
    except Exception as err:
        error_msg = str(err)
        if "429" in error_msg:
            error_msg = "API quota exceeded. Please wait a moment and try again."
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/history")
async def get_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM history ORDER BY id DESC LIMIT 50")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "AI Email Backend is Running! (Powered by Hugging Face)"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
