import os
import json
import re
import logging

# ✅ NEW SDK
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-1.5-flash"

def _get_client():
    """Lazily get Gemini client for Vercel compatibility."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=api_key)

def generate_ai_timetable(user_data):
    """Dakash Engine: Generates an AI-optimized schedule using Gemini."""

    prompt = f"""
    Act as the Samarth AI Mentor. Create an elite 1-day combat schedule (timetable).

    CONSTRAINTS:
    - Wake up: {user_data['wake_up']}
    - School: {user_data['school_start']} to {user_data['school_end']}
    - Coaching: {user_data['has_coaching']} ({user_data.get('coaching_time', 'N/A')})
    - Special Objective: {user_data['special_task']}

    STRATEGIC RULES:
    1. Deep Work: Allocate 90-min uninterrupted slots for tough subjects.
    2. Buffer: Add 15-min 'Recovery Phases' after intense sessions.
    3. English: Details must be in encouraging, clear English.
    4. Output: Return ONLY a raw JSON array. No extra text.

    JSON STRUCTURE:
    [
      {{
        "time": "06:00 AM",
        "task": "MORNING DRILL",
        "detail": "High-energy start! 15 min exercise + formula revision.",
        "type": "Deep Work / Recovery / Buffer"
      }}
    ]
    """

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        if not response or not response.text:
            logging.error(">> [ERROR]: Gemini Scheduler core returned null.")
            return get_fallback_schedule(user_data)

        raw_text = response.text.strip()
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)

        if json_match:
            schedule = json.loads(json_match.group())
            print(f">> [SCHEDULER]: AI Combat Plan generated with {len(schedule)} slots.")
            return schedule
        else:
            data = json.loads(raw_text)
            if isinstance(data, dict):
                for val in data.values():
                    if isinstance(val, list):
                        return val
            return get_fallback_schedule(user_data)

    except Exception as e:
        logging.error(f"Scheduler Engine Error: {str(e)}")
        return get_fallback_schedule(user_data)

def get_fallback_schedule(user_data):
    """Fallback preset schedule when API fails."""
    wake_time = user_data.get('wake_up', '06:00 AM')
    special = user_data.get('special_task', 'Formula Revision')
    return [
        {"time": wake_time, "task": "MORNING DRILL", "detail": f"Wake up! Start with revision of '{special}'. ⚡", "type": "Recovery"},
        {"time": "08:00 AM", "task": "SCHOOL / FOCUS CORE", "detail": "Absorb core concepts during lectures. Be attentive! 🏫", "type": "Deep Work"},
        {"time": "03:00 PM", "task": "TACTICAL RECOVERY", "detail": "Lunch + refresh your neural cells. Rest is essential. 🍎", "type": "Recovery"},
        {"time": "04:30 PM", "task": "DEEP WORK BLOCK", "detail": "Deep focus on weak topics. Complete numericals. 📖", "type": "Deep Work"},
        {"time": "08:00 PM", "task": "QUIZ/SIMULATION RUN", "detail": "Execute a Practice Mission or Mock Quiz on Samarth. 🏆", "type": "Deep Work"},
        {"time": "10:00 PM", "task": "HIBERNATION", "detail": "Sleep for neural optimization and memory consolidation. 😴", "type": "Recovery"}
    ]

def get_current_task(schedule):
    """Mobile Dashboard ke liye: Abhi kya karna hai."""
    pass
