# 🚀 AI Email Generator (End-to-End)

A premium, full-stack AI platform that leverages **Google Gemini 1.5 Flash** to craft high-converting emails in seconds.

## 🛠️ Tech Stack
-   **Frontend**: React (Vite) + Tailwind CSS + Lucide Icons
-   **Backend**: Node.js + Express
-   **AI Engine**: Google Generative AI (Gemini API)
-   **State Management**: React Hooks
-   **API Communication**: REST via Axios

---

## 🏃‍♂️ How to Run Locally

### 1. Prerequisites
-   Node.js installed (v18+)
-   A **Google Gemini API Key**. Get one [here](https://aistudio.google.com/app/apikey).

### 2. Backend Setup
1.  Navigate to the `backend` folder:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Create a `.env` file from the template:
    ```bash
    cp .env.example .env
    ```
4.  Open `.env` and add your `GEMINI_API_KEY`.
5.  Start the backend server:
    ```bash
    node index.js
    ```
    *Server will be running at `http://localhost:5000`*

### 3. Frontend Setup
1.  Open a **new terminal** and navigate to the `frontend` folder:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    *Vite will provide a local URL (e.g., `http://localhost:5173`)*

---

## 📂 Project Structure
```text
ai-email-generator/
├── backend/       # Express server & Gemini integration
├── frontend/      # React application (Vite + Tailwind)
└── api/           # Placeholder for shared API logic
```

## ✨ Key Features
-   **Intelligent Prompting**: Custom logic ensures Gemini generates structured JSON for both subject and body.
-   **Premium UI**: Glassmorphism effects, micro-animations, and a responsive design system.
-   **One-Click Copy**: Instantly copy your generated email to the clipboard.
-   **Error Resilience**: Handles empty fields and API failures gracefully.

---
Built with ❤️ by Antigravity AI
