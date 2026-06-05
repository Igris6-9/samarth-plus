import os
import numpy as np
from sklearn.linear_model import LinearRegression
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# .env se keys load karo
load_dotenv()

# 👑 DAKASH ML-ENGINE: HYBRID PREDICTIVE ANALYTICS (GEMINI UPGRADE)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class DakashPredictor:
    def __init__(self):
        # Neural Model initialization (Math core)
        self.model = LinearRegression()

    def get_ai_analysis(self, score, slope, weak_subjects):
        """
        Gemini AI se personalized strategic feedback lena.
        """
        prompt = f"""
        Analyze this Cadet's performance:
        - Predicted Board Score: {score}%
        - Growth Trend (Slope): {slope}
        - Weak Sectors: {', '.join(weak_subjects) if weak_subjects else 'None'}
        
        Write a 2-line strategic advice in clear, plain English. 
        Tone: Professional, supportive, and encouraging. 
        Avoid military jargon. Refer to the user as a student.
        """
        try:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not set")
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
        except:
            return "Neural Link unstable, par Cadet tu rukk mat. Practice jaari rakh! 🛡️"

    def predict_boards_score(self, quiz_history, subject_data=None):
        """
        Cadet ki purani history se Boards ka result forecast karna + AI Insights.
        """
        if not quiz_history or len(quiz_history) < 3:
            return None, "Cadet, neural data kam hai. Kam se kam 3 tests attempt karo! 🛡️"

        try:
            # 1. Math Processing (Trend Analysis)
            X = np.array(range(len(quiz_history))).reshape(-1, 1)
            y = np.array([float(q['score']) for q in quiz_history])

            self.model.fit(X, y)
            future_test_index = len(quiz_history) + 5
            prediction = self.model.predict([[future_test_index]])[0]
            final_pred = float(np.clip(prediction, 0, 100))
            slope = float(self.model.coef_[0])

            # 2. Subject Scan for AI
            weak_sectors = []
            if subject_data:
                weak_sectors = [s for s, sc in subject_data.items() if sc < 50]

            # 3. Get Strategic AI Feedback via Gemini
            ai_msg = self.get_ai_analysis(round(final_pred, 1), round(slope, 2), weak_sectors)

            return round(final_pred, 1), ai_msg

        except Exception as e:
            logging.error(f">> [ML-ENGINE ERROR]: {e}")
            return None, "Prediction failed. Neural links unstable. 🛰️"

    def analyze_subject_dominance(self, subject_data):
        """
        Subject wise strength scan.
        """
        weak_sectors = [s for s, sc in subject_data.items() if sc < 50]
        strong_sectors = [s for s, sc in subject_data.items() if sc >= 85]
        
        return {
            "critical": weak_sectors,
            "elite": strong_sectors
        }
