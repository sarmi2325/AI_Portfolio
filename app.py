from flask import Flask, request, render_template, jsonify

from rag import retrieve
from system_prompts import (
    SYSTEM_PROMPT,
    get_about_prompt,
    get_skills_prompt,
    get_project_prompt,
    get_contact_prompt,
    get_personal_prompt,
    detect_language,
    translate_to_english
)
import os
import re
import requests
from dotenv import load_dotenv
from langdetect import detect
import joblib

# Load Claude API Key
load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("Missing Claude API Key. Set CLAUDE_API_KEY in .env file")

# Load your trained SVM intent classifier
intent_model = joblib.load("best_intent_classifier.joblib")

# Flask Setup
app = Flask(__name__)

# Session context
chat_history = []
session_context = {
    "last_topic": None,
    "last_response": None,
    "last_response_type": None,
}

def preprocess(text):
    return re.sub(r'\b(she|her|sarmitha)\b', 'you', text, flags=re.IGNORECASE)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/home')
def home1():
    return render_template('home.html')

@app.route("/chat", methods=["POST"])
def chat():
    user_raw = request.json.get("message", "").strip()
    if not user_raw:
        return jsonify({"response": "❗ Please enter a valid message."})

    # Detect language and translate to English
    user_lang = detect_language(user_raw)
    user_msg_en = translate_to_english(user_raw)
    user_msg = preprocess(user_msg_en)

    # Predict intent using SVM model
    intent = intent_model.predict([user_msg])[0]
 
    # Route based on predicted intent
    if intent == "resume":
        context = "\n".join(retrieve(user_msg, top_k=6))
        system_prompt = get_about_prompt(context, user_msg)
        session_context["last_topic"] = "about"
    elif intent == "project":
        context = "\n".join(retrieve(user_msg, top_k=6))
        system_prompt = get_project_prompt(context, user_msg)
        session_context["last_topic"] = "project"
    elif intent == "skills":
        context = "\n".join(retrieve(user_msg, top_k=6))
        system_prompt = get_skills_prompt(context, user_msg)
        session_context["last_topic"] = "skills"
    elif intent == "personal":
        system_prompt = get_personal_prompt("", user_msg)
        session_context["last_topic"] = "personal"
    elif intent == "contact":
        context = "\n".join(retrieve(user_msg, top_k=6))
        system_prompt = get_contact_prompt(context, user_msg)
        session_context["last_topic"] = "contact"
    elif intent == "greeting":
        return jsonify({"response": "Hi! 😊 I'm <b>Sarmitha</b> — an AI/ML enthusiast from Tamil Nadu.<br>Wanna explore my projects, skills, or just chat about tech? 🚀"})
    else:
        return jsonify({"response": "I'm not sure what you mean. 😊 Try asking about my projects, skills, or background."})

    chat_history.append({"role": "user", "content": user_msg})
    answer = ask_claude(chat_history + [{"role": "user", "content": system_prompt}])
    chat_history.append({"role": "assistant", "content": answer})
    session_context["last_response"] = answer

    # Add a note if the user's language wasn't English
    if user_lang != "en":
        lang_note = f"<br><i>(By the way, I noticed you wrote in {user_lang.upper()}. I replied in English for clarity!)</i>"
        answer = answer + lang_note

    return jsonify({"response": answer})

def ask_claude(messages):
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    formatted = [
        {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]} for m in messages[-10:]
    ]
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT["content"],
        "messages": formatted
    }
    try:
        res = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
        result = res.json()
        return result['content'][0]['text'] if 'content' in result else "⚠️ Claude Error"
    except Exception as e:
        print("Claude Exception:", e)
        return "Cannot get answer right now, try again"




