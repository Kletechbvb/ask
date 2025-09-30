# -*- coding: utf-8 -*-
from fastapi import FastAPI
import uvicorn
import requests

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI(title="Ask API with Gemini", version="1.0")

# ----------------------
# Gemini API Config (hardcoded key ⚠️)
# ----------------------
# 👉 Replace with your actual Gemini API key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
MODEL_NAME = "gemini-2.5-flash"   # or "gemini-2.5-pro"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
    raise ValueError("❌ Please set your GEMINI_API_KEY inside the code.")

# ----------------------
# /ask endpoint (GET so it works in browser)
# ----------------------
@app.get("/ask")
def ask(question: str, context: str):
    """
    Ask Gemini API with a question and context.
    Returns structured JSON.
    """

    # Prompt instructions (instead of system role)
    instruction = """
    You are a helpful study assistant 🤝.
    Format your answers like this:
    • Use numbered sections (1., 2., 3.)
    • Use bullet points (•) and sub-bullets (→)
    • Add emojis (🌱📘💡🎯🧠)
    • Highlight key terms with **BOLD**
    • Show definitions as: **Definition:** ...
    • Keep answers clear and concise.
    If no relevant information is found in the CONTEXT, reply exactly:
    "❌ Sorry, I couldn’t find anything related in your uploads."
    """

    # User full prompt
    user_prompt = f"""
    {instruction}

    CONTEXT:
    {context}

    QUESTION:
    {question}
    """

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}]
            }
        ]
    }

    try:
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        response = requests.post(
            GEMINI_API_URL,
            json=payload,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()

        # Extract answer
        if "candidates" in data and len(data["candidates"]) > 0:
            answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            answer = "❌ Sorry, I couldn’t find anything related in your uploads."

        return {
            "status": "answered" if not answer.startswith("❌") else "no_answer",
            "message": "Answer generated ✅" if not answer.startswith("❌") else answer,
            "answer": None if answer.startswith("❌") else answer,
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Gemini API call failed 🚨: {str(e)}",
            "answer": None,
        }

# ----------------------
# Run server
# ----------------------
if __name__ == "__main__":
    port = 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
