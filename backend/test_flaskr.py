import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # Hardcode to add new question
        self.newQuestion = {
            "question": "new Question",
            "category": 1,
            "difficulty": 12,
            "answer": "Correct answer"
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """ Get questions """

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['message'], 'success')
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    """ Add new Question test """

    def test_post_new_questions(self):
        res = self.client().post('/questions', json=self.newQuestion)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['Success'], True)
        self.assertEqual(data['message'], 'Question added')

    """ Test delete question when success and failure """

    def test_delete_questions(self):
        res = self.client().delete('/questions/10')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 10).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['message'], 'Success')
        self.assertEqual(question, None)

    def test_404_delete_questions(self):
        res = self.client().delete('/questions/100')
        self.assertEqual(res.status_code, 404)

    # Categories testing area
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
