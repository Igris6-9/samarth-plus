import os
import re
import logging
from flask import session, current_app

# ✅ NEW SDK - google.genai (replaces deprecated google.generativeai)
from google import genai
from google.genai import types

# System Instruction: Casual, friendly, and human-like tutor
SYSTEM_PROMPT = """
You are the 'Samarth AI Mentor', a friendly, encouraging, and natural human-like tutor.
Your goal is to explain educational concepts to students in a highly conversational, simple, and direct manner—exactly like a helpful human peer would write.
- Tone: Casual, warm, friendly, and natural. Do NOT sound robotic, textbook-like, or overly formal.
- Language: Plain, conversational English.
- Format: Keep formatting clean and minimal. Use short paragraphs and simple lists. Avoid heavy markdown decoration, forced headers, and excessive emojis.
- Explanations: Explain concepts in the simplest terms first. Use quick, realistic examples.
- Value Add: Integrate tips and tricks smoothly into the conversation without making it look like a rigid textbook layout.
"""

GEMINI_MODEL = "gemini-1.5-flash"

def _get_client():
    """Lazily get Gemini client — reads API key fresh every call for Vercel compatibility."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")
    return genai.Client(api_key=api_key)

def clean_chemistry_text(text: str) -> str:
    """Clean LaTeX and chemical notation from AI responses."""
    text = text.replace(r"\rightarrow", "→")
    subscripts = str.maketrans("0123456789aeiou", "₀₁₂₃₄₅₆₇₈₉ₐₑᵢₒᵤ")
    text = re.sub(r'_([0-9a-euieo])', lambda m: m.group(1).translate(subscripts), text)
    text = text.replace("$$", "").replace("$", "")
    return text

def get_ai_response(user_input):
    try:
        # ── Creator/Father intercept (English, Hindi, Hinglish) ──
        input_clean = user_input.strip().lower()
        creator_patterns = [
            r"\b(who|tumhe|tumhaara|tumhara|aapko)\b.*\b(made|created|built|developed|designed|wrote|father|papa|creator|developer|maker|owner|banaya|create kiya|develop kiya|baap|pita|janmadata)\b",
            r"\b(creator|developer|father|papa|baap|pita|maker)\b.*\b(you|tum|aap)\b",
            r"\b(who is|who's|kaun hai|kon hai|kisne)\b.*\b(your father|your creator|your developer|your papa|your maker)\b",
            r"\b(kisne banaya|kaun hai creator|kaun hai developer|tumhara baap kaun|tumhara papa kaun|aapke papa|aapke pita|aapka baap)\b"
        ]
        is_creator_query = any(re.search(p, input_clean) for p in creator_patterns)
        if not is_creator_query:
            if any(w in input_clean for w in ["creator", "developer", "janmadata", "founder"]) and \
               any(u in input_clean for u in ["you", "tum", "aap", "ur"]):
                is_creator_query = True
            elif any(p in input_clean for p in ["tumhara papa", "tumhaara papa", "aapke papa",
                                                  "tumhara baap", "who made you", "who created you",
                                                  "who built you", "kisne banaya"]):
                is_creator_query = True

        if is_creator_query:
            return "Mujhe **DAKASH** ne banaya hai! 👑🔥"

        # ── Get fresh client (lazy init for Vercel) ──
        client = _get_client()

        # ── Build conversation history ──
        if 'chat_history' not in session:
            session['chat_history'] = []

        # Build contents list with system prompt prepended
        contents = [types.Content(
            role="user",
            parts=[types.Part(text=SYSTEM_PROMPT + "\n\nNow answer the user's messages below.")]
        ), types.Content(
            role="model",
            parts=[types.Part(text="Understood! I'm your Samarth AI Mentor. Let's go! 🚀")]
        )]

        for msg in session['chat_history']:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])]
            ))

        # Add current user message
        contents.append(types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        ))

        # ── Call Gemini ──
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents
        )

        response_text = response.text
        response_text = clean_chemistry_text(response_text)

        # Update session history
        session['chat_history'].append({"role": "user", "content": user_input})
        session['chat_history'].append({"role": "assistant", "content": response_text})

        # Keep history to last 10 messages
        if len(session['chat_history']) > 10:
            session['chat_history'] = session['chat_history'][-10:]

        session.modified = True
        return response_text

    except Exception as e:
        logging.error(f">> [DAKASH-AI-ERROR]: {e}")

        # Rule-based fallback
        input_lower = user_input.lower()
        if any(g in input_lower for g in ["hello", "hi", "hey", "namaste"]):
            return "Hello! I am your Samarth AI Mentor. My live connection is currently offline, but my backup system is active. How can I help you with your studies today? 🚀"
        elif any(e in input_lower for e in ["exam", "test", "nda", "jee", "board"]):
            return "For exams, keep your strategy simple: solve PYQs, manage your time, and take mock tests regularly. ⚡"
        elif any(s in input_lower for s in ["timetable", "schedule", "plan"]):
            return "Head over to the Strategy Scheduler page to generate a customized study timetable. 📅"
        elif any(g in input_lower for g in ["goal", "target", "mission"]):
            return "Setting clear goals is key. Break subjects into smaller milestones and track them daily. 🎯"
        else:
            return "Keep learning and moving forward! There seems to be a temporary issue with the AI connection. Please try again in a moment. 🛡️"

def clear_chat_session():
    """Mission reset."""
    session.pop('chat_history', None)
    session.modified = True