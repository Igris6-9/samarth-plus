import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import unittest
import json
from app import create_app
from models import db, User, Score, Goal, Timetable

class SamarthTestCases(unittest.TestCase):
    def setUp(self):
        # Configure app for testing using in-memory database
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Initialize test database inside context
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def register_user(self, username, email, password):
        return self.client.post('/register', data={
            'username': username,
            'email': email,
            'password': password
        }, follow_redirects=True)

    def login_user(self, email, password):
        return self.client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def test_registration_and_login(self):
        # 1. Test register
        response = self.register_user('cadet1', 'cadet1@samarth.plus', 'securepassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mission Ready!', response.data)

        # 2. Test duplicate register
        response = self.register_user('cadet2', 'cadet1@samarth.plus', 'otherpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email already registered!', response.data)

        # 3. Test login correct
        response = self.login_user('cadet1@samarth.plus', 'securepassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'COMMAND', response.data)
        self.assertIn(b'CENTER', response.data)

        # 4. Test login incorrect
        response = self.login_user('cadet1@samarth.plus', 'wrongpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid Credentials', response.data)

    def test_authenticated_routes(self):
        # Register and login to establish session
        self.register_user('cadet1', 'cadet1@samarth.plus', 'securepassword')
        self.login_user('cadet1@samarth.plus', 'securepassword')

        # 1. Dashboard
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'cadet1', response.data)

        # 2. Chatbot view
        response = self.client.get('/chatbot')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SAMARTH', response.data)
        self.assertIn(b'MENTOR', response.data)

        # 3. Practice view
        response = self.client.get('/practice')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'WAR', response.data)
        self.assertIn(b'ZONE', response.data)

        # 4. Quiz view
        response = self.client.get('/quiz')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MOCK', response.data)
        self.assertIn(b'EXAM', response.data)

        # 5. Timetable view
        response = self.client.get('/timetable')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MISSION SCHEDULER', response.data)

        # 6. Goals view
        response = self.client.get('/goals')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MISSION', response.data)
        self.assertIn(b'OBJECTIVES', response.data)

        # 7. History view
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ACADEMIC', response.data)
        self.assertIn(b'LEGACY', response.data)

        # 8. Compare view
        response = self.client.get('/compare')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'HALL OF', response.data)
        self.assertIn(b'FAME', response.data)

        # 9. Result view
        response = self.client.get('/result?correct=8&total=10')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MISSION', response.data)
        self.assertIn(b'COMPLETE', response.data)

    def test_goals_functionality(self):
        self.register_user('cadet1', 'cadet1@samarth.plus', 'securepassword')
        self.login_user('cadet1@samarth.plus', 'securepassword')

        # Add goal
        response = self.client.post('/add_goal', data={'goal_title': 'Complete Physics Chapter 1'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Complete Physics Chapter 1', response.data)

        # Mark goal accomplished
        goal = Goal.query.first()
        self.assertIsNotNone(goal)
        self.assertEqual(goal.status, 'ACTIVE')

        response = self.client.get(f'/delete_goal/{goal.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Complete Physics Chapter 1', response.data)  # Since goals page only shows active ones

        # Check status is accomplished in DB
        db_goal = db.session.get(Goal, goal.id)
        self.assertEqual(db_goal.status, 'ACCOMPLISHED')

    def test_timetable_generation(self):
        self.register_user('cadet1', 'cadet1@samarth.plus', 'securepassword')
        self.login_user('cadet1@samarth.plus', 'securepassword')

        payload = {
            'wake_up': '06:00',
            'school_start': '08:00',
            'school_end': '14:00',
            'has_coaching': 'No',
            'special_task': 'Maths practice'
        }
        response = self.client.post('/generate_timetable', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        schedule = json.loads(response.data)
        self.assertTrue(len(schedule) > 0)
        self.assertIn('task', schedule[0])

    def test_quiz_generation(self):
        self.register_user('cadet1', 'cadet1@samarth.plus', 'securepassword')
        self.login_user('cadet1@samarth.plus', 'securepassword')

        payload = {
            'subject': 'Physics',
            'difficulty': 'Moderate',
            'class_level': '10'
        }
        response = self.client.post('/generate_quiz', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        quiz_data = json.loads(response.data)
        self.assertTrue(len(quiz_data) > 0)
        self.assertIn('question', quiz_data[0])

    def test_practice_generation(self):
        self.register_user('cadet1', 'cadet1@samarth.plus', 'securepassword')
        self.login_user('cadet1@samarth.plus', 'securepassword')

        payload = {
            'subject': 'Chemistry',
            'chapter': 'Acids and Bases',
            'difficulty': 'Easy',
            'class_level': '10'
        }
        response = self.client.post('/generate_practice', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        practice_data = json.loads(response.data)
        self.assertTrue(len(practice_data) > 0)
        self.assertIn('question', practice_data[0])

    def test_save_score_and_archives(self):
        self.register_user('cadet1', 'cadet1@samarth.plus', 'securepassword')
        self.login_user('cadet1@samarth.plus', 'securepassword')

        # Save score
        payload = {
            'subject': 'Physics Mock Quiz',
            'score': 8,
            'total': 10,
            'test_type': 'QUIZ'
        }
        response = self.client.post('/save_score', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Check archives/history page
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Physics Mock Quiz', response.data)
        self.assertIn(b'8', response.data)
        self.assertIn(b'10', response.data)

        # Add manual score
        response = self.client.post('/add_manual_score', data={
            'subject': 'Chemistry Board Exam',
            'score': 90,
            'total': 100
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Chemistry Board Exam', response.data)

    def test_chatbot_api(self):
        self.register_user('cadet1', 'cadet1@samarth.plus', 'securepassword')
        self.login_user('cadet1@samarth.plus', 'securepassword')

        payload = {'message': 'Hello AI Mentor'}
        response = self.client.post('/api/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertTrue(len(data['response']) > 0)

    def test_logout_redirection(self):
        self.register_user('cadet1', 'cadet1@samarth.plus', 'securepassword')
        self.login_user('cadet1@samarth.plus', 'securepassword')

        # Call logout and verify it redirects to login page '/login'
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        # Check redirect target is /login
        self.assertTrue(response.location.endswith('/login'))
        
        # Follow the redirect and verify we are back on login page
        follow_response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(follow_response.status_code, 200)
        self.assertIn(b'CADET LOGIN', follow_response.data) # from login.html

if __name__ == '__main__':
    unittest.main()
