import os
import re
import google.generativeai as genai
from flask import session, current_app
from dotenv import load_dotenv
import logging

# .env file load karo
load_dotenv()

# Create data cleaning logic for chemistry text
def clean_chemistry_text(text: str) -> str:
    # 1. Replace chemical arrows (\rightarrow) with a clean arrow symbol
    text = text.replace(r"\rightarrow", "→")
    
    # 2. Fix chemical subscripts (turns H_2O_2 into H₂O₂)
    subscripts = str.maketrans("0123456789aeiou", "₀₁₂₃₄₅₆₇₈₉ₐₑᵢₒᵤ")
    text = re.sub(r'_([0-9a-euieo])', lambda m: m.group(1).translate(subscripts), text)
    
    # 3. Strip out the raw math dollar signs entirely
    text = text.replace("$$", "").replace("$", "")
    return text

# 👑 DAKASH ENGINE - HYBRID AI MENTOR CONFIGURATION (GEMINI EDITION)
# Try both env sources (Vercel sets them directly without .env)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# System Instruction: Casual, friendly, and human-like tutor
SYSTEM_PROMPT = """
You are the 'Samarth AI Mentor', a friendly, encouraging, and natural human-like tutor.
Your goal is to explain educational concepts to students in a highly conversational, simple, and direct manner—exactly like a helpful human peer would write.
- Tone: Casual, warm, friendly, and natural. Do NOT sound robotic, textbook-like, or overly formal.
- Language: Plain, conversational English.
- Format: Keep formatting clean and minimal. Use short paragraphs and simple lists. Avoid heavy markdown decoration, forced headers (like 'Method 1:', 'Step-by-Step Example:', 'Why does this work?'), and excessive emojis.
- Explanations: Explain concepts in the simplest terms first. Use quick, realistic examples.
- Value Add: Integrate tips and tricks smoothly into the conversation without making it look like a rigid textbook layout.
"""

def get_ai_response(user_input):
    try:
        # User inquiries intercept for creator/father/maker in English, Hindi, Hinglish
        input_clean = user_input.strip().lower()
        creator_patterns = [
            r"\b(who|tumhe|tumhaara|tumhara|aapko)\b.*\b(made|created|built|developed|designed|wrote|father|papa|creator|developer|maker|owner|bhagwan|maker|banaya|create kiya|develop kiya|banaya hai|baap|pita|janmadata)\b",
            r"\b(creator|developer|father|papa|baap|pita|maker)\b.*\b(you|tum|aap)\b",
            r"\b(who is|who's|kaun hai|kon hai|kisne)\b.*\b(your father|your creator|your developer|your papa|your maker|you|tumhe|aapko)\b.*\b(father|creator|developer|papa|maker|banaya)\b",
            r"\b(kisne banaya|kaun hai creator|kaun hai developer|tumhara baap kaun|tumhara papa kaun|aapke papa|aapke pita|aapka baap)\b"
        ]
        
        is_creator_query = False
        for pattern in creator_patterns:
            if re.search(pattern, input_clean):
                is_creator_query = True
                break
                
        # Handle specifically simple single-word checks as fallbacks
        if not is_creator_query:
            single_words = ["creator", "developer", "janmadata", "founder"]
            if any(w in input_clean for w in single_words) and any(u in input_clean for u in ["you", "tum", "aap", "ur"]):
                is_creator_query = True
            elif "tumhara papa" in input_clean or "tumhaara papa" in input_clean or "aapke papa" in input_clean or "tumhara baap" in input_clean:
                is_creator_query = True
            elif "who made you" in input_clean or "who created you" in input_clean or "who built you" in input_clean or "kisne banaya" in input_clean:
                is_creator_query = True

        if is_creator_query:
            return "Mujhe **DAKASH** ne banaya hai! 👑🔥"

        # Check if API Key exists
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")

        # 🔄 SESSION MEMORY
        if 'chat_history' not in session:
            # Initialize with system message using Gemini roles
            session['chat_history'] = []

        # Construct chat history in Gemini format
        gemini_history = []
        for msg in session['chat_history']:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({
                "role": role,
                "parts": [msg["content"]]
            })

        # Initialize the model with system instruction
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT
        )
        
        # Start a chat session with the historical messages
        chat = model.start_chat(history=gemini_history)
        
        # Send message
        response = chat.send_message(user_input)
        response_text = response.text
        
        # Clean chemistry text (e.g. chemical subscripts and arrows)
        response_text = clean_chemistry_text(response_text)

        # Update session history in our standardized format
        session['chat_history'].append({"role": "user", "content": user_input})
        session['chat_history'].append({"role": "assistant", "content": response_text})

        # 🧹 BUFFER CONTROL
        if len(session['chat_history']) > 10:
            session['chat_history'] = session['chat_history'][-10:]

        session.modified = True 
        return response_text

    except Exception as e:
        # Error logging for PC debugging
        logging.error(f">> [DAKASH-AI-ERROR]: {e}")
        
        # Rule-based fallback
        user_input_lower = user_input.lower()
        if any(greet in user_input_lower for greet in ["hello", "hi", "hey", "namaste"]):
            return "Hello! I am your Samarth AI Mentor. My live connection is currently offline, but my backup system is active. How can I help you with your studies today? 🚀"
        elif any(exam in user_input_lower for exam in ["exam", "test", "nda", "jee", "board"]):
            return "For exams, keep your strategy simple: solve Previous Year Questions (PYQs), manage your study time effectively, and take mock tests regularly to assess your progress. ⚡"
        elif any(sch in user_input_lower for sch in ["timetable", "schedule", "plan"]):
            return "To organize your study day, head over to the Strategy Scheduler page and generate a customized study timetable. 📅"
        elif any(tgt in user_input_lower for tgt in ["goal", "target", "mission"]):
            return "Setting clear goals is key. Break down larger subjects into smaller milestones and track them daily. You will reach your target score in no time! 🎯"
        else:
            return "Keep learning and moving forward! If you want to connect my live system, please verify that your GEMINI_API_KEY is correctly set in your .env file. 🛡️"

def clear_chat_session():
    """Mission reset ke liye"""
    session.pop('chat_history', None)
    session.modified = True