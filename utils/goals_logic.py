from datetime import datetime
from flask_login import current_user
import os
import logging

# ✅ NEW SDK
from google import genai

GEMINI_MODEL = "gemini-1.5-flash"

def _get_client():
    """Lazily get Gemini client for Vercel compatibility."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=api_key)

# 👑 DAKASH ENGINE - HYBRID GOAL ARCHITECTURE
class GoalManager:
    """Cadet ke missions aur targets ko manage karne wala real-time engine."""

    def __init__(self, db, GoalModel):
        self.db = db
        self.Goal = GoalModel

    def add_mission(self, title, category="Side Quest"):
        try:
            new_goal = self.Goal(
                user_id=current_user.id,
                title=title,
                category=category,
                status="ACTIVE",
                date_created=datetime.now()
            )
            self.db.session.add(new_goal)
            self.db.session.commit()
            print(f">> [MISSION LOG]: Target '{title}' synced to Database.")
            return True
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Goal Addition Error: {e}")
            return False

    def update_progress(self, goal_id):
        target = self.db.session.get(self.Goal, goal_id)
        if target and target.user_id == current_user.id:
            target.status = "ACCOMPLISHED"
            self.db.session.commit()
            return True
        return False

    def get_active_missions(self):
        return self.Goal.query.filter_by(
            user_id=current_user.id,
            status='ACTIVE'
        ).order_by(self.Goal.date_created.desc()).all()

    def get_stats(self):
        total = self.Goal.query.filter_by(user_id=current_user.id).count()
        done = self.Goal.query.filter_by(user_id=current_user.id, status='ACCOMPLISHED').count()
        rate = round((done / total) * 100) if total > 0 else 0
        return {"total": total, "done": done, "rate": rate}

# 🧠 AI NEURAL ANALYSIS
def analyze_goals_with_ai(goals_list, api_key):
    """Gemini se cadet ki trajectory analyze karwana."""
    if not goals_list:
        return "Abhi koi targets nahi hain, Cadet. Base taiyar karo! 🛡️"
    try:
        client = _get_client()
        prompt = f"""
        Analyze these student goals: {goals_list}
        1. Reality Check: Ek line mein batao realistic hain ya nahi.
        2. Strategic Tip: Har goal ke liye ek 'Pro Cadet' tip.
        3. Motivation: Power level (High/Low).
        Language: Hinglish. Tone: Commanding yet supportive.
        """
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text
    except Exception as e:
        logging.error(f"AI Analysis Error: {e}")
        return "Keep grinding, Cadet! Neural links temporary busy hain. 🛰️"
