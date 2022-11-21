import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format('postgres', '1234','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

   
   
    #############GET_QUESTION#########
    def test_get_question(self):
        response = self.client().get('/questions')
        load_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200 )
        self.assertEqual(load_data['success'], True )
        self.assertTrue(len(load_data['questions']))
        self.assertTrue(load_data['totalQuestions'])
        self.assertTrue(len(load_data['categories']))
        self.assertTrue(load_data['total_categories'])

    def test_404_get_question(self):
        response = self.client().get('/questions?page=200')
        load_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(load_data['success'], False )
        self.assertEqual(load_data['message'], 'Requested page Not found')

    
    ######QUESTION_SEARCH TEST###########
    def test_search_question(self):
       response = self.client().post('/questions', json = {
           "searchTerm" : "What"
       })
       load_data = json.loads(response.data)

       self.assertEqual(response.status_code, 200 )
       self.assertEqual(load_data['success'], True )
       self.assertTrue(len(load_data['questions']))
       self.assertTrue(load_data['totalQuestions'])

    def test_search_question_withno_result(self):

        response = self.client().post('/questions', 
        json = {
            "searchTerm" : "sububbu"
        })

        load_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200 )
        self.assertEqual(load_data['success'], True )
        self.assertEqual(len(load_data['questions']), 0)
        self.assertEqual(load_data['totalQuestions'], 0)

    
    #######CREATING NEW QUESTION TEST###############
    def test_create_question(self):
        response = self.client().post('/questions', json ={

            "question":"what is the most streaming song ?",
            "answer":"Thriller MJ", 
            "difficully":"4", 
            "category":"3"
        })
        load_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200 )
        self.assertEqual(load_data['success'], True )
        self.assertTrue(len(load_data['data']))
        self.assertTrue(load_data['created Question'])

    def test_422_create_question(self):
        response = self.client().post('/questions', json ={
            "question":"what is the most streaming song ?",
            "answer":"Thriller MJ", 
            "difficully":"High", 
            "category":"science"


        })
        load_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(load_data['success'], False )
        self.assertEqual(load_data['message'], "Server can't process your request")

    
    ######DELETE QUESTION TEST##############
    def test_delete_question(self):
        response = self.client().delete('/questions/35')
        load_data = json.loads(response.data)
        question = Question.query.filter(Question.id == 35).one_or_none()
        self.assertEqual(response.status_code, 200 )
        self.assertEqual(load_data['success'], True )
        self.assertTrue(load_data['deleted'], 35)
        self.assertEqual(question, None )
    def test_404_delete_question(self):
        response = self.client().delete('/questions/2000')
        load_data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(load_data['success'], False )
        self.assertEqual(load_data['message'], "Server can't process your request")
    
    
    def test_get_question_by_category_id(self):
        response = self.client().get('/categories/2/questions')
        load_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200 )
        self.assertEqual(load_data['success'], True )
        self.assertTrue(len(load_data['questions']))
        self.assertTrue(load_data['totalQuestions'])

    def test_404_question_by_category_id(self):
        response = self.client().get('/categories/1000/questions')
        load_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(load_data['success'], False )
        self.assertEqual(load_data['message'], 'Requested page Not found')

    #done
    #########GET QUIZ TEST###############
    def test_get_quizz(self):
        response = self.client().post('/quizzes', json = {
            "previous_questions":[12,16],
            "quiz_category": {
                "type" : "Art",
                "id":"2"
            }
        })
        load_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_data['success'], True )
        self.assertTrue(len(load_data['question']))
      
    def test_400_get_quizz(self):
        response = self.client().post('/quizzes', json = {
            "previous_questions":[],
            "quiz_category": {
                "type" : "Biology",
                "id":"40"
            }
        })
        load_data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(load_data['success'], False )
        self.assertEqual(load_data['message'], "Bad Request")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()