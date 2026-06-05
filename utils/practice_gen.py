import os
import json
import re
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from flask import session

# .env se keys load karo
load_dotenv()

# 👑 DAKASH ENGINE - HYBRID GENERATIVE AI CONFIG (GEMINI UPGRADE)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def clean_response_text(text: str) -> str:
    text = text.replace(r"\rightarrow", "→")
    subscripts = str.maketrans("0123456789aeiou", "₀₁₂₃₄₅₆₇₈₉ₐₑᵢₒᵤ")
    text = re.sub(r'_([0-9a-euieo])', lambda m: m.group(1).translate(subscripts), text)
    text = text.replace("$$", "").replace("$", "")
    return re.sub(r' +', ' ', text)

def generate_practice_paper(data):
    """
    Dakash Engine: Custom AI Question Generator for Class 6-12 using Gemini.
    - Easy: NCERT Fundamentals
    - Moderate: Board PYQs (CBSE/ICSE)
    - Hard: Competitive (JEE/NEET/NDA/CUET)
    """
    
    # 🎯 Level & Source Calibration (Class-wise)
    target_class = data.get('class_level', '10') # Default 10th agar missing ho
    
    if data['difficulty'] == "Easy":
        source_logic = f"Strictly NCERT Textbook questions and basic concepts for Class {target_class}."
    elif data['difficulty'] == "Moderate":
        source_logic = f"Previous Year Questions (PYQs) from CBSE/ICSE Board Exams relevant to Class {target_class}."
    else:
        # Hard level for higher classes focus on entrance, for lower classes focus on Olympiads
        if int(target_class) >= 11:
            source_logic = f"Competitive Exam level (JEE Main, NEET, NDA, CUET) complexity for Class {target_class}."
        else:
            source_logic = f"Olympiad and Advanced Foundation level questions for Class {target_class}."

    # 🛠️ Constructing the Neural Prompt
    prompt = f"""
    Create an elite practice paper for a Class {target_class} student:
    - Subject: {data['subject']} | Chapter: {data['chapter']}
    - Difficulty: {data['difficulty']}
    - Logic: {source_logic}
    - Total Questions: Exactly 10 MCQs.
    
    ARCHITECTURE RULES:
    1. Language: All text (questions, options, explanation, and complement) MUST be in clear, standard English. Keep explanations concise and clear.
    2. Tags: At the very bottom right/end of the question text block, strictly include the meta source tag in plain text, e.g., '[Source: JEE Main 2022]' or '[Source: NCERT]' or '[Source: CBSE 2020]'.
    3. JSON Only: Return ONLY a raw JSON array.
    4. Do NOT wrap it in a parent key like "questions". Return the JSON array directly as the root element.

    COMPLIMENT LOGIC:
    - If user gets it right: Encouraging praise like 'Excellent job!', 'Great understanding!', 'Perfect score!'.
    - If user gets it wrong: Encouraging feedback like 'No problem, every mistake is a learning opportunity.', 'Review the concept and try again!', 'Keep practicing, you are getting better!'.

    JSON STRUCTURE:
    [
      {{
        "id": 1,
        "question": "Question text (Source Tag)",
        "options": ["A", "B", "C", "D"],
        "answer": "Exact Correct Option (matching one of the options)",
        "explanation": "Simple English breakdown of the concept...",
        "complement": "Dynamic compliment/encouraging feedback based on performance logic"
      }}
    ]
    """

    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")

        # Configure Gemini JSON Mode
        model = genai.GenerativeModel('gemini-flash-lite-latest')
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        if not response or not response.text:
            logging.error("JSON response from Gemini was empty.")
            return get_mock_practice_questions(data['subject'], target_class)

        raw_output = response.text.strip()
        
        # 🧪 Robust JSON Extraction
        json_match = re.search(r'\[.*\]', raw_output, re.DOTALL)
        
        if json_match:
            questions = json.loads(json_match.group())
            
            # Clean LaTeX symbols and chemical subscripts in generated questions
            for q in questions:
                if 'question' in q: q['question'] = clean_response_text(q['question'])
                if 'explanation' in q: q['explanation'] = clean_response_text(q['explanation'])
                if 'complement' in q: q['complement'] = clean_response_text(q['complement'])
                if 'options' in q and isinstance(q['options'], list):
                    q['options'] = [clean_response_text(opt) for opt in q['options']]
            
            if 'user_id' in session:
                print(f">> [DAKASH LOG]: Cadet {session['user_id']} (Class {target_class}) is on a mission.")
            
            print(f">> [DAKASH LOG]: {len(questions)} Class {target_class} Qs Generated (Level: {data['difficulty']}).")
            return questions
        else:
            logging.error("JSON Structure not found in Gemini response.")
            return get_mock_practice_questions(data['subject'], target_class)

    except Exception as e:
        logging.error(f"Dakash Engine Critical Error: {str(e)}")
        return get_mock_practice_questions(data['subject'], target_class)

def get_mock_practice_questions(subject, target_class):
    """Fallback practice questions when API fails"""
    return [
        {
            "id": 1,
            "question": f"Which of the following describes the key principle of {subject} in Class {target_class}? (NCERT)",
            "options": ["Principle Alpha", "Principle Beta", "Principle Gamma", "Principle Delta"],
            "answer": "Principle Alpha",
            "explanation": "Baseline logic states Principle Alpha is the prime controller.",
            "complement": "Toofani speed! Divine Rank Material!"
        },
        {
            "id": 2,
            "question": f"What is the main objective of learning {subject}? (BOARD PYQ)",
            "options": ["Analyze facts", "Rote learning", "Get marks only", "None of these"],
            "answer": "Analyze facts",
            "explanation": "Critical thinking triggers the ability to analyze and apply facts.",
            "complement": "Shabaash Cadet! Keep it up!"
        },
        {
            "id": 3,
            "question": f"Select the true statement regarding {subject}. (NDA/JEE/NEET)",
            "options": ["It is completely logical", "It has no structure", "It is purely theoretical", "None of the above"],
            "answer": "It is completely logical",
            "explanation": "All modules under CBSE classes are built with structured logical systems.",
            "complement": "Koi baat nahi Cadet, next time bilkul sahi hoga!"
        }
    ]

# 🔐 LOGIN-REGISTER LINKING UTILITY
def sync_with_user_profile(user_id, performance_data):
    """
    Cadet ki performance ko database mein save karne ke liye.
    """
    pass