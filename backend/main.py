import os
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import sqlite3
from typing import List
from datetime import datetime

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

# 1. Load context and environment
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
HF_API_KEY = os.getenv("HF_API_KEY")

app = FastAPI()

# 2. Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run DB initialization on startup
init_db()

# 3. Request Model
class EmailQuery(BaseModel):
    purpose: str
    tone: str
    audience: str
    points: str

from huggingface_hub import InferenceClient

def generate_with_hf(query: EmailQuery):
    """Robust fallback using the official Python client"""
    if not HF_API_KEY or "your_huggingface" in HF_API_KEY:
        raise Exception("Hugging Face API key not configured")

    client = InferenceClient(api_key=HF_API_KEY)

    hf_models = [
        "meta-llama/Llama-3.2-3B-Instruct",
        "mistralai/Mistral-Nemo-Instruct-2407",
        "HuggingFaceH4/zephyr-7b-beta",
    ]

    last_error = None
    for model_id in hf_models:
        try:
            print(f"Trying HF Fallback with {model_id}...")
            prompt = f"Write a professional email for {query.audience}. Tone: {query.tone}. Purpose: {query.purpose}. Key Points: {query.points}. Formatting: Do not include introductory text just the email subject and body."
            messages = [{"role": "user", "content": prompt}]
            
            response = client.chat_completion(
                model=model_id,
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try parsing as JSON if the model happened to return JSON
            try:
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    clean_json = json_match.group(0).replace('```json', '').replace('```', '')
                    return json.loads(clean_json)
            except Exception:
                pass
                
            # If not valid JSON, intelligently extract subject and body
            subject = "AI Generated Email"
            body = content
            lines = content.split('\n')
            for i, line in enumerate(lines[:3]):
                if line.lower().startswith('subject:'):
                    subject = line[8:].strip()
                    body = '\n'.join(lines[i+1:]).strip()
                    break
                    
            return {"subject": subject.replace('**', ''), "email": body}
            
        except Exception as e:
            last_error = f"HF {model_id} error: {e}"
            continue
    
    raise Exception(f"All fallbacks failed. Last error: {last_error}")

@app.post("/api/generate-email")
async def generate_email(query: EmailQuery):
    if not query.purpose or not query.audience or not query.points:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Tier 1: Gemini
    try:
        for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro']:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = f"Email Purpose: {query.purpose}, Tone: {query.tone}, Audience: {query.audience}, Points: {query.points}. Return ONLY JSON subject & email body."
                response = model.generate_content(prompt)
                result = json.loads(response.text.replace('```json', '').replace('```', '').strip())
                
                # Save to database
                try:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO history (purpose, tone, audience, points, subject, email_body)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (query.purpose, query.tone, query.audience, query.points, result["subject"], result["email"]))
                    conn.commit()
                    conn.close()
                except Exception as db_err:
                    print(f"Failed to save to database: {db_err}")
                
                return result
            except Exception as e:
                print(f"Gemini {model_name} failed: {e}")
                continue
    except: pass

    # Tier 2: Hugging Face Fallback
    try:
        result = generate_with_hf(query)
    except Exception as err:
        error_msg = str(err)
        if "429" in error_msg:
            error_msg = "All AI quota limits exceeded (Gemini & HF). Please wait 60 seconds."
        raise HTTPException(status_code=500, detail=error_msg)

    # Save to database
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO history (purpose, tone, audience, points, subject, email_body)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (query.purpose, query.tone, query.audience, query.points, result["subject"], result["email"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to save to database: {e}")

    return result

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
    return {"message": "AI Email Backend Multi-Provider is Running!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
