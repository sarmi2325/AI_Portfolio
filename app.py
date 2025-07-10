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

# Load Claude API Key
load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("Missing Claude API Key. Set CLAUDE_API_KEY in .env file")

# Flask Setup
app = Flask(__name__)

# Session context
chat_history = []
session_context = {
    "last_topic": None,
    "last_response": None,
    "last_response_type": None,
}

# Keywords
RESUME_KEYWORDS = [
    "resume", "cv", "portfolio", "profile", "about", "bio", "background", "introduction", "summary",
    "education", "degree", "college", "university", "school", "academic", "graduation", "cgpa", "marks", "percentage",
    "qualification", "branch", "department", "b.e", "engineering", "instrumentation", "specialization",
    "skills", "skillset", "expertise", "tools", "frameworks", "technologies", "language", "python", "numpy", "keras", "scikit", "shap",
    "project", "projects", "capstone", "final year", "churn", "pneumonia", "linear algebra", "visual toolkit",
    "certification", "certifications", "courses", "nptel", "coursera", "hackerrank", "infosys", "silver", "ai primer",
    "publication", "publications", "conference", "conferences", "paper", "published", "scopus", "icaiss",
    "award", "awards", "achievement", "achievements", "honor", "honours", "trophy", "hackathon",
    "internship", "experience", "work", "training", "job", "role",
    "contact", "email", "linkedin", "github", "reach", "connect", "network", "hire", "collaborate", "collaboration",
    "career", "objective", "goal", "mission", "aspiration",
    "languages spoken", "english", "tamil", "communication", "soft skills",
    "yourself", "tell me", "describe", "who are you", "journey", "story"
]
PERSONAL_KEYWORDS = [
    "father", "mother", "dad", "mom", "parents", "family", "sister", "brother", "siblings",
    "pet", "dog", "rythm", "patti", "thatha", "grandmother", "grandfather",
    "cooking", "cook", "kitchen", "food", "recipe",
    "drawing", "painting", "sketching", "craft", "craftwork", "hobby", "hobbies", "interests", "interest",
    "shinchan", "anime", "drama", "tv", "movie", "cinema", "netflix", "watch",
    "personality", "fun", "relax", "free time", "what do you do", "how are you", "what are you doing",
    "born", "age", "location", "place", "from where"
]
THANGLISH_HINTS = [
    "enna", "epdi", "epdi iruka", "iruka", "sapudra", "sapta", "pasanga", "poda", "sollu", "velai", "padikka", "padichinga","unnaku"
    "vera", "pesa", "theriyuma", "solra", "eppadi", "yenga", "enaku", "ungalukku", "neenga", "thambi", "akka", "sari",
    "romba", "siriya", "ennoda", "periya", "machan", "machi", "veetla", "kadha", "kadhal", "kandippa", "aama", "illa",
    "naan", "nee", "avan", "ava", "ivanga", "inga", "unga", "enga", "ethuku", "edhuku", "paathu", "seriya", "enna panra", "sathiyama"
]
FOLLOWUP_HINTS = ["that", "this", "one", "more", "continue", "yes", "tell", "explain",'yes ofcourse',"i do","think","ok","okay"]

def preprocess(text):
    return re.sub(r'\b(she|her|sarmitha)\b', 'you', text, flags=re.IGNORECASE)

def is_thanglish(text):
    return any(word in text.lower() for word in THANGLISH_HINTS)

def is_resume_related(text):
    return any(word in text.lower() for word in RESUME_KEYWORDS)

def is_personal_related(text):
    return any(word in text.lower() for word in PERSONAL_KEYWORDS)

def is_followup(text):
    return any(word in text.lower() for word in FOLLOWUP_HINTS)

def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"

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

    # Detect language
    user_lang = detect_language(user_raw)
    # Translate to English for Claude
    user_msg_en = translate_to_english(user_raw)
    user_msg = preprocess(user_msg_en)

    # Build system prompt as usual
    if is_followup(user_msg) and session_context["last_response"]:
        system_prompt = (
            f"{SYSTEM_PROMPT['content']}\n\n"
            f"Previous Response:\n{session_context['last_response']}\n\n"
            f"Follow-up User Question: {user_msg}\n"
            f"Give a relevant follow-up answer using my previous reply."
        )
    elif is_resume_related(user_msg):
        context = "\n".join(retrieve(user_msg, top_k=6))
        if "project" in user_msg:
            system_prompt = get_project_prompt(context, user_msg)
            session_context["last_topic"] = "project"
        elif "skill" in user_msg:
            system_prompt = get_skills_prompt(context, user_msg)
            session_context["last_topic"] = "skills"
        elif "contact" in user_msg:
            system_prompt = get_contact_prompt(context, user_msg)
            session_context["last_topic"] = "contact"
        elif "about" in user_msg or "yourself" in user_msg:
            system_prompt = get_about_prompt(context, user_msg)
            session_context["last_topic"] = "about"
        else:
            system_prompt = SYSTEM_PROMPT['content'] + f"\n\nUser Question: {user_msg}"
            session_context["last_topic"] = "general"
    elif is_personal_related(user_msg):
        system_prompt = get_personal_prompt("", user_msg)
        session_context["last_topic"] = "personal"
    elif any(greet in user_msg.lower() for greet in ["hi", "hello", "hey", "vanakkam"]):
        return jsonify({"response": "Hi! 😊 I'm <b>Sarmitha</b> — an AI/ML enthusiast from Tamil Nadu.<br>Wanna explore my projects, skills, or just chat about tech? 🚀"})
    else:
        return jsonify({"response": "I'm not sure what you mean. 😊 Try asking about my projects, skills, or background."})

    chat_history.append({"role": "user", "content": user_msg})
    answer = ask_claude(chat_history + [{"role": "user", "content": system_prompt}])
    chat_history.append({"role": "assistant", "content": answer})
    session_context["last_response"] = answer

    # If the user's language was not English, add a flavor note in English
    if user_lang != "en":
        # Optionally, you can use a mapping to show the language name (e.g., 'hi'->'Hindi')
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






