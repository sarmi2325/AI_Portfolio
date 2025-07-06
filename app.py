from flask import Flask, request, render_template, jsonify
from rag import retrieve
from system_prompts import (
    get_about_prompt,
    get_skills_prompt,
    get_project_prompt,
    get_contact_prompt
)
import re
import os
import requests
from dotenv import load_dotenv

# Load API Key
load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

if not CLAUDE_API_KEY:
    raise ValueError("❌ Missing Claude API Key. Set CLAUDE_API_KEY in your .env file.")

app = Flask(__name__)

def preprocess_user_input(user_msg):
    user_msg = re.sub(r'\bher\b', 'you', user_msg, flags=re.IGNORECASE)
    user_msg = re.sub(r'\bshe\b', 'you', user_msg, flags=re.IGNORECASE)
    user_msg = re.sub(r'\bsarmitha\b', 'you', user_msg, flags=re.IGNORECASE)
    return user_msg

@app.route('/')
def home():
    return render_template("chatbot.html")

@app.route('/chat', methods=["POST"])
def chat():
    raw_user_msg = request.json.get("message", "").strip()
    user_msg = preprocess_user_input(raw_user_msg.lower())

    if not user_msg:
        return jsonify({"response": "❗ Please enter a valid message."})

    context_chunks = retrieve(user_msg)[:10]
    context = "\n".join(context_chunks)

    if "project" in user_msg:
        prompt = get_project_prompt(context, user_msg)
    elif "skill" in user_msg:
        prompt = get_skills_prompt(context, user_msg)
    elif "contact" in user_msg:
        prompt = get_contact_prompt(context, user_msg)
    elif "about" in user_msg or "you" in user_msg:
        prompt = get_about_prompt(context, user_msg)
    else:
        prompt = context + f"\n\nUser Question: {user_msg}\n\nRespond clearly and concisely."

    answer = ask_claude(prompt)
    return jsonify({"response": answer})

def ask_claude(prompt):
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
        if res.status_code != 200:
            print("❌ Claude API Error:", res.status_code, res.text)
            return "⚠️ Claude API error."
        result = res.json()
        if "content" in result and isinstance(result["content"], list) and result["content"]:
            answer = result["content"][0].get("text", "").replace("\n", " ")
            return answer if answer else "⚠️ No answer returned from Claude."
        else:
            print("❌ Claude API: Unexpected response format:", result)
            return "⚠️ Claude API: Unexpected response format."
    except Exception as e:
        print("❌ Claude Exception:", e)
        return "⚠️ Connection failed."







