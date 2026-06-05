import os
import json
import re
import logging

# ✅ NEW SDK - google.genai (replaces deprecated google.generativeai)
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment keys
load_dotenv()

# ✅ Correct model name
GEMINI_MODEL = "gemini-1.5-flash"

def _get_client():
    """Lazily get Gemini client — reads API key fresh every call for Vercel compatibility."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")
    return genai.Client(api_key=api_key)

def clean_response_text(text: str) -> str:
    # Removes raw math dollar signs and handles technical symbols
    text = text.replace(r"\rightarrow", "→")
    subscripts = str.maketrans("0123456789aeiou", "₀₁₂₃₄₅₆₇₈₉ₐₑᵢₒᵤ")
    text = re.sub(r'_([0-9a-euieo])', lambda m: m.group(1).translate(subscripts), text)
    text = text.replace("$$", "").replace("$", "")
    return re.sub(r' +', ' ', text)

# ==========================================
# 2. MASTER CBSE CLASS 9 BLUEPRINTS DATABASE
# ==========================================
CBSE_CLASS_9_BLUEPRINTS = {
    "Mathematics": {
        "total_marks": 80,
        "total_questions": 38,
        "structure": (
            "- Section A: 20 Objective Questions (18 standard MCQs + 2 Assertion-Reason) [1 Mark each] (Total: 20)\n"
            "- Section B: 5 Very Short Answer questions [2 Marks each] (Total: 10)\n"
            "- Section C: 6 Short Answer questions [3 Marks each] (Total: 18)\n"
            "- Section D: 4 Long Answer Type questions [5 Marks each] (Total: 20)\n"
            "- Section E: 3 Integrated Case-Based/Source-Based questions [4 Marks each] *Sub-parts divided into 1, 1, and 2 marks keys* (Total: 12)"
        )
    },
    "Science": {
        "total_marks": 70,  # Critical Class 9 Specification (30 Marks Internal)
        "total_questions": 33,
        "structure": (
            "- Section A: 16 Objective Questions (MCQs, fill-in-the-blanks, Assertion-Reason) [1 Mark each] (Total: 16)\n"
            "- Section B: 5 Very Short Answer questions [2 Marks each] *Strictly 30 to 50 words* (Total: 10)\n"
            "- Section C: 7 Short Answer questions [3 Marks each] *Strictly 50 to 80 words* (Total: 21)\n"
            "- Section D: 2 Integrated Case-Based/Source-Based conceptual sets [4 Marks each] (Total: 8)\n"
            "- Section E: 3 Long Answer questions spanning Physics, Chemistry, and Biology [5 Marks each] *Strictly 80 to 120 words* (Total: 15)"
        )
    },
    "Social Science": {
        "total_marks": 80,
        "total_questions": 37,
        "structure": (
            "- Section A: 20 Objective Questions (MCQs, matching items, and picture-based tasks) [1 Mark each] (Total: 20)\n"
            "- Section B: 4 Very Short Answer questions [2 Marks each] *Strictly ~40 words* (Total: 8)\n"
            "- Section C: 5 Short Answer questions [3 Marks each] *Strictly ~60 words* (Total: 15)\n"
            "- Section D: 4 Long Answer questions [5 Marks each] *Strictly ~120 words* (Total: 20)\n"
            "- Section E: 3 Integrated Case-Based/Source-Based passages [4 Marks each] (Total: 12)\n"
            "- Section F (Map Skills): 1 Unified Map Question split into:\n"
            "  * Part 1 (History - French/Russian Revolution identification): [2 Marks]\n"
            "  * Part 2 (Geography - Mountains, rivers, capitals locating & labeling): [3 Marks]"
        )
    },
    "English Core": {
        "total_marks": 80,
        "total_questions": 11,
        "structure": (
            "- Section A (Reading Skills - 20 Marks):\n"
            "  * Q1: 1 Unseen Discursive passage [10 Marks]\n"
            "  * Q2: 1 Unseen Case-Based factual passage with static statistical charts/graphs [10 Marks]\n"
            "- Section B (Writing Skills & Grammar - 20 Marks):\n"
            "  * Grammar: 10 items out of 12 (gap-filling, editing, sentence transformations on tenses, modals, determiners, concord, reported speech) [10 Marks]\n"
            "  * Creative Writing: Q3: 1 Descriptive Paragraph from visual/verbal cues [5 Marks] + Q4: 1 Formal Diary Entry OR Story Writing from outline [5 Marks]\n"
            "- Section C (Language through Literature - 40 Marks testing Beehive & Moments):\n"
            "  * Reference to Context: 1 Prose Extract [5 Marks] + 1 Poetry Extract [5 Marks] (Total: 10)\n"
            "  * Short Answers (40-50 words): 4 questions from Beehive [12 Marks] + 2 questions from Moments [6 Marks] (Total: 18)\n"
            "  * Long Answers (100-120 words): 1 analysis/character sketch from Beehive [6 Marks] + 1 evaluation plot from Moments [6 Marks] (Total: 12)"
        )
    }
}

# ==========================================
# 3. MASTER CBSE CLASS 10 BLUEPRINTS DATABASE
# ==========================================
CBSE_CLASS_10_BLUEPRINTS = {
    "Mathematics": {
        "total_marks": 80,
        "total_questions": 38,
        "structure": (
            "- Section A: 20 Objective Questions (18 standard MCQs + 2 Assertion-Reason) [1 Mark each] (Total: 20)\n"
            "- Section B: 5 Very Short Answer Type-I questions [2 Marks each] (Total: 10)\n"
            "- Section C: 6 Short Answer Type-II questions [3 Marks each] (Total: 18)\n"
            "- Section D: 4 Long Answer Type questions [5 Marks each] (Total: 20)\n"
            "- Section E: 3 Integrated Case-Based/Source-Based questions [4 Marks each] (Total: 12)"
        )
    },
    "Science": {
        "total_marks": 80,
        "total_questions": 39,
        "structure": (
            "- Section A: 20 Objective Type Questions (16 MCQs + 4 Assertion-Reason) [1 Mark each] (Total: 20)\n"
            "- Section B: 6 Very Short Answer questions [2 Marks each] *Strictly 30 to 50 words* (Total: 12)\n"
            "- Section C: 7 Short Answer questions [3 Marks each] *Strictly 50 to 80 words* (Total: 21)\n"
            "- Section D: 3 Long Answer questions [5 Marks each] *Strictly 80 to 120 words* (Total: 15)\n"
            "- Section E: 3 Case-Based / Data-Interpretation integrated units [4 Marks each] (Total: 12)"
        )
    },
    "Social Science": {
        "total_marks": 80,
        "total_questions": 37,
        "structure": (
            "- Section A: 20 MCQs [1 Mark each] (Total: 20)\n"
            "- Section B: 4 Very Short Answer questions [2 Marks each] (Total: 8)\n"
            "- Section C: 5 Short Answer questions [3 Marks each] (Total: 15)\n"
            "- Section D: 4 Long Answer questions [5 Marks each] (Total: 20)\n"
            "- Section E: 3 Case-Based / Source-Based integrated questions [4 Marks each] (Total: 12)\n"
            "- Section F (Map Skills): 1 Integrated Map Question split into:\n"
            "  * Part 1 (History Identification): [2 Marks]\n"
            "  * Part 2 (Geography Locating & Labeling): [3 Marks]"
        )
    },
    "English Core": {
        "total_marks": 80,
        "total_questions": "Section-wise Continuous",
        "structure": (
            "- Section A (Reading Skills - 20 Marks):\n"
            "  * 1 Discursive unseen passage [10 Marks]\n"
            "  * 1 Case-Based factual passage with visual/statistical inputs like charts/data graphs [10 Marks]\n"
            "- Section B (Grammar & Creative Writing - 20 Marks):\n"
            "  * Grammar: 10 items testing tenses, modals, subject-verb concord, reported speech [10 Marks]\n"
            "  * Creative Writing: 1 Situation-based Formal Letter [5 Marks] + 1 Analytical Paragraph using map/graph/chart cues [5 Marks]\n"
            "- Section C (Language through Literature - 40 Marks):\n"
            "  * 2 Reference to Context extracts (1 Drama/Prose + 1 Poetry) [10 Marks total]\n"
            "  * Short Answers: 4 questions from First Flight [12 Marks] + 2 from Footprints Without Feet [6 Marks]\n"
            "  * Long Answers: 1 critical question from First Flight [6 Marks] + 1 from Footprints Without Feet [6 Marks]"
        )
    }
}

# ==========================================
# 4. CBSE CLASS 11 & 12 MASTER BLUEPRINTS
# ==========================================
CBSE_CLASS_11_12_BLUEPRINTS = {
    "Mathematics": {
        "total_marks": 80,
        "total_questions": 38,
        "structure": (
            "- Section A: 18 MCQs + 2 Assertion-Reason questions [1 Mark each] (Total: 20)\n"
            "- Section B (Very Short Answer): 5 questions [2 Marks each] (Total: 10) *Include internal choices in 2 questions*\n"
            "- Section C (Short Answer): 6 questions [3 Marks each] (Total: 18) *Include internal choices in 3 questions*\n"
            "- Section D (Long Answer): 4 questions [5 Marks each] (Total: 20) *Include internal choices in 2 questions*\n"
            "- Section E (Case Study): 3 integrated case-based questions [4 Marks each] (Total: 12) *Include internal choices in sub-parts*"
        )
    },
    "Physics": {
        "total_marks": 70,
        "total_questions": 33,
        "structure": (
            "- Section A: 16 MCQs (analytical, data-driven, & Assertion-Reason types) [1 Mark each] (Total: 16)\n"
            "- Section B (Very Short Answer): 5 questions [2 Marks each] (Total: 10)\n"
            "- Section C (Short Answer): 7 questions [3 Marks each] (Total: 21)\n"
            "- Section D (Case-Based): 2 integrated, source/case-based problem sets [4 Marks each] (Total: 8)\n"
            "- Section E (Long Answer): 3 comprehensive analytical questions [5 Marks each] (Total: 15)"
        )
    },
    "Accountancy": {
        "total_marks": 80,
        "total_questions": 34,
        "structure": (
            "Divided into Part A and Part B:\n"
            "- Objective Questions: 20 MCQs [1 Mark each] (Total: 20)\n"
            "- Short Answer Type: 6 questions [3 Marks each] (Total: 18)\n"
            "- Long Answer Type I: 3 questions [4 Marks each] (Total: 12)\n"
            "- Long Answer Type II: 5 comprehensive numerical/application questions [6 Marks each] (Total: 30)"
        )
    },
    "Business Studies": {
        "total_marks": 80,
        "total_questions": 34,
        "structure": (
            "- Objective Type: 20 MCQs [1 Mark each] (Total: 20)\n"
            "- Short Answer Type I: 4 questions [3 Marks each] (Total: 12)\n"
            "- Short Answer Type II: 6 questions [4 Marks each] (Total: 24)\n"
            "- Long Answer Type: 4 situational/theoretical questions [6 Marks each] (Total: 24)"
        )
    },
    "English Core": {
        "total_marks": 80,
        "total_questions": "Section-wise Continuous",
        "structure": (
            "- Section A (Reading Skills - 26 Marks):\n"
            "  * 1 Factual/Literary passage [10 Marks]\n"
            "  * 1 Case-Based passage with visual/static inputs charts [8 Marks]\n"
            "  * 1 Unseen passage for Note Making & Summarization [8 Marks]\n"
            "- Section B (Grammar & Creative Writing - 23 Marks):\n"
            "  * Grammar tasks (gap-filling/sentence reordering) [7 Marks total]\n"
            "  * Short Composition (Notice/Invitation: 3 Marks + Poster/Ad: 3 Marks) [6 Marks total]\n"
            "  * Long Composition (Letter: 5 Marks + Article/Report: 5 Marks) [10 Marks total]\n"
            "- Section C (Literature - 31 Marks):\n"
            "  * 3 Textbook reference extracts from Hornbill/Snapshots [10 Marks total]\n"
            "  * 3 Short Answer Questions [9 Marks total]\n"
            "  * 2 Long Answer critical-thinking questions [12 Marks total]"
        )
    }
}

# Mapping exact duplicate configurations
CBSE_CLASS_11_12_BLUEPRINTS["Chemistry"] = CBSE_CLASS_11_12_BLUEPRINTS["Physics"]
CBSE_CLASS_11_12_BLUEPRINTS["Biology"] = CBSE_CLASS_11_12_BLUEPRINTS["Physics"]
CBSE_CLASS_11_12_BLUEPRINTS["Economics"] = CBSE_CLASS_11_12_BLUEPRINTS["Business Studies"]

# ==========================================
# 5. MASTER COMPETITIVE BLUEPRINT DATABASE
# ==========================================
COMPETITIVE_BLUEPRINTS = {
    "JEE_Main": {
        "exam_name": "JEE Main (B.E./B.Tech)",
        "total_marks": 300,
        "total_questions": 75,
        "timer": "3 Hours (180 Minutes)",
        "marking_scheme": "Compulsory System: Correct (+4) | Incorrect (-1) | Unattempted (0)",
        "structure": "Generate 25 COMPULSORY questions for this subject:\n- Section A: 20 MCQs [Single Correct Option]\n- Section B: 5 Numerical Value Questions [Requires integer/decimal calculations]",
        "tag_pattern": "JEE Main Simulation"
    },
    "NEET_UG": {
        "exam_name": "NEET UG (Medical)",
        "total_marks": 720,
        "total_questions": 180,
        "timer": "3 Hours and 20 Minutes (200 Minutes)",
        "marking_scheme": "OMR Offline System: Correct (+4) | Incorrect (-1) | Skipped (0)",
        "structure": "Generate completely COMPULSORY Multiple Choice Questions (MCQs) only. No descriptive or numerical text inputs allowed.",
        "tag_pattern": "NEET UG Simulation"
    },
    "UPSC_NDA_Maths": {
        "exam_name": "UPSC NDA — Paper 1: Mathematics",
        "total_marks": 300,
        "total_questions": 120,
        "timer": "2.5 Hours (150 Minutes)",
        "marking_scheme": "NDA Maths Protocol: Correct (+2.5) | Incorrect (-0.83) | Unattempted (0)",
        "structure": "Generate 120 Compulsory MCQs focusing on core mathematical concepts standard to UPSC NDA.",
        "tag_pattern": "NDA Written Exam (Paper-1)"
    },
    "UPSC_NDA_GAT": {
        "exam_name": "UPSC NDA — Paper 2: General Ability Test (GAT)",
        "total_marks": 600,
        "total_questions": 150,
        "timer": "2.5 Hours (150 Minutes)",
        "marking_scheme": "NDA GAT Protocol: Correct (+4.0) | Incorrect (-1.33) | Unattempted (0)",
        "tag_pattern": "NDA Written Exam (Paper-2)"
    }
}

def generate_cbse_quiz(subject, difficulty, class_level="10", exam_track=None, chapter=None, solved_history=None):
    """
    Dakash Engine: Generates simulated pattern paper utilizing Gemini API.
    Supports Class 6 to 12 blueprints, JEE/NEET/NDA tracks, and question anti-duplication.
    """
    if solved_history is None:
        solved_history = []
    if not chapter:
        chapter = "General Syllabus"

    target_exam = None
    subject_instruction = f"Subject Target: {subject} | Chapter Focus: {chapter}"
    is_competitive = False

    # 1. Track Identification & Routing (Hard / Competitive vs standard CBSE)
    if "Hard" in difficulty or exam_track in ["JEE", "NEET", "NDA"]:
        is_competitive = True

        if exam_track == "JEE":
            target_exam = COMPETITIVE_BLUEPRINTS["JEE_Main"]
            
        elif exam_track == "NEET":
            target_exam = COMPETITIVE_BLUEPRINTS["NEET_UG"]
            if subject == "Biology":
                subject_instruction = "Generate 90 Compulsory MCQs (Split evenly into 45 Botany and 45 Zoology questions)."
                
        elif exam_track == "NDA":
            if any(math_term in subject.lower() for math_term in ["mathematics", "maths", "math"]):
                target_exam = COMPETITIVE_BLUEPRINTS["UPSC_NDA_Maths"]
            else:
                target_exam = COMPETITIVE_BLUEPRINTS["UPSC_NDA_GAT"].copy()
                gat_rules = {
                    "English": "Part A: English (50 Questions). Focus on Spotting errors, vocabulary, idioms/phrases.",
                    "Physics": "Part B: GK - Physics Section (~25 Questions).",
                    "History": "Part B: GK - History & Indian Freedom Movement (~20 Questions).",
                    "Geography": "Part B: GK - Geography Section (~20 Questions).",
                    "Chemistry": "Part B: GK - Chemistry Section (~15 Questions).",
                    "Current Affairs": "Part B: GK - Current Affairs & Defence Updates (~10 Questions)."
                }
                subject_instruction = gat_rules.get(subject, f"Part B GK Section for Subject: {subject}.")
                target_exam["structure"] = f"Generate 150 Compulsory MCQs based on UPSC standards. Active Focus: {subject_instruction}"

        # Setup standard template fields if not correctly resolved
        if not target_exam:
            target_exam = COMPETITIVE_BLUEPRINTS["JEE_Main"]

    else:
        # Load corresponding CBSE Class 9, Class 10 or Class 11/12 database
        if class_level == "9":
            blueprint_db = CBSE_CLASS_9_BLUEPRINTS
        elif class_level == "10":
            blueprint_db = CBSE_CLASS_10_BLUEPRINTS
        else:
            blueprint_db = CBSE_CLASS_11_12_BLUEPRINTS
        
        blueprint = None
        for key, bp in blueprint_db.items():
            if key.lower() in subject.lower():
                blueprint = bp
                break
                
        if not blueprint:
            blueprint = {
                "total_marks": 80,
                "total_questions": 10,
                "structure": (
                    "- Section A: Q1-4 (1M MCQs + Assertion-Reason)\n"
                    "- Section B: Q5-6 (2M Very Short Answer)\n"
                    "- Section C: Q7-8 (3M Short Answer)\n"
                    "- Section D: Q9 (5M Long Answer)\n"
                    "- Section E: Q10 (4M Case-Based)"
                )
            }

        # Set up source tag constraints based on the difficulty
        if "Easy" in difficulty:
            source_rule = f"Strict Rule: Use ONLY official standard NCERT Class {class_level} Textbook questions, internal textbook review questions, and exemplar problems."
            tag_format = f"[Source: NCERT Class {class_level} Textbook]"
        else:
            source_rule = f"Strict Rule: Use ONLY authentic, past-year official CBSE Class {class_level} Board Examination questions (PYQs)."
            tag_format = f"[Source: CBSE Class {class_level} Exam PYQ]" if class_level in ["10", "12"] else f"[Source: CBSE Class {class_level} Chapter PYQ]"

    # Dynamic target generation count logic based on selected blueprint sizes
    if is_competitive:
        if exam_track == "JEE":
            num_questions = 25
        elif exam_track == "NEET":
            num_questions = 90 if subject.lower() == "biology" else 45
        elif exam_track == "NDA":
            # Cap NDA math to 40 representative items to prevent token size cuts
            num_questions = 40 if any(m in subject.lower() for m in ["mathematics", "maths", "math"]) else 50
        else:
            num_questions = 25
    else:
        # Standard CBSE counts
        if any(m in subject.lower() for m in ["mathematics", "maths", "math"]):
            num_questions = 38
        elif any(s in subject.lower() for s in ["science", "physics", "chemistry", "biology"]):
            num_questions = 39 if class_level == "10" else 33
        elif any(ss in subject.lower() for ss in ["social science", "history", "geography"]):
            num_questions = 37
        elif any(act in subject.lower() for act in ["accountancy", "business studies", "economics"]):
            num_questions = 34
        else:
            num_questions = 15

    # 2. Prompts compilation
    if is_competitive:
        prompt = f"""
        You are the Lead Coordinator for National Competitive Test Deployments.
        Target Track Matrix: {target_exam['exam_name']} Core Engine.
        Academic Level Focus: Class {class_level} | Topic: {chapter}

        CRITICAL STRUCTURAL ARCHITECTURE:
        - Target Subject Scope: {subject_instruction}
        - Structure Setup: {target_exam.get('structure', 'Standard Pattern')}

        STRICT EVALUATION & TIMING SYSTEMS:
        - Absolute Session Timer: {target_exam['timer']}
        - Marking Penalty Matrix: {target_exam['marking_scheme']}
        - CRITICAL RULES: Options are completely removed. Every question is 100% compulsory.

        LIFETIME ANTI-DUPLICATION GUARDRAIL:
        Omit any matching identifier present in this history log array: {json.dumps(solved_history)}.

        DIGITAL ADAPTATION:
        - Provide exactly {num_questions} multiple choice questions (MCQs) for this simulator session, each with 4 options (A, B, C, D) and exactly 1 correct option.
        - English: Keep explanations extremely concise (maximum 1 sentence) to optimize speed.
        - Output MUST be a clean JSON array containing objects matching the format below.
        - Do NOT wrap it in a parent key like "questions". Return the JSON array directly as the root element.

        STRICT OUTPUT RENDERING PROTOCOL:
        1. Never display raw LaTeX syntax or math markdown tags ($ or $$).
        2. Every question block generated must contain its origin metadata stamp on the absolute bottom-right line using plain text pattern: '[Source: {target_exam['tag_pattern']} Actual PYQ]'.

        JSON FORMAT:
        [
            {{
                "section": "A",
                "q_num": 1,
                "q_id": "q_jee_9011",
                "marks": 4,
                "question": "Question text here [Source: {target_exam['tag_pattern']} Actual PYQ]",
                "options": ["Opt 1", "Opt 2", "Opt 3", "Opt 4"],
                "answer": "Correct Option (exactly matching one of the options)",
                "explanation": "Brief clear English logic explanation"
            }}
        ]
        """
    else:
        prompt = f"""
        You are the elite Chief Controller of School Examinations for CBSE Class {class_level}.
        Subject Track: {subject} | Core Chapter Focus: {chapter}
        Target Difficulty Mode: {difficulty}

        {source_rule}

        EXAMINATION BLUEPRINT CONSTRAINTS:
        - Total Target Weightage: {blueprint['total_marks']} Marks
        - Question Layout Strategy: Total {blueprint['total_questions']} questions broken down exactly as:
        {blueprint['structure']}

        COMPETENCY WEIGHTAGE PROTOCOL:
        - CRITICAL: Ensure exactly 50% of the total theory marks consist of Competency-Based questions (application-focused MCQs, integrated case studies, and source-based source passages).

        SESSION EVALUATION CONFIGURATIONS:
        - Dedicated Session Time: Strictly 3 Hours (180 Minutes).
        - Negative Marking Rules: Disabled (0 marks deducted for incorrect updates).

        LIFETIME ZERO REPETITION CONSTRAINT:
        Compare and eliminate any question match found in this structural identifier history array: {json.dumps(solved_history)}.

        DIGITAL ADAPTATION:
        - Provide exactly {num_questions} multiple choice questions (MCQs) for this simulator session, each with 4 options (A, B, C, D) and exactly 1 correct option.
        - English: Keep explanations extremely concise (maximum 1 sentence) to optimize speed.
        - Output MUST be a clean JSON array containing objects matching the format below.
        - Do NOT wrap it in a parent key like "questions". Return the JSON array directly as the root element.

        STRICT OUTPUT RENDERING PROTOCOL:
        1. Never output raw LaTeX or math dollar formatting blocks ($ or $$).
        2. Every individual question must contain its true origin stamp on the absolute bottom-right line using plain text layout (e.g., '{tag_format} / Verified Concept PYQ').

        JSON FORMAT:
        [
            {{
                "section": "A",
                "q_num": 1,
                "q_id": "q_cbse_1001",
                "marks": 1,
                "question": "Question text here {tag_format} / Verified Concept PYQ",
                "options": ["Opt 1", "Opt 2", "Opt 3", "Opt 4"],
                "answer": "Correct Option (exactly matching one of the options)",
                "explanation": "Brief clear English logic explanation"
            }}
        ]
        """

    try:
        # Get fresh client (lazy init for Vercel)
        client = _get_client()

        # Call Gemini with JSON response mode
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        if not response or not response.text:
            logging.error(">> [ERROR]: Gemini AI core returned null.")
            return get_mock_quiz_questions(subject, class_level)

        # Parse JSON
        raw_output = response.text.strip()
        
        try:
            quiz_data = json.loads(raw_output)
            
            # Handle cases where AI returns {"questions": [...]}
            if isinstance(quiz_data, dict):
                for key in quiz_data:
                    if isinstance(quiz_data[key], list):
                        quiz_data = quiz_data[key]
                        break
            
            if not isinstance(quiz_data, list):
                quiz_data = []

            # Clean LaTeX symbols and chemical subscripts in generated questions
            for q in quiz_data:
                if 'question' in q: q['question'] = clean_response_text(q['question'])
                if 'explanation' in q: q['explanation'] = clean_response_text(q['explanation'])
                if 'options' in q and isinstance(q['options'], list):
                    q['options'] = [clean_response_text(opt) for opt in q['options']]

            print(f">> [QUIZ ENGINE]: {len(quiz_data)} Qs Generated via Gemini.")
            return quiz_data if len(quiz_data) > 0 else get_mock_quiz_questions(subject, class_level)
            
        except json.JSONDecodeError:
            json_match = re.search(r'\[.*\]', raw_output, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                for q in parsed:
                    if 'question' in q: q['question'] = clean_response_text(q['question'])
                    if 'explanation' in q: q['explanation'] = clean_response_text(q['explanation'])
                    if 'options' in q and isinstance(q['options'], list):
                        q['options'] = [clean_response_text(opt) for opt in q['options']]
                return parsed
            logging.error(">> [ERROR]: Neural Link Truncated. JSON incomplete.")
            return get_mock_quiz_questions(subject, class_level)

    except Exception as e:
        logging.error(f"Quiz Gen Critical Error: {str(e)}")
        return get_mock_quiz_questions(subject, class_level)

def get_mock_quiz_questions(subject, class_level):
    """Fallback mock quiz generator when API fails"""
    return [
        {
            "section": "A",
            "q_num": 1,
            "q_id": "q_mock_001",
            "marks": 1,
            "question": f"Which of the following describes the fundamental component of {subject} in Class {class_level}? [Source: NCERT Class {class_level} Textbook]",
            "options": ["Basic Concept Alpha", "Core Theory Beta", "Applied Law Gamma", "None of the above"],
            "answer": "Basic Concept Alpha",
            "explanation": "Fundamental component starts with the baseline concept Alpha."
        },
        {
            "section": "A",
            "q_num": 2,
            "q_id": "q_mock_002",
            "marks": 1,
            "question": f"Assertion (A): Studying {subject} improves reasoning.\nReason (R): {subject} involves analytical principles. [Source: CBSE Class {class_level} Exam PYQ]",
            "options": ["Both A and R are true and R is correct explanation of A", "Both A and R are true but R is not correct explanation of A", "A is true but R is false", "A is false but R is true"],
            "answer": "Both A and R are true and R is correct explanation of A",
            "explanation": "Analytical study naturally boosts cognitive and logical skills, explaining Assertion A."
        },
        {
            "section": "B",
            "q_num": 3,
            "q_id": "q_mock_003",
            "marks": 2,
            "question": f"What is the primary formula used to calculate progress in {subject}? [Source: NCERT Class {class_level} Textbook]",
            "options": ["Efficiency = (Output / Input) * 100", "Efficiency = Input * Output", "Efficiency = Input - Output", "None of these"],
            "answer": "Efficiency = (Output / Input) * 100",
            "explanation": "Standard efficiency metric percentage formula."
        },
        {
            "section": "C",
            "q_num": 4,
            "q_id": "q_mock_004",
            "marks": 3,
            "question": f"Which parameter plays the most critical role in understanding advanced {subject} modules? [Source: CBSE Class {class_level} Exam PYQ]",
            "options": ["Consistency", "Memory power", "Syllabus depth", "External notes"],
            "answer": "Consistency",
            "explanation": "Regular practice makes learning persistent and builds strong neural links."
        },
        {
            "section": "E",
            "q_num": 5,
            "q_id": "q_mock_005",
            "marks": 4,
            "question": f"Case Study: A cadet studies {subject} daily for 2 hours. After 30 days, their mock scores increase from 50% to 92%.\nAnalyze their growth factor. [Source: CBSE Class {class_level} Exam PYQ]",
            "options": ["Linear growth", "Exponential consolidation", "Stagnant performance", "Negative trend"],
            "answer": "Exponential consolidation",
            "explanation": "Consistently learning causes compound interest in memory retention, leading to rapid consolidation."
        }
    ]

def get_section_info(section_name):
    """Dashboard UI ke liye section details"""
    info = {
        "A": "MCQs & Logic (Focus: Accuracy)",
        "B": "Core Concepts (Focus: Keywords)",
        "C": "Analytical (Focus: Diagrams)",
        "D": "Deep Knowledge (Focus: Structure)",
        "E": "Real-world Case (Focus: Application)"
    }
    return info.get(section_name, "General Section")