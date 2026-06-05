from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import io
import re

# 🛸 DAKASH ENGINE CORE IMPORTS
load_dotenv()

from config import Config
from models import db, User, Score, Goal, Timetable
from utils.chatbot_logic import get_ai_response
from utils.graph_generator import generate_progress_graph
from utils.goals_logic import GoalManager, analyze_goals_with_ai
from utils.practice_gen import generate_practice_paper
from utils.timetable_gen import generate_ai_timetable

def create_app():
    # 🛸 Explicit static path for Vercel compatibility
    import os as _os
    _base = _os.path.abspath(_os.path.dirname(__file__))
    app = Flask(__name__,
                static_folder=_os.path.join(_base, 'static'),
                static_url_path='/static')
    app.config.from_object(Config)
    # Force Vercel to always serve fresh CSS/JS
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    # 🏗️ NEURAL DATABASE SYNC
    db.init_app(app)
    
    # Initialize GoalManager
    goal_manager = GoalManager(db, Goal)
    
    # 🛠️ LOGIN ARCHITECTURE
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # --- 🛰️ THE MASTER DIVINE ROUTING ENGINE ---

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        print(">> [SYSTEM]: Home Base accessed. Loading Divine Interface...")
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email_input = request.form.get('email')
            password_input = request.form.get('password')
            
            user = User.query.filter_by(email=email_input).first()
            
            if user and check_password_hash(user.password_hash, password_input):
                login_user(user, remember=True)
                session.permanent = True
                # Session fix for practice/quiz tracking
                session['user_id'] = user.id 
                session['username'] = user.username
                print(f">> [SYSTEM]: Cadet {user.username} is now ONLINE.")
                return redirect(url_for('dashboard'))
                
            flash('Invalid Credentials. Check your Neural Key!', 'danger')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            if User.query.filter_by(email=email).first():
                flash('Email already registered!', 'danger')
                return redirect(url_for('register'))

            new_user = User(
                username=username, 
                email=email, 
                password_hash=generate_password_hash(password)
            )
            
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Mission Ready! Account Created.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('Database Error!', 'danger')

        return render_template('register.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        user_scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.date_recorded.asc()).all()
        
        # Build progress graph URL with correct arguments
        if len(user_scores) >= 1:
            dates = [s.date_recorded.strftime('%d/%m') for s in user_scores]
            scores = [int((s.score_val / s.total_val) * 100) if s.total_val > 0 else 0 for s in user_scores]
            graph_url = generate_progress_graph(dates, scores)
        else:
            graph_url = None

        # Predictive ML insights
        pred = "Optimizing Paths..."
        if len(user_scores) >= 3:
            from utils.ml_engine import DakashPredictor
            predictor = DakashPredictor()
            history_data = [{'score': int((s.score_val / s.total_val) * 100)} for s in user_scores]
            subj_data = {}
            for s in user_scores:
                subj_data[s.subject_name] = int((s.score_val / s.total_val) * 100)
            pred_score, ai_advice = predictor.predict_boards_score(history_data, subj_data)
            if pred_score is not None:
                pred = f"Predicted Score: {pred_score}% | {ai_advice}"
            else:
                pred = ai_advice
        else:
            pred = "Need at least 3 quiz attempts to unlock prediction matrix. 🔐"

        return render_template('dashboard.html', user=current_user, chart=graph_url, pred=pred)

    @app.route('/chatbot')
    @login_required
    def chatbot():
        return render_template('chatbot.html')

    @app.route('/practice')
    @login_required
    def practice():
        return render_template('practice.html')

    @app.route('/generate_practice', methods=['POST'])
    @login_required
    def generate_practice():
        try:
            data = request.get_json()
            questions = generate_practice_paper(data)
            return jsonify(questions)
        except Exception as e:
            print(f">> [ERROR]: Practice Gen Crash: {e}")
            return jsonify({"error": "Failed to generate practice session"}), 500

    @app.route('/quiz')
    @login_required
    def quiz():
        return render_template('quiz.html')

    @app.route('/generate_quiz', methods=['POST'])
    @login_required
    def generate_quiz():
        try:
            data = request.get_json()
            subject = data.get('subject', 'Science')
            difficulty = data.get('difficulty', 'Medium')
            class_lvl = data.get('class_level', '10')
            exam_track = data.get('exam_track')
            chapter = data.get('chapter')
            
            # Fetch user solved history to prevent repetition
            solved_history = session.get('user_solved_history', [])
            
            print(f">> [SYSTEM]: Gemini Mission Initiated for Class {class_lvl} {subject} (Track: {exam_track}, Chapter: {chapter})...")
            
            from utils.quiz_gen import generate_cbse_quiz
            quiz_data = generate_cbse_quiz(subject, difficulty, class_lvl, exam_track, chapter, solved_history)
            
            if quiz_data:
                # Update solved history in user session
                new_ids = [q['q_id'] for q in quiz_data if 'q_id' in q]
                solved_history.extend(new_ids)
                # Keep history buffer at a reasonable size
                if len(solved_history) > 50:
                    solved_history = solved_history[-50:]
                session['user_solved_history'] = solved_history
                # Cache active quiz structure to server-side JSON file to avoid cookie size bloat
                import json
                cache_dir = os.path.join(app.config['BASE_DIR'], 'instance', 'quiz_cache')
                os.makedirs(cache_dir, exist_ok=True)
                with open(os.path.join(cache_dir, f"active_quiz_{current_user.id}.json"), 'w', encoding='utf-8') as f:
                    json.dump(quiz_data, f)
                
                session['active_quiz_subject'] = subject
                session.modified = True
                return jsonify(quiz_data)
            return jsonify({"error": "AI failed to build mission"}), 500
        except Exception as e:
            print(f">> [ERROR]: Quiz Engine Crash: {e}")
            return jsonify({"error": "Neural Link Failed. Check API!"}), 500

    @app.route('/save_score', methods=['POST'])
    @login_required
    def save_score():
        try:
            data = request.get_json()
            new_score = Score(
                user_id=current_user.id,
                subject_name=data.get('subject'),
                score_val=int(data.get('score')),
                total_val=int(data.get('total')),
                test_type=data.get('test_type', 'QUIZ')
            )
            db.session.add(new_score)
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error"}), 500

    @app.route('/api/submit-simulation', methods=['POST'])
    @login_required
    def submit_simulation():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Empty payload"}), 400
                
            submitted_answers = data.get('answers', {})
            
            # Read active quiz from server-side cache file
            import json
            cache_path = os.path.join(app.config['BASE_DIR'], 'instance', 'quiz_cache', f"active_quiz_{current_user.id}.json")
            
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    active_quiz = json.load(f)
            else:
                return jsonify({"error": "No active quiz session found"}), 400
                
            total_marks = 0
            user_score = 0
            correct_count = 0
            total_questions = len(active_quiz)
            
            for q in active_quiz:
                q_id = q.get('q_id')
                q_marks = q.get('marks', 1)
                total_marks += q_marks
                
                user_ans = submitted_answers.get(q_id)
                correct_ans = q.get('answer')
                
                if user_ans is not None:
                    if user_ans.strip() == correct_ans.strip():
                        user_score += q_marks
                        correct_count += 1
                    else:
                        # Apply competitive negative marking rules if applicable
                        if q_id.startswith('q_jee'):
                            user_score -= 1  # -1 penalty
                        elif q_id.startswith('q_neet'):
                            user_score -= 1  # -1 penalty
                        elif q_id.startswith('q_nda'):
                            if q_marks == 2.5: # Maths
                                user_score -= 0.83
                            else: # GAT
                                user_score -= 1.33
                                
            # Make sure score doesn't fall below 0
            user_score = max(0, round(user_score, 2))
            
            # Save score to Database
            subject = session.get('active_quiz_subject', 'General Science')
            new_score = Score(
                user_id=current_user.id,
                subject_name=subject,
                score_val=int(user_score) if isinstance(user_score, float) and user_score.is_integer() else user_score,
                total_val=total_marks,
                test_type='QUIZ'
            )
            db.session.add(new_score)
            db.session.commit()
            
            # Save detail to server-side cache for Gemini analysis BEFORE clearing active quiz
            last_submit_data = {
                "subject": subject,
                "score": user_score,
                "total": total_marks,
                "correct": correct_count,
                "total_questions": total_questions,
                "test_type": "QUIZ",
                "questions": [
                    {
                        "question": q.get('question'),
                        "options": q.get('options'),
                        "correct_answer": q.get('answer'),
                        "user_answer": submitted_answers.get(q.get('q_id')),
                        "explanation": q.get('explanation')
                    }
                    for q in active_quiz
                ]
            }
            submit_dir = os.path.join(app.config['BASE_DIR'], 'instance', 'submit_cache')
            os.makedirs(submit_dir, exist_ok=True)
            with open(os.path.join(submit_dir, f"last_submit_{current_user.id}.json"), 'w', encoding='utf-8') as f:
                json.dump(last_submit_data, f)
            
            # Clear active quiz from server-side cache
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except Exception:
                    pass
            
            return jsonify({
                "status": "success", 
                "correct": correct_count, 
                "total": total_questions,
                "score": user_score,
                "total_marks": total_marks
            })
            
        except Exception as e:
            print(f">> [ERROR]: Simulation Submit Crash: {e}")
            return jsonify({"error": "Failed to process simulation submission"}), 500

    @app.route('/api/submit-practice', methods=['POST'])
    @login_required
    def submit_practice():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Empty payload"}), 400
                
            subject = data.get('subject')
            score = data.get('score')
            total = data.get('total')
            questions = data.get('questions', [])
            
            # Save score to Database
            new_score = Score(
                user_id=current_user.id,
                subject_name=subject,
                score_val=score,
                total_val=total,
                test_type='PRACTICE'
            )
            db.session.add(new_score)
            db.session.commit()
            
            # Save detail to server-side cache for Gemini analysis
            last_submit_data = {
                "subject": subject,
                "score": score,
                "total": total,
                "correct": score,
                "total_questions": total,
                "test_type": "PRACTICE",
                "questions": [
                    {
                        "question": q.get('question'),
                        "options": q.get('options'),
                        "correct_answer": q.get('answer'),
                        "user_answer": q.get('user_answer'),
                        "explanation": q.get('explanation')
                    }
                    for q in questions
                ]
            }
            import json
            submit_dir = os.path.join(app.config['BASE_DIR'], 'instance', 'submit_cache')
            os.makedirs(submit_dir, exist_ok=True)
            with open(os.path.join(submit_dir, f"last_submit_{current_user.id}.json"), 'w', encoding='utf-8') as f:
                json.dump(last_submit_data, f)
            
            return jsonify({"status": "success"})
        except Exception as e:
            print(f">> [ERROR]: Practice Submit Crash: {e}")
            return jsonify({"error": "Failed to process practice submission"}), 500

    @app.route('/api/get-result-analysis', methods=['GET'])
    @login_required
    def get_result_analysis():
        try:
            # Read last submit data from server-side cache file
            import json
            submit_path = os.path.join(app.config['BASE_DIR'], 'instance', 'submit_cache', f"last_submit_{current_user.id}.json")
            if os.path.exists(submit_path):
                with open(submit_path, 'r', encoding='utf-8') as f:
                    submit_data = json.load(f)
            else:
                submit_data = None
                
            if not submit_data:
                return jsonify({"analysis": "<p>No recent test submission data found for analysis.</p>"})
                
            subject = submit_data.get('subject')
            score = submit_data.get('score')
            total = submit_data.get('total')
            correct = submit_data.get('correct')
            total_questions = submit_data.get('total_questions')
            test_type = submit_data.get('test_type')
            questions = submit_data.get('questions', [])
            
            # Format questions log for prompt
            log_parts = []
            for i, q in enumerate(questions, 1):
                part = (
                    f"Question {i}: {q.get('question')}\n"
                    f"Options: {', '.join(q.get('options', []))}\n"
                    f"Correct Answer: {q.get('correct_answer')}\n"
                    f"Student's Answer: {q.get('user_answer')}\n"
                    f"Explanation: {q.get('explanation')}\n"
                )
                log_parts.append(part)
            questions_log_formatted = "\n---\n".join(log_parts)
            
            prompt = f"""
            You are the 'SAMARTH AI Mentor', an encouraging, super-smart academic guide.
            
            Provide a premium, highly detailed performance report card, diagnostic analysis of weak topics, and study tips for a student who just took a {test_type} on the subject {subject}.
            
            Student Score: {correct} / {total_questions} (Accuracy: {int((correct/total_questions)*100) if total_questions > 0 else 0}%)
            
            Here is the question log:
            {questions_log_formatted}
            
            Based on the questions they got wrong (and the explanations of the correct answers), identify:
            1. Report Card Summary: An encouraging, friendly, and structured summary. Use words like 'Cadet', 'Mission', 'Command Center'.
            2. Diagnostic Breakdown of Weak Topics: List the specific concepts, chapters, or rules where the student made mistakes. Be highly specific (e.g. 'Ohm's Law application', 'Trigonometric identities').
            3. Actionable study tips & resources (specific methods/shortcuts) to convert these weak spots into strong points.
            
            FORMATTING RULES:
            - Output ONLY clean HTML code that can be embedded inside a <div> in the user interface.
            - Use <h3>, <p>, <ul>, <li>, and <strong> tags.
            - Highlight key words using styling or color (e.g., <span style="color: var(--neon-blue);">...</span> or <span style="color: #ff003c;">...</span>).
            - Do NOT include any markdown code blocks (like ```html), <html>, <body>, or <head> tags. Just output the inner HTML content directly.
            - Do NOT use plain text descriptions of HTML. Just output the raw HTML tags and text.
            - Make sure it looks very premium, clean, and fit for a futuristic dark-themed console dashboard.
            """
            
            # Call Gemini
            import google.generativeai as genai
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            if GEMINI_API_KEY:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-flash-lite-latest')
                response = model.generate_content(prompt)
                analysis_text = response.text.strip()
                
                # Strip any triple backticks ```html or ``` that Gemini might wrap the output in
                analysis_text = re.sub(r"^```html\s*", "", analysis_text, flags=re.IGNORECASE)
                analysis_text = re.sub(r"^```\s*", "", analysis_text)
                analysis_text = re.sub(r"\s*```$", "", analysis_text)
                analysis_text = analysis_text.strip()
            else:
                analysis_text = "<p>Gemini API is offline. Performance index analysis skipped.</p>"
                
            return jsonify({"analysis": analysis_text})
        except Exception as e:
            print(f">> [ERROR]: Result Analysis Crash: {e}")
            return jsonify({"error": "Failed to generate report analysis"}), 500

    @app.route('/dashboard/performance')
    @login_required
    def dashboard_performance():
        return redirect(url_for('result'))

    @app.route('/api/chat', methods=['POST'])
    @login_required
    def api_chat():
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({"response": "Signal Lost!"}), 400
            
            reply = get_ai_response(data['message'])
            return jsonify({"response": reply})
        except Exception as e:
            return jsonify({"response": "Neural Link Failed!"}), 500

    # --- 🎯 GOALS/MISSION TRACKER ROUTES ---
    @app.route('/goals')
    @login_required
    def goals():
        active_goals = goal_manager.get_active_missions()
        return render_template('goals.html', goals=active_goals)

    @app.route('/add_goal', methods=['POST'])
    @login_required
    def add_goal():
        title = request.form.get('goal_title')
        if title:
            goal_manager.add_mission(title)
        return redirect(url_for('goals'))

    @app.route('/delete_goal/<int:goal_id>')
    @login_required
    def delete_goal(goal_id):
        goal_manager.update_progress(goal_id)
        return redirect(url_for('goals'))

    # --- 📅 TIMETABLE/SCHEDULER ROUTES ---
    @app.route('/timetable')
    @login_required
    def timetable():
        return render_template('timetable.html')

    @app.route('/generate_timetable', methods=['POST'])
    @login_required
    def generate_timetable():
        try:
            data = request.get_json()
            schedule = generate_ai_timetable(data)
            return jsonify(schedule)
        except Exception as e:
            print(f">> [ERROR]: Timetable Gen Crash: {e}")
            return jsonify([]), 500

    # --- 📜 HISTORY/ARCHIVES ROUTES ---
    @app.route('/history')
    @login_required
    def history():
        user_scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.date_recorded.desc()).all()
        history_records = []
        for s in user_scores:
            history_records.append({
                'is_manual': (s.test_type == 'MANUAL'),
                'test_type': s.test_type or 'MANUAL',
                'subject_name': s.subject_name,
                'date_taken': s.date_recorded,
                'score': s.score_val,
                'total': s.total_val
            })
        return render_template('history.html', history=history_records)

    @app.route('/add_manual_score', methods=['POST'])
    @login_required
    def add_manual_score():
        try:
            subject = request.form.get('subject')
            score = int(request.form.get('score'))
            total = int(request.form.get('total'))
            
            new_score = Score(
                user_id=current_user.id,
                subject_name=subject,
                score_val=score,
                total_val=total,
                test_type='MANUAL'
            )
            db.session.add(new_score)
            db.session.commit()
            flash('Score synced successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to sync score.', 'danger')
        return redirect(url_for('history'))

    # --- 🏆 LEADERBOARD/COMPARE ROUTES ---
    @app.route('/compare')
    @login_required
    def compare():
        users = User.query.all()
        leaderboard = []
        for u in users:
            scores = Score.query.filter_by(user_id=u.id).all()
            if scores:
                avg = sum((s.score_val / s.total_val) * 100 for s in scores) / len(scores)
            else:
                avg = 0.0
            leaderboard.append({
                'username': u.username,
                'avg_score': avg
            })
        leaderboard = sorted(leaderboard, key=lambda x: x['avg_score'], reverse=True)
        return render_template('compare.html', leaderboard=leaderboard)

    # --- 📊 RESULT ROUTE ---
    @app.route('/result')
    @login_required
    def result():
        correct = int(request.args.get('correct', 0))
        total = int(request.args.get('total', 10))
        percent = int((correct / total) * 100) if total > 0 else 0
        
        # Build progress graph URL with correct arguments
        user_scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.date_recorded.asc()).all()
        if len(user_scores) >= 1:
            dates = [s.date_recorded.strftime('%d/%m') for s in user_scores]
            scores = [int((s.score_val / s.total_val) * 100) if s.total_val > 0 else 0 for s in user_scores]
            graph_url = generate_progress_graph(dates, scores)
        else:
            graph_url = None
            
        return render_template('result.html', score_percent=percent, correct_ans=correct, total_ques=total, chart=graph_url)

    @app.route('/api/get-result-solutions', methods=['GET'])
    @login_required
    def get_result_solutions():
        try:
            # Read last submit data from server-side cache file
            import json
            submit_path = os.path.join(app.config['BASE_DIR'], 'instance', 'submit_cache', f"last_submit_{current_user.id}.json")
            if os.path.exists(submit_path):
                with open(submit_path, 'r', encoding='utf-8') as f:
                    submit_data = json.load(f)
                return jsonify({"status": "success", "questions": submit_data.get('questions', [])})
            else:
                return jsonify({"status": "error", "message": "No recent submission found"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/logout')
    def logout():
        logout_user()
        session.clear()
        flash("Cadet Offline. Neural Link Terminated.", "info")
        return redirect(url_for('login'))

    # Initialize Database inside App Context
    with app.app_context():
        try:
            db.create_all()
            print(">> [DATABASE]: Neural Database Synced. System is 100% Divine.")
        except Exception as db_err:
            print(f">> [DATABASE]: Table sync skipped or warning: {db_err}")

    return app

# Ignition
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5002))
    app.run(debug=Config.DEBUG, port=port, host='0.0.0.0')