import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


############Paginations#############
QUESTIONS_PER_PAGE = 10

def pagination (request, sel):
    #Implement pagination, get the arg of page and if it dont exist, then it will default to 1 
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatt = [ questions.format() for questions in sel]
    #instead of getting all the query it will get only the "start to end "
    pag = formatt[start:end]
    return pag

def quizz_pagination (request, sel):
    #Implement pagination, get the arg of page and if it dont exist, then it will default to 1 
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 1
    end = start + 1
    formattt = [ questions.format() for questions in sel]
    #instead of getting all the query it will get only the "start to end "
    pagg = formattt[start:end]
    return pagg


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    #cors = CORS(app, resources={r"/categories": {"origins": "http://localhost:5000"}}
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH,DELETE, OPTIONS')
        return response
    
    
    
    @app.route('/categories', methods=['GET'])
    #@cross_origin()
    def get_categories():
        try:
            cats = Category.query.all()
            format_cats = {cat.id:cat.type for cat in cats}
            return jsonify({
                'success': True,
                'categories' : format_cats,
                'total_categories':len(cats)
                })
        except:
            abort(500)
  
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            sel = Question.query.all()
            paged_que = pagination(request, sel)

            if len(paged_que) == 0:
                abort(404)

            cats = Category.query.all()
            format_cats = {cat.id:cat.type for cat in cats }

            return jsonify({
                'success': True,
                'questions' : paged_que,
                'totalQuestions':len(sel),
                'categories' : format_cats,
                'total_categories':len(cats),
                })
        except:
            abort(404)
   
    @app.route("/questions/<int:que_id>", methods=["DELETE"])
    def delete_question(que_id):
        try:    
            question = Question.query.filter(Question.id == que_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
                    "success": True,
                    "deleted": que_id,
                })
        except:
            abort(422)
    
    @app.route("/questions", methods=["POST"])
    def create_question():

        data_body = request.get_json()
        new_question = data_body.get("question",None)
        new_answer = data_body.get("answer", None)
        new_difficulty = data_body.get("difficulty",None)
        new_category = data_body.get("category",None)
        search_term = data_body.get("searchTerm",None)

        try:

            if search_term:

                sel = Question.query.filter(Question.question.like("%"+search_term+"%"))
                count = len(sel.all())
                paged_que = pagination(request, sel)
                return jsonify({
                    'success': True,
                    'totalQuestions' : count,
                    'questions' : paged_que
                })
            else:
                new_questions = Question(
                    question = new_question,
                    answer = new_answer,
                    category = new_category,
                    difficulty = new_difficulty
                )
                new_questions.insert()
                sel = Question.query.order_by(Question.id).all()
                paged_que = pagination(request, sel)
                return jsonify({
                    'success': True,
                    'created Question': new_questions.id,
                    'data' : paged_que,
                    'total_questions':len(sel)
                })
        except:
            abort(422)

   
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_by_id(category_id):
        try:
            data=[]
            category = Question.query.join(Category, Question.category == category_id).all()
            #category = db.session.query(Question).join(Category).filter(Question.category == category_id).all()
            if category == None:
                abort(404)
            cur =  Category.query.get(category_id)
            current = cur.type
            for question in category:
                info = {
                
                    "id":question.id,
                    "question" : question.question,
                    "answer" : question.answer,
                    "category" : question.category,
                    "difficulty" : question.difficulty
                }
                data.append(info)
            return jsonify({
                'success': True,
                'questions' : data,
                'totalQuestions' : len(category),
                'currentCatergory': current
            })
        except:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def get_quizz():
        try:

            data=[]
            data_body =  request.get_json()
            previous_questions = data_body.get("previous_questions", [])
            quiz_category = data_body.get("quiz_category", "")
            cat = quiz_category['id']

            if cat == 0:
                sel = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                sel = Question.query.filter(Question.category == cat).filter(Question.id.notin_(previous_questions)).all()

            que = [questions.format() for questions in sel]   
            random_questions = random.randint(0, len(que) )
            data = que[random_questions]
            return jsonify({
                "success" : True,
                "question":data,
            })
        except:
            abort(400)    

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Requested page Not found"
            }), 404

    @app.errorhandler(422)
    def unprocessed_request(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Server can't process your request"
            }), 422

    @app.errorhandler(400)
    def invalid_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "Bad Request"
            }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "internal server error"
            }),500

    return app

