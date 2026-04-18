---
title: Ai Auto Task Agent
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# AI Task Automation Agent - Backend

This repository contains the FastAPI backend for the AI Task Automation Agent. It powers the AI orchestration, tool execution, and manages user data and tasks.

## Deployment on Hugging Face Spaces

This backend is designed to be deployed on Hugging Face Spaces using a custom `Dockerfile`.

### Setup Steps:

1.  **Create a Hugging Face Space:**
    *   Go to [huggingface.co/spaces](https://huggingface.co/spaces) and create a new Space.
    *   Select **Docker** as the SDK.

2.  **Push to your Space:**
    ```bash
    # Navigate to the backend directory
    cd D:/Randum-Project/ai-task-automation-agent/backend

    # Initialize git if not already a git repository
    git init

    # Add your Hugging Face Space as a remote
    git remote add origin https://huggingface.co/spaces/Uzair001/ai-auto-task-agent

    # Add all files, commit, and push
    git add .
    git commit -m "Initial backend deployment for Hugging Face"
    git push origin main
    ```

3.  **Set Environment Variables:**
    *   On your Hugging Face Space page, go to the **Settings** tab.
    *   Under "Repository secrets" or "Environment variables", add all the necessary variables from your local `.env` file.
    *   **Crucial Variables include:**
        *   `DATABASE_URL`
        *   `GROQ_API_KEY`
        *   `JWT_SECRET`
        *   `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `SMTP_SERVER`, `SMTP_PORT`
        *   `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_WABA_ID`, `WHATSAPP_RECIPIENT_NUMBER`, `WHATSAPP_VERIFY_TOKEN`

### Local Development:

To run the backend locally:

1.  **Navigate to the backend directory:**
    ```bash
    cd D:/Randum-Project/ai-task-automation-agent/backend
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    ./venv/Scripts/activate # On Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run database migrations:**
    ```bash
    alembic upgrade head
    ```
5.  **Start the FastAPI server:**
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

## API Endpoints:

Refer to the `/docs` endpoint of your running backend (e.g., `https://uzair001-ai-auto-task-agent.hf.space/docs`) for detailed API documentation.
