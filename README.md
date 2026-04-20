# 🚀 AI Email Generator (Premium)

A cutting-edge, full-stack AI platform that leverages **Google Gemini 1.5 Flash** and **Hugging Face (Llama 3 / Qwen)** to craft professional, high-converting emails in seconds. 

This project is now "Dual-Stack", supporting both a modern JavaScript/React workflow and a streamlined Python/Streamlit workflow.

---

## ✨ Features
-   **Multi-Model Intelligence**: Uses Gemini 1.5 Flash for high-speed drafting and Hugging Face (Qwen 72B / Llama 3.1) as a powerful alternative.
-   **Dual Frontend Options**:
    -   **Streamlit (Recommended)**: A sleek, dark-themed Python frontend for quick deployment and zero-JS overhead.
    -   **React + Vite**: A high-performance, modular frontend for scalable web applications.
-   **Smart History**: Automatically saves your generations to a local SQLite database.
-   **Premium UI**: Custom CSS with glassmorphism, micro-animations, and a responsive design system.

---

## 🛠️ Project Structure
```text
ai-email-generator/
├── streamlit_app.py   # Primary Streamlit Dashboard (Python)
├── requirements.txt   # Python Dependencies
├── backend/           
│   ├── main.py        # FastAPI Backend (Python)
│   ├── index.js       # Express Backend (Node.js)
│   ├── emails.db      # SQLite Generation History
│   └── .env           # API Keys configuration
├── frontend/          
│   ├── src/           # React Source Code
│   ├── index.html     # Alpine.js / CDN Version
│   └── package.json   # Node build configuration
└── render.yaml        # Deployment Blueprint (Render.com)
```

---

## 🏃‍♂️ Quick Start (Streamlit)
**The fastest way to get started.**

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure API Keys**:
    Open `backend/.env` and add your Hugging Face API key:
    ```text
    HF_API_KEY=your_key_here
    ```
3.  **Run the app**:
    ```bash
    streamlit run streamlit_app.py
    ```

---

## 🏗️ Technical Setup (Deep Dive)

### Python (FastAPI + Streamlit)
-   **Backend**: `main.py` handles the logic for generation and DB storage.
-   **Frontend**: `streamlit_app.py` provides the user interface.

### Javascript (Express + React)
1.  **Backend**:
    ```bash
    cd backend
    npm install
    node index.js
    ```
2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

---

## 🚀 Deployment
This project is configured for **Render.com**. Just connect your repository, and it will automatically deploy the Streamlit frontend using the provided `render.yaml`.

---

Build with ❤️ by [Yashwant Singh Chauhan](https://github.com/Yashwant-king)
